> **Historical documentation:** the paid notebook runner is retired. See [current methodology](methodology.md) and [repository README](../ReadME.md) for the supported workflow and corrected token/scoring claims.

# Notebooks guide

The repository ships three Jupyter notebooks that complement the scripted pipeline. They are useful for exploratory work, ad-hoc debugging, and visual analysis.

## `FTAAT.ipynb`

- Contains the original end-to-end experiment flow, including manual prompt generation, provider querying, and grading.
- Serves as a readable blueprint for `scripts/run_experiments.py`; the first code cell demonstrates how to construct a prompt and grade responses manually.
- Supports only the OpenAI API out of the box. Helper functions were later extracted into the `scripts/` package for reuse.

## `token_generation.ipynb`

- Rebuilds the single-token inventories stored in `tokens/`.
- Use it when introducing a new provider or updating model tokenisation. The notebook introspects the provider's tokenizer and records tokens that remain single units in both prompts and answers.
- The same logic powers `scripts/token_generation.py` for headless environments.

## `visual.ipynb`

- Provides a starting point for analysing and plotting failure curves.
- Includes utility cells for cleaning result JSON files, recalculating format flaws, and recomputing accuracies after pipeline updates.
- Relies on the JSON artefacts written by `scripts/run_experiments.py` or on database imports performed via `core/json_import.py`.

When documenting experiment runs, link to the specific notebook revision and store key charts (e.g., failure curves) alongside the generated JSON files to preserve provenance.
