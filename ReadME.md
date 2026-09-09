# ContextFrontier / FTAAT

Reproducible games that probe where language models lose track of supplied information.
Built from the **Fixed Token Abstract Attention Test (FTAAT)**, now being prepared for
an original educational video series, **GPT Learning**.

**Episode 01, second edition:** 810 substantive responses across four configured
models, plus 16 separate smoke checks. The new prespecified long-context comparison
produced **GPT-4o Mini 2/32 versus GPT-5.6 Luna 32/32**, with GPT-4.1 Mini at 31/32,
at roughly 111,000 input tokens. Claude Haiku receives a clearly labeled smaller
retrieval panel and the full paired formatting experiment.

[Read the new report](docs/episodes/01-v2/report.md),
[inspect the frozen protocol](docs/episodes/01-v2/PROTOCOL.md), and
[download the complete evidence](https://github.com/MarcoBetti1/FTAAT/releases/tag/episode-01-v2).
The [original animated film source](video/v2/README.md) gives Pip a filing office,
two stock voices, and an increasingly awkward performance review. Video publishing
is handled by the channel owner.

This is a synthetic task comparison, not a general intelligence ranking. Exact
delivery and a predeclared final-line answer score are reported separately. All
requests, model-specific usage, uncertainty, and paired reminder outcomes remain
auditable. [Edition one](docs/episodes/01/report.md) and its
[evidence](https://github.com/MarcoBetti1/FTAAT/releases/tag/episode-01) are retained
unchanged and are not pooled into this new experiment.

## Run locally

Python 3.11+ on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,video]'
pytest -q
python -m contextfrontier example --task two_hop
python -m contextfrontier plan experiments/pilot.json --output results/pilot-plan --budget 5
```

Copy `.env.example` to `.env` and fill in your own API keys locally. `.env` and run
artifacts are excluded from Git. `doctor` prints presence only, never key values.

```bash
python -m contextfrontier doctor
python -m contextfrontier run experiments/pilot.json --output results/pilot-live --budget 5 --live
python -m contextfrontier report results/pilot-live
```

Without `--live`, both `plan` and `run` are **offline**, contain no model results, and
make no claims about token counts or API cost. A live run counts each exact request
against its requested model before generation. It checks capacity and reserves a
conservative cost before sending. Resume with the same command/directory; completed
requests are not sent again. The budget is cumulative for that directory, not per
invocation. Keep a separate overall campaign budget when using several directories.

A billing-uncertain request stops the run and is never automatically retried. Inspect
provider billing before starting another run. The local cost ceiling depends on the
dated configured prices and provider estimates; retain provider-side spending limits.

## The games

| Game | Question | Main variable |
|---|---|---|
| Needle | Can you locate one random association? | Record count and evidence position |
| Two-hop | Can you follow two linked records? | Separation and record count |
| Updates | Can you choose the highest revision, even if stale text comes later? | Current/stale placement |
| Recall | Can you return every association in shuffled question order? | Associations and answer length |

The same seeded text is shared across models. Answer scoring is deterministic.
The absent-needle control expects `UNKNOWN`. These tests measure task performance,
not internal attention weights, human memory, or general intelligence.

## Counting correctly

- OpenAI: official `POST /v1/responses/input_tokens` with the actual model and input.
- Anthropic: official `POST /v1/messages/count_tokens`, including the system prompt.
  Anthropic documents this as an estimate; the model response supplies actual usage.
- Store preflight counts, actual input/output usage, cache fields, raw responses,
  returned model IDs, timestamps, request IDs, and the preflight/actual difference.
- Optional `tokens --model MODEL --file FILE` uses that model's tiktoken mapping for
  **text only**. It fails for unknown mappings. It is not a Claude tokenizer or a
  replacement for full-request counting.
- **K is the number of pipe-delimited symbols, not a fixed number of BPE tokens.**
  Joining individually single-token strings can change tokenization. Record depth
  is a fraction of records, not a claim about exact token position.
- No automatic prompt truncation. No generic tokenizer fallback. No silent model substitution.

See [methodology](docs/methodology.md), [audit](docs/audits/2026-09-09.md),
[experiment protocol](experiments/PROTOCOL.md), and [video treatment](video/TREATMENT.md).

## Outputs

Each run contains a manifest, full cases, an append-only event ledger, and generated
Markdown/JSON reports. Exact success uses complete trials; partial symbol/sequence
scores remain separate. Confidence intervals use seeds/trials, not individual answer
symbols. Refusals, output exhaustion, errors, and skips are separately reported.

## Historical notebooks

The original notebooks, inventories, and data readers are retained. The legacy paid
`run_experiments` entry point is retired because its batch matching, output caps,
and accounting could invalidate comparisons. It stops before making API calls and
points to the new runner. Legacy grading helpers now penalize missing answers.
Historical results need re-auditing and are not mixed into new experiments.

`docs/audits/historical-environment.txt` records the former environment as an
audit artifact, not an installation manifest. Those old pins contain known vulnerabilities. Optional notebook dependencies are available through `.[legacy]`.
DeepSeek and Ollama adapters are historical, unverified integrations, outside this
first OpenAI/Anthropic episode.

## Development

```bash
pip install -e '.[dev,video]'
pytest -q
python -m compileall -q contextfrontier scripts
```

The runner currently uses a POSIX file lock (macOS/Linux). Windows needs a compatible
lock implementation before live use. Packaging is local; no PyPI release is claimed.
No license was present in the original repository; no new open-source license has
been selected. GitHub visibility is preserved.

## Reproduce the episode analysis

Extract the release evidence archive into this repository, then run:

```bash
python scripts/validate_episode.py results/smoke-20260909 results/pilot-20260909 results/current-20260909 results/long-20260909 results/confirm-20260909 --output artifacts/validation.json
python scripts/episode_evidence.py results/pilot-20260909 results/current-20260909 results/long-20260909 results/confirm-20260909 --output artifacts/episode-evidence
```

These commands are offline. Original ledgers retain their experiment-time grades;
analysis version `score-v1.1` corrects 12 secondary `UNKNOWN` format labels without
changing any primary success score. [Video production instructions](video/PRODUCTION.md)
cover the optional paid narration step and local render.
