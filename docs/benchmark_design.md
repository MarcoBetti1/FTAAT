> **Historical documentation:** the paid notebook runner is retired. See [current methodology](methodology.md) and [repository README](../ReadME.md) for the supported workflow and corrected token/scoring claims.

# Benchmark design

This document explains how the Fixed Token Abstract Attention Test (FTAAT) frames abstract key–value memorisation as a controllable benchmarking problem for large language models.

## Task definition

Each trial presents an LLM with a list of synthetic facts of the form `A|B|C => X|Y|Z` where both the key (`A|B|C`) and the value (`X|Y|Z`) are guaranteed to be composed of single tokenizer units. The model is then asked to answer all keys in a shuffled order, effectively turning the task into an associative recall challenge.

Two independent variables control difficulty:

- **Number of facts ($N$)** — how many unique associations must be remembered.
- **Key (and value) length ($K$)** — how many single-token symbols make up each key and value.

By sweeping $N$ and $K$, you can trace the failure boundary for any model under test.

## Token-consistent generation

FTAAT enforces token consistency when building prompts and grading responses:

- `scripts/helpers/token_utils.py` loads provider-specific token inventories (see `tokens/*.json`) and filters them with `provider.count_tokens` so every symbol is a single tokenizer unit. This keeps the prompt length predictable as $N$ and $K$ grow.
- `scripts/helpers/fact_gen.py` assembles unique key/value sequences from that inventory, ensuring no duplicate keys or values across a trial. Collisions are rejected up to a configurable retry budget.
- `scripts/build_prompt.py` renders the final prompt with `prompt_template.j2`, inserting both the fact list and the query section that requests answers in a fixed format.

## Evaluation metrics

The benchmark measures performance on two axes, implemented in `scripts/run_experiments.py`:

1. **Sequence accuracy** — the fraction of requested key→value lines that match exactly, as computed by `evaluate_token_sequences` (see `scripts/helpers/eval.py`).
2. **Token accuracy** — the proportion of individual tokens (split on the `|` delimiter) that match, providing a softer signal when whole lines are wrong.

A **major format flaw** flag is also emitted when the response deviates from the expected structure (e.g., missing tokens, repeated lines, or malformed boundaries). Scores for flawed responses are forced to zero, preventing optimistic accuracy reports.

## Scaling strategy

`scripts/run_experiments.py` supports two scheduling modes:

- **Cartesian sweeps** iterate over every combination of `facts_list_sizes` and `token_sizes` you specify.
- **Staircase schedules** (via `staircase_schedule`) progressively double $N$ and $K$ from a seed pair until configured maxima are exceeded, producing a rapid failure curve survey.

For providers that implement batch APIs (e.g., OpenAI), the runner packages multiple prompts into deferred requests with automatic size checks and resumable uploads. Non-batch providers run each trial sequentially while still capturing per-trial latency and token counts.

## Results artefacts

Each experiment writes a JSON summary to `results/<provider>/<model>_<N>N_<K>K_<timestamp>.json`. Every file contains the controlling parameters, per-trial grades, and the exact prompt/response texts. These artefacts can be promoted to a SQLite store through `core/json_import.py` for downstream analysis.

With this design, FTAAT isolates memory capacity from tokenisation quirks, letting you correlate failure points directly with $(N, K)$ instead of fuzzy prompt length heuristics.
