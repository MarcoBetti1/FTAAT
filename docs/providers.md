# Provider integrations

The `llm_providers` package encapsulates the adapters required to query different large language model backends while keeping the benchmark pipeline agnostic to their APIs.

## Common interface

`llm_providers/base.py` defines the `LLMProvider` abstract base class. Providers should implement:

- `provider_id`: short, filesystem-friendly name used in result folders.
- `model_name`: default model identifier (configurable via environment variables).
- `token_set_path`: path to the JSON file containing single-token symbols compatible with the provider's tokenizer.
- `query(prompt, *, temperature, max_tokens, timeout)`: synchronous completion call that returns plain text.
- `count_tokens(text)`: helper that returns the tokenizer's token count for `text`.

Providers may optionally implement batching helpers:

- `queue_batch_request(prompt, metadata, max_tokens)` collects jobs for later submission.
- `submit_batch(save_dir, timeout_sec)` flushes queued jobs to the provider's batch API and returns the resulting JSONL path plus metadata copy.

Any provider exposing both optional methods automatically opts into batched execution in `scripts/run_experiments.py`.

## Available providers

### DeepSeek (`deepseek_llm.py`)

- Uses the OpenAI-compatible DeepSeek API via the `openai` Python SDK with a custom base URL.
- Requires `DEEPSEEK_API_KEY` and optionally `DEEPSEEK_MODEL`.
- Token counts rely on `transformers.AutoTokenizer` (`deepseek-ai/DeepSeek-V3`).
- Batching is not currently implemented; runs execute sequentially.

### OpenAI (`openai_llm.py`)

- Wraps OpenAI's Chat Completions and Batch APIs using the official SDK.
- Requires `OPENAI_API_KEY` and optionally `OPENAI_MODEL`.
- Implements `queue_batch_request` and `submit_batch`, enabling large experiment sweeps without hitting rate limits.
- Tokenisation uses `tiktoken.encoding_for_model`, matching the JSON token inventories in `tokens/gpt4o_tokens_clean.json`.

### Ollama (`ollama_llm.py`)

- Targets a locally hosted Ollama instance (default `http://localhost:11434`).
- Model override via `OLLAMA_MODEL`; you can point to any model pulled into Ollama.
- Issues HTTP requests to the `/api/generate` endpoint.
- Token counting uses `tiktoken`'s `llama3` encoding when available, falling back to `transformers` if needed.

## Discovery utilities

`core/discover.py` provides a Streamlit-friendly utility to discover provider classes dynamically. It scans `llm_providers/` for modules ending in `_llm.py`, imports them, and registers any classes whose name ends with `Provider`. This enables UI-driven provider selection without hard-coding module paths.

## Adding a new provider

1. Create `llm_providers/<name>_llm.py` with a class inheriting from `LLMProvider`.
2. Implement the `query` and `count_tokens` methods, referencing your SDK of choice.
3. Generate a single-token JSON inventory and place it in `tokens/`.
4. (Optional) Add batch helpers if the provider supports asynchronous execution.
5. Confirm that `core/discover.discover_providers()` lists the new provider, then reference it via its dotted path when calling `run_experiments`.

With the interface constraints in place, the benchmark can compare providers fairly while letting each integration handle authentication, rate limiting, and tokenizer quirks internally.
