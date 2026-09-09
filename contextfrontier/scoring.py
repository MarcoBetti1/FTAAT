"""Prespecified scoring; never divide by only the answers a model chose to return."""
import math


VERSION = "score-v1.1"


def grade(text, expected, *, symbols_per_answer=None):
    if not expected:
        raise ValueError("Expected answers cannot be empty")
    lines = text.strip().splitlines() if text.strip() else []
    lines = [line.strip() for line in lines]
    matched = sum(i < len(lines) and lines[i] == answer for i, answer in enumerate(expected))
    total_symbols = sum(len(line.split("|")) for line in expected)
    matched_symbols = 0
    for i, answer in enumerate(expected):
        actual = lines[i].split("|") if i < len(lines) else []
        matched_symbols += sum(j < len(actual) and actual[j] == sym
                               for j, sym in enumerate(answer.split("|")))
    # Secondary shape diagnostic: line and pipe-delimited symbol counts only.
    # It is not a full lexical grammar validator or a semantic correctness score.
    shape_ok = len(lines) == len(expected) and all(
        (a == "UNKNOWN" or len(a.split("|")) == (symbols_per_answer or len(b.split("|"))))
        for a, b in zip(lines, expected))
    return dict(exact=lines == expected, sequence_accuracy=matched / len(expected),
                symbol_accuracy=matched_symbols / total_symbols, format_ok=shape_ok,
                expected_lines=len(expected), received_lines=len(lines), matched_lines=matched)


def wilson(successes, n, z=1.959963984540054):
    if n == 0:
        return None
    if not 0 <= successes <= n:
        raise ValueError("Invalid success count")
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [max(0., center - radius), min(1., center + radius)]
