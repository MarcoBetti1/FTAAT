import json, importlib
from datetime import datetime
from pathlib import Path
from time import perf_counter
import os
import uuid
import time

from .build_prompt           import build_prompt_for_all_keys
from .helpers.eval           import evaluate_token_sequences
from .helpers.token_utils    import build_single_token_vocab
from .helpers.fact_gen       import generate_facts_k_tokens

def staircase_schedule(n0: int, k0: int,
                       n_max: int, k_max: int,
                       factor: int = 2):
    """Yield (N,K): (n0,k0) → (2n0,2k0) → ... until bounds exceeded."""
    if n0 < 1 or k0 < 1 or factor <= 1:
        raise ValueError("Positive starts and factor > 1 required")
    n, k = n0, k0
    while n <= n_max and k <= k_max:
        yield n, k
        n *= factor
        k *= factor

def grade_response(response_text, question_keys_in_order, key_value_dict, *, tokenizer):
    from contextfrontier.scoring import grade
    correct_seqs = [key_value_dict[key] for key in question_keys_in_order]
    result = grade(response_text, correct_seqs)
    # Count the complete strings, including separators/newlines; never sum isolated pieces.
    expected_tokens = tokenizer("\n".join(correct_seqs))
    response_tokens = tokenizer(response_text)
    return ((result["sequence_accuracy"], result["symbol_accuracy"]),
            not result["format_ok"], expected_tokens, response_tokens)


def run_experiments(
    provider_module: str,
    facts_list_sizes=[3, 6],
    token_sizes=[2, 3],
    trials=1,
    output_root="results",
    prompt_id="default_prompt",
    verbose=True,
    adaptive=False,
    early_abort=False,
    timeout_sec=60,
    max_tok_mult=2,
    batch_size=20
):
    raise RuntimeError(
        "The historical paid runner is retired after the 2026 audit. "
        "Use python -m contextfrontier run experiments/pilot.json --output results/pilot "
        "--budget 5 --live. Historical notebooks/data remain readable."
    )
