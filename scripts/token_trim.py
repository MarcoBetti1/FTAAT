"""
scripts/token_trim.py
─────────────────────
Ensure a single-token vocabulary stays single when surrounded or
concatenated with a separator (*e.g.*, '|').
"""

from __future__ import annotations
import json, itertools
from collections import Counter
from typing import Callable, Sequence, List

DEFAULT_SEP = "|"


# ───────────────────────────────────────────────────
#  helpers
# ───────────────────────────────────────────────────
def _single_tokens(path: str, encode: Callable[[str], Sequence[int]]) -> List[str]:
    with open(path) as f:
        vocab = json.load(f)
    return [t for t in vocab if len(encode(t)) == 1]


def _seq_expected_len(seq_len: int, sep_len: int) -> int:
    return seq_len + (seq_len + 1) * sep_len


def _mismatch_stats(
    tokens: List[str],
    encode: Callable[[str], Sequence[int]],
    separator: str,
    max_sequence_length: int,
) -> Counter:
    sep_len = len(encode(separator))
    stats = Counter()
    for L in range(2, max_sequence_length + 1):
        for combo in itertools.combinations(tokens, L):
            test = separator + separator.join(combo) + separator
            if len(encode(test)) != _seq_expected_len(L, sep_len):
                for t in combo:
                    stats[t] += 1
    return stats


# ───────────────────────────────────────────────────
#  public API
# ───────────────────────────────────────────────────
def trim_token_set(
    json_path: str,
    encode: Callable[[str], Sequence[int]],
    *,
    separator: str = DEFAULT_SEP,
    single_surround: bool = True,
    max_sequence_length: int = 2,
    save_as: str | None = None,
) -> str:
    """
    Remove tokens that break when written as '|token|' or
    '|t1|t2|…|tL|' (L ≤ `max_sequence_length`).
    """
    save_as = save_as or json_path.replace(".json", "_clean.json")
    vocab = _single_tokens(json_path, encode)

    # 1. '|token|' rule
    if single_surround:
        sep_len = len(encode(separator))
        vocab = [
            t for t in vocab
            if len(encode(f"{separator}{t}{separator}")) == 1 + 2 * sep_len
        ]

    # 2. sequence rule
    if max_sequence_length > 1:
        stats = _mismatch_stats(vocab, encode, separator, max_sequence_length)
        if stats:
            # heavy offenders first
            worst = {t for t, c in stats.items() if c > min(stats.values())}
            vocab = [t for t in vocab if t not in worst]
            # purge any remaining offenders
            stats2 = _mismatch_stats(vocab, encode, separator, max_sequence_length)
            vocab  = [t for t in vocab if t not in stats2]

    with open(save_as, "w") as f:
        json.dump(sorted(vocab), f)
    return save_as
