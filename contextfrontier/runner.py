"""Serial, resumable runs with durable conservative reservations before dispatch."""
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import fcntl
import json
import math
from pathlib import Path
import platform
import random
import subprocess

from . import __version__
from .providers import APIProvider, ProviderError, usage_counts
from .scoring import grade
from .tasks import digest, make_suite


def now():
    return datetime.now(timezone.utc).isoformat()


def append(path, row):
    import os
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_rows(path):
    if not path.exists():
        return []
    # Fail closed on an interrupted/corrupt ledger; never silently forget spend.
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def money(tokens, per_million):
    return Decimal(tokens) * Decimal(str(per_million)) / Decimal(1000000)


def validate(config):
    if config.get("comparison") != "same_text":
        raise ValueError("v1 supports same_text only; never mislabel it equal-token")
    if not config.get("models"):
        raise ValueError("At least one model is required")
    ids = []
    for model in config["models"]:
        if model["provider"] not in ("openai", "anthropic"):
            raise ValueError("Unsupported provider")
        ids.append((model["provider"], model["model"]))
        for field in ("max_output_tokens", "context_window"):
            if type(model[field]) is not int or model[field] < 1:
                raise ValueError(f"Invalid {field}")
        for field in ("input_usd_per_million", "output_usd_per_million"):
            value = model[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"Invalid {field}")
        if not model.get("pricing_source") or not model.get("pricing_checked"):
            raise ValueError("Dated pricing source required")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate models; use a separate run for another setting")
    return make_suite(config["suite"])


def run(config, directory, budget_usd, *, live=False, provider_factory=APIProvider):
    budget = Decimal(str(budget_usd))
    if not budget.is_finite() or budget <= 0:
        raise ValueError("Budget must be a positive finite amount")
    cases = validate(config)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _run_locked(config, cases, directory, budget, live, provider_factory)


def _run_locked(config, cases, directory, budget, live, provider_factory):
    manifest_path = directory / "manifest.json"
    identity = digest({"config": config, "case_ids": [c.id for c in cases], "live": live,
                       "runner_version": __version__, "source_hash": digest({p.name: p.read_text() for p in sorted(Path(__file__).parent.glob("*.py"))})})
    if manifest_path.exists():
        if json.loads(manifest_path.read_text())["identity"] != identity:
            raise ValueError("Run configuration/code/cases changed; use a new output directory")
    else:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
        manifest = dict(identity=identity, created=now(), live=live, config=config,
                        code_version=__version__, git_revision=revision, git_dirty=bool(dirty),
                        python=platform.python_version(), cases=len(cases))
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        (directory / "cases.jsonl").write_text("".join(json.dumps(c.to_dict()) + "\n" for c in cases))
    if not live:
        result = dict(status="dry_run", cases=len(cases), requests=len(cases) * len(config["models"]),
                      input_tokens=None, cost_usd=None,
                      note="No API calls. Token counts and costs require provider preflight; no model results.")
        (directory / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    path = directory / "events.jsonl"
    rows = read_rows(path)
    reserved = {r["request_key"]: Decimal(r["reserve_usd"]) for r in rows if r["event"] == "reserved"}
    settled = {r["request_key"]: Decimal(r["cost_upper_usd"]) for r in rows if r["event"] == "result"}
    terminal = {r["request_key"] for r in rows if r["event"] in ("result", "error", "skipped")}
    counts = {r["request_key"]: r["count"] for r in rows if r["event"] == "count"}
    uncertain = set(reserved) - set(settled)
    if uncertain:
        # Never automatically resend requests with unknown outcomes or uncertain billing.
        return dict(status="uncertain_billing", requests=sorted(uncertain),
                    note="Review provider billing and start a separate run; no automatic retry.")
    spent = sum(settled.values(), Decimal(0))
    jobs = [(case, spec) for case in cases for spec in config["models"]]
    random.Random(config.get("order_seed", 20260909)).shuffle(jobs)
    clients = {}
    try:
        for case, spec in jobs:
            key = digest([case.id, spec])
            if key in terminal:
                continue
            provider_key = (spec["provider"], spec["model"])
            if provider_key not in clients:
                clients[provider_key] = provider_factory(spec)
            provider = clients[provider_key]
            meta = dict(request_key=key, case_id=case.id, provider=spec["provider"], model=spec["model"])
            if key not in counts:
                count = provider.count(case)
                counts[key] = count
                append(path, dict(event="count", at=now(), count=count, **meta))
            count = counts[key]
            inp = count["input_tokens"]
            # Anthropic documents preflight as an estimate. Reserve a margin; usage is authoritative.
            input_reserve = math.ceil(inp * 1.05) + 32
            cap = spec["max_output_tokens"]
            if input_reserve > spec.get("max_input_tokens", spec["context_window"]) or input_reserve + cap > spec["context_window"]:
                append(path, dict(event="skipped", at=now(), reason="context_limit", **meta))
                continue
            if input_reserve > spec.get("price_input_limit", spec["context_window"]):
                append(path, dict(event="skipped", at=now(), reason="unverified_long_context_price", **meta))
                continue
            # For ASCII-only expected answers, UTF-8 bytes are a conservative visible-token bound.
            answer_bytes = len("\n".join(case.expected).encode("utf-8"))
            if cap < answer_bytes + 64:
                append(path, dict(event="skipped", at=now(), reason="output_cap_too_small", **meta))
                continue
            reserve = money(input_reserve, spec["input_usd_per_million"]) * Decimal("1.25") + money(cap, spec["output_usd_per_million"])
            if spent + reserve > budget:
                return dict(status="budget_stop", spent_upper_usd=str(spent), budget_usd=str(budget))
            append(path, dict(event="reserved", at=now(), reserve_usd=str(reserve), **meta))
            try:
                reply = provider.generate(case)
                actual_in, actual_out = usage_counts(spec["provider"], reply.usage)
                # Conservative ceiling: all input at 1.25x ordinary rate covers short cache writes; cache reads cost less.
                actual_cost = money(actual_in, spec["input_usd_per_million"]) * Decimal("1.25") + money(actual_out, spec["output_usd_per_million"])
                scored = grade(reply.text, case.expected) if reply.status == "completed" else None
                append(path, dict(event="result", at=now(), reply=asdict(reply), grade=scored,
                                  actual_input_tokens=actual_in, actual_output_tokens=actual_out,
                                  count_delta=actual_in-inp, cost_upper_usd=str(actual_cost), **meta))
                spent += actual_cost
                if actual_cost > reserve:
                    return dict(status="reservation_exceeded", spent_upper_usd=str(spent),
                                note="Stopped: observed usage exceeded conservative reservation.")
            except (ProviderError, ValueError, KeyError) as e:
                append(path, dict(event="error", at=now(), error_type=type(e).__name__, **meta))
                return dict(status="uncertain_billing", request_key=key,
                            note="Stopped without retry; reserved cost retained. Check provider billing.")
    finally:
        for client in clients.values():
            client.close()
    return dict(status="completed", spent_upper_usd=str(spent), budget_usd=str(budget))
