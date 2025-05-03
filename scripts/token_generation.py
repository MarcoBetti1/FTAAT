"""
scripts/token_generation.py
──────────────────────────
Utilities to create *single-token* vocabularies for OpenAI-style (BPE)
and DeepSeek (SentencePiece) tokenizers.
"""

from __future__ import annotations
import itertools, random, re, json
from typing import Callable, Set, List

# ───────────────────────────────────────────────────
#  Generic OpenAI-style generator
# ───────────────────────────────────────────────────
def generate_alpha_tokens(
    N: int,
    *,
    encode: Callable[[str], List[int]],
    decode_single: Callable[[int], str],
    alphabet: str = "abcdefghijklmnopqrstuvwxyz",
    min_len: int = 2,
    max_len: int = 10,
) -> Set[str]:
    """Return *N* lowercase strings, each exactly **one** token."""
    assert 1 <= min_len <= max_len

    tokens: Set[str] = set()

    # deterministic sweep
    for length in range(min_len, max_len + 1):
        for chars in itertools.product(alphabet, repeat=length):
            s = "".join(chars)
            if len(encode(s)) == 1 and decode_single(encode(s)[0]) == s:
                tokens.add(s)
                if len(tokens) >= N:
                    return tokens

    # random top-up
    rng = random.Random(42)
    while len(tokens) < N:
        length = rng.randint(min_len, max_len + 3)
        s = "".join(rng.choice(alphabet) for _ in range(length))
        if len(encode(s)) == 1 and decode_single(encode(s)[0]) == s:
            tokens.add(s)

    return tokens


# ───────────────────────────────────────────────────
#  DeepSeek / SentencePiece shortcut
# ───────────────────────────────────────────────────
def alpha_tokens_from_vocab(
    tokenizer,
    N: int,
    *,
    alphabet: str = "abcdefghijklmnopqrstuvwxyz",
    min_len: int = 2,
    max_len: int = 10,
) -> Set[str]:
    """
    Pull *N* suitable tokens directly from a SentencePiece vocabulary.
    """
    pattern = re.compile(f"^[{alphabet}]+$")
    out: list[str] = []

    for tok in tokenizer.get_vocab().keys():
        core = tok.lstrip("▁")
        if (
            min_len <= len(core) <= max_len
            and pattern.fullmatch(core)
            and len(tokenizer.encode(core, add_special_tokens=False)) == 1
        ):
            out.append(core)
            if len(out) >= N:
                return set(out)

    raise ValueError(f"Only {len(out)} tokens found (<{N}).")


# ───────────────────────────────────────────────────
#  Persistence helper
# ───────────────────────────────────────────────────
def save_tokens(tokens: Set[str], path: str) -> None:
    with open(path, "w") as f:
        json.dump(sorted(tokens), f)
