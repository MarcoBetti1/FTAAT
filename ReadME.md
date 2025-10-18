# Fixed Token Abstract Attention Test (FTAAT)

FTAAT is a benchmark that probes how large language models memorise abstract key→value associations when both the number of facts ($N$) and the length of each key/value sequence ($K$) are tightly controlled at the token level. By scaling $N$ and $K$ independently, you can trace a model’s failure curve and separate memory load from token complexity.

## Key capabilities

- **Token-consistent prompts** – facts and answers are assembled from inventories of single-token symbols (see `scripts/helpers/token_utils.py`), ensuring comparable difficulty across models.
- **Flexible schedules** – sweep Cartesian grids or staircase progressions of $(N, K)$ via `scripts/run_experiments.py` to map failure boundaries quickly.
- **Provider abstraction** – adapters in `llm_providers/` standardise query and token-count APIs for OpenAI, DeepSeek, Ollama, and future backends.
- **Reproducible artefacts** – every run saves rich JSON summaries under `results/`, with utilities in `core/` to import, index, and analyse outcomes.

## Repository at a glance

- `scripts/` – experiment runner, prompt builder, batching helpers, and evaluation utilities.
- `core/` – shared services for template hashing, result discovery, and SQLite ingestion.
- `llm_providers/` – provider integrations implementing a consistent interface for querying and token counting.
- `docs/` – in-depth documentation covering design rationale, pipeline details, providers, notebooks, and data management.
- `FTAAT.ipynb`, `token_generation.ipynb`, `visual.ipynb` – notebooks for exploratory runs, token inventory generation, and visual analysis.
- `prompt_template.j2` – Jinja2 template that renders the fact table and answer instructions used in every prompt.

## Quick start

1. Install dependencies from `requirements.txt` and export the relevant API keys (e.g., `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`).
2. Regenerate a prompt identifier if you customise the template:

	```python
	from core.template_utils import generate_prompt_id_from_template
	prompt_id = generate_prompt_id_from_template()
	```

3. Launch an experiment sweep:

	```python
	from scripts.run_experiments import run_experiments

	run_experiments(
		 provider_module="llm_providers.openai_llm.OpenAIProvider",
		 facts_list_sizes=[3, 6, 12, 24],
		 token_sizes=[2, 3, 4],
		 trials=3,
		 adaptive=True,
		 prompt_id=prompt_id,
	)
	```

4. Post-process and analyse results with the helpers in `core/` or the notebooks in the project root.

## Documentation

The full documentation lives in `docs/`:

- [Documentation hub](docs/index.md) – entry point and rationale for token-consistent benchmarking.
- [Benchmark design](docs/benchmark_design.md) – how $(N, K)$ experiments are generated and graded.
- [Experiment pipeline](docs/pipeline.md) – step-by-step instructions for running and extending the pipeline.
- [Provider integrations](docs/providers.md) – API contracts and configuration for each backend.
- [Notebooks guide](docs/notebooks.md) – tips for exploratory workflows.
- [Results and data management](docs/results_management.md) – how to store, import, and inspect artefacts.

Refer to the documentation for deeper dives into each component and for guidelines on adding new providers or visualisations.

