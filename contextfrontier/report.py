"""Auditable descriptive reports. Confidence intervals use trials, never answer tokens."""
from collections import defaultdict
import json
from pathlib import Path

from .runner import read_rows
from .scoring import wilson, grade, VERSION


def report(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    cases = {c["id"]: c for c in read_rows(directory / "cases.jsonl")}
    rows = read_rows(directory / "events.jsonl")
    groups = defaultdict(list)
    for row in rows:
        if row["event"] not in ("result", "skipped", "error"):
            continue
        c = cases[row["case_id"]]
        if row["event"] == "result" and row["reply"]["status"] == "completed":
            row["grade"] = grade(row["reply"]["text"], c["expected"], symbols_per_answer=c["k"])
        key = (row["provider"], row["model"], c["task"], c["n"], c["k"], c["depth"], c["absent"])
        groups[key].append(row)
    output = []
    for key, trials in sorted(groups.items()):
        successful = [r for r in trials if r["event"] == "result" and r["grade"] is not None]
        exact = sum(r["grade"]["exact"] for r in successful)
        n = len(successful)
        failures = len(trials) - n
        entry = dict(zip(("provider", "model", "task", "n_records", "k_symbols", "depth", "absent"), key))
        entry.update(completed=n, other_outcomes=failures, exact_successes=exact,
                     exact_rate=exact / n if n else None, wilson95=wilson(exact, n),
                     mean_sequence_accuracy=sum(r["grade"]["sequence_accuracy"] for r in successful)/n if n else None,
                     format_failures=sum(not r["grade"]["format_ok"] for r in successful),
                     input_token_range=[min(r["actual_input_tokens"] for r in successful),
                                        max(r["actual_input_tokens"] for r in successful)] if n else None)
        output.append(entry)
    reserved = {r["request_key"]: float(r["reserve_usd"]) for r in rows if r["event"] == "reserved"}
    settled = {r["request_key"]: float(r["cost_upper_usd"]) for r in rows if r["event"] == "result"}
    pending = set(reserved) - set(settled)
    data = dict(scoring_version=VERSION, live=manifest["live"], groups=output, case_count=len(cases),
                terminal_requests=sum(len(x) for x in groups.values()),
                unsettled_requests=len(pending), reserved_unsettled_usd=sum(reserved[k] for k in pending),
                settled_cost_upper_usd=sum(settled.values()),
                inference="Descriptive per-cell trial intervals; no universal memory limit or significance claim.")
    (directory / "report.json").write_text(json.dumps(data, indent=2) + "\n")
    text = ["# ContextFrontier experiment report", "",
            "LIVE API DATA" if manifest["live"] else "DRY RUN — NO MODEL RESULTS", "",
            f"Cases prepared: {len(cases)}. Terminal requests: {data['terminal_requests']}.",
            f"Unsettled requests: {len(pending)}. Settled cost upper estimate: ${sum(settled.values()):.6f}.", "",
            "Identical text is shared across models; token counts are model-specific. K counts symbols, not tokenizer units.",
            "API models are tested; this is not a test of the ChatGPT or Claude web apps.", "",
            "| Model | Game | N | K | Depth | Absent | Completed | Exact | 95% interval | Other outcomes | Input tokens |",
            "|---|---|---:|---:|---:|---|---:|---:|---|---:|---|"]
    for g in output:
        ci = g["wilson95"]
        interval = f"{ci[0]:.1%}–{ci[1]:.1%}" if ci else "—"
        rate = f"{g['exact_rate']:.1%}" if ci else "—"
        text.append(f"| {g['model']} | {g['task']} | {g['n_records']} | {g['k_symbols']} | {g['depth']} | {g['absent']} | {g['completed']} | {rate} | {interval} | {g['other_outcomes']} | {g['input_token_range']} |")
    text += ["", "Intervals describe exact trial success within each cell across seeds. Multiple answers in one recall trial are not independent samples.",
             "Refusals, incomplete output, transport failures, and skipped requests are shown separately and never silently scored as memory failures.",
             "A small exploratory sample cannot establish a reliable context frontier. Confirm interesting effects with fresh seeds and matched settings.",
             "Adaptive stopping and many comparisons require caution; these are descriptive intervals, not a corrected significance test.", ""]
    (directory / "report.md").write_text("\n".join(text))
    return data
