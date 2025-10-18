# Results and data management

FTAAT logs every experiment in JSON files and optionally promotes them into a SQLite database for richer analysis. This document explains the artefacts produced by the pipeline and the utilities available to consume them.

## File artefacts

Each run of `scripts/run_experiments.py` saves a file in `results/<provider>/` with the pattern `<model>_<N>N_<K>K_<timestamp>.json`. Every file contains:

- Global metadata: `id`, `prompt_id`, `provider`, `model`, `num_facts` ($N$), and `k` ($K$).
- A `trials` array with per-trial metrics (`sequence_accuracy`, `token_accuracy`, `major_format_flaw`, `response_time_ms`, token counts, and the raw prompt/response texts).

These files serve as the source of truth for post-hoc grading, debugging, or visualisation.

## Database schema

`core/db_utils.py` initialises a SQLite database located at `config.DB_PATH` (default `experiments.db`). The `trials` table includes:

- Primary key: `(id, trial_idx)` to deduplicate results.
- Provider/model identifiers and the controlling parameters ($N$, $K$).
- Stored metrics (sequence accuracy, token accuracy, format flaw) and auxiliary data (latency, prompt tokens, raw texts).

`core/json_import.py` walks through the `results/` directory, parses JSON artefacts, and inserts missing rows into the database. Re-running the importer is safe because duplicates are ignored via `sqlite3.IntegrityError` handling.

## Utility helpers

`core/results_utils.py` offers helper functions to:

- Resolve the folder for a given `prompt_id` and provider.
- Check whether a result file already exists for a specific $(N, K)$ pair (`file_exists`).
- Retrieve the latest JSON file for a pair (`latest_json`).
- Iterate through all saved trials for a prompt/provider combination, returning structured dictionaries for analysis (`iter_saved_trials`, `saved_metrics`).

These utilities are especially useful inside notebooks or Streamlit dashboards that load and compare results interactively.

## Token inventories

The `tokens/` directory stores provider-specific JSON files listing the symbols verified to be single tokens. These inventories are critical for keeping prompts consistent across runs. Regenerate them whenever tokenizer implementations change or when you add a new provider.

## Prompt tracking

`core/template_utils.generate_prompt_id_from_template()` hashes `prompt_template.j2` to produce a stable identifier included in every result file. This mechanism lets you compare experiments across prompt revisions and quickly detect when a template change invalidates prior results.

Combined, these utilities make it straightforward to track experiments, avoid reruns, and feed data into dashboards that visualise the failure curve as $N$ and $K$ scale.
