> **Historical documentation:** the paid notebook runner is retired. See [current methodology](methodology.md) and [repository README](../ReadME.md) for the supported workflow and corrected token/scoring claims.

# Experiment pipeline

This guide walks through the end-to-end flow for running Fixed Token Abstract Attention Test (FTAAT) experiments, surfacing the key scripts and modules involved.

## 1. Configure the project

- Set provider credentials in your environment (e.g., `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_MODEL`). Many providers also allow overriding the default model name via environment variables.
- Review `config.py` for root paths used across the project (`RESULTS_ROOT`, `TEMPLATE_PATH`, and the SQLite location `DB_PATH`). Create the `results/` folder if it is missing.
- Install dependencies from `requirements.txt` into a Python 3.12+ environment.

## 2. Inspect and customise the prompt

- `prompt_template.j2` defines the instruction block and placeholders inserted by the runner. Variables available in the template include `facts_block`, `questions_block`, `n`, and `k`.
- Update the template to adjust instructions or answer formatting. Changes automatically propagate because prompts are regenerated on every run.

## 3. Generate token vocabularies

- Provider-specific token inventories live in `tokens/*.json`. Use `scripts/token_generation.py` or the `token_generation.ipynb` notebook to refresh them when models or tokenisers change.
- `scripts/helpers/token_utils.py` enforces that each entry is a single token for the provider. Any mismatch raises a descriptive error so you never run benchmarks with inconsistent token lengths.

## 4. Run experiments

The primary entry point is `scripts/run_experiments.py`:

```python
from scripts.run_experiments import run_experiments
from core.template_utils import generate_prompt_id_from_template

prompt_id = generate_prompt_id_from_template()
run_experiments(
    provider_module="llm_providers.openai_llm.OpenAIProvider",
    facts_list_sizes=[3, 6, 12, 24],
    token_sizes=[2, 3, 4],
    trials=5,
    prompt_id=prompt_id,
    adaptive=True,
)
```

Key behaviours to understand:

- `generate_facts_k_tokens` (from `scripts/helpers/fact_gen.py`) constructs the fact table per $(N, K)$ pair.
- `build_prompt_for_all_keys` (from `scripts/build_prompt.py`) renders a coherent instruction block and randomises the question order.
- `grade_response` enforces formatting rules and computes metrics, delegating token-level comparison to `evaluate_token_sequences`.
- Providers that expose `queue_batch_request`/`submit_batch` (see `llm_providers/openai_llm.py`) will automatically batch prompts up to the `batch_size` threshold, respecting OpenAI's 100 MB input limit via `flush_batch`.

All intermediate metadata (prompt tokens, latency, raw answers, grading outcomes) are included in the JSON artefacts written to `results/<provider>/`.

## 5. Import results for analysis

- `core/json_import.py` ingests JSON artefacts into the SQLite database defined in `config.DB_PATH`, enabling downstream queries or dashboarding.
- `core/db_utils.py` handles connection management and schema initialisation, creating the `trials` table on first access.
- `core/results_utils.py` provides convenience helpers to locate the latest run per $(N, K)$ pair or iterate through stored results for a given prompt/provider combination.

## 6. Visualise and iterate

- `FTAAT.ipynb` shows the original interactive pipeline and is helpful for quick experiments or debugging.
- `visual.ipynb` demonstrates how to plot failure curves, re-clean results, and analyse format flaws.
- As you tune schedules or prompts, regenerate a `prompt_id` via `core/template_utils.generate_prompt_id_from_template`. This ID is included in every result file, making it easy to group experiments by prompt revision.

Following these steps ensures that each run stays token-consistent, properly logged, and ready for comparative analysis across models.
