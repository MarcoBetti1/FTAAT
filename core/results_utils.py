from config import RESULTS_ROOT
from pathlib import Path

def json_pattern(n: int, k: int) -> str:
    return f"*_{n}N_{k}K_*.json"

def result_folder(prompt_id: str, provider: str) -> Path:
    return RESULTS_ROOT / f"prompt_{prompt_id}" / provider

def file_exists(prompt_id: str, provider: str, n: int, k: int) -> bool:
    folder = result_folder(prompt_id, provider)
    return folder.exists() and any(folder.glob(json_pattern(n, k)))

def latest_json(prompt_id: str, provider: str, n: int, k: int):
    folder = result_folder(prompt_id, provider)
    matches = list(folder.glob(json_pattern(n, k)))
    return max(matches, key=lambda p: p.stat().st_mtime) if matches else None

# ── core/results_utils.py ───────────────────────────────────────────────
import re, json
from pathlib import Path
from typing import Iterator, Tuple

RESULT_RE = re.compile(r"(?P<N>\d+)N_(?P<K>\d+)K")

def iter_saved_trials(prompt_id: str, provider_id: str) -> Iterator[Tuple[int,int,dict]]:
    """
    Yield (N, K, result_json_dict) for every saved run that matches the prompt
    & provider. Assumes the structure:
      RESULTS_ROOT/prompt_<prompt_id>/<provider_id>/*.json
    """
    from pathlib import Path
    import json, re

    print(f"[DEBUG] prompt_id = [{prompt_id}] with length {len(prompt_id)}")
    root = Path(RESULTS_ROOT) / f"prompt_{prompt_id}" / provider_id

    print(f"[DEBUG] root: {root} | Exists: {root.exists()} | Is dir: {root.is_dir()}")
    if not root.exists():
        print(f"[INFO] Folder not found: {root}")
        return

    for p in root.glob("*.json"):
        m = RESULT_RE.search(p.name)  # use .search instead of .match
        if not m:
            print(f"[SKIP] {p.name} does not match pattern")
            continue
        try:
            data = json.loads(p.read_text())
            yield int(m["N"]), int(m["K"]), data
        except Exception as e:
            print(f"[ERROR] Failed to read/parse {p.name}: {e}")




def saved_metrics(prompt_id: str, provider_id: str
                 ) -> dict[tuple[int,int], tuple[float,float]]:
    """
    Return {(N,K): (flaw_ratio, avg_accuracy)} for *all* saved runs.
    """
    out = {}
    for N, K, data in iter_saved_trials(prompt_id, provider_id):
        try:
            trials = data["trials"]
            flaw   = sum(t["major_format_flaw"] for t in trials) / len(trials)
            acc    = sum(t["sequence_accuracy"]  for t in trials) / len(trials)
            out[(N, K)] = (flaw, acc)
        except Exception as e:
            print(f"[ERROR] Malformed data in (N={N}, K={K}): {e}")
    return out