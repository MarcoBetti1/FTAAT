# Prespecified second-edition protocol

Frozen before paid second-edition observations. See the Git commit timestamp and
configuration files in `experiments/v2`. Original episode data are exploratory
background, retained unchanged, and are not pooled into this replication.

## Questions and primary contrast

The primary contrast is exact completed output **per dispatched request** between
GPT-4o Mini (2024-07-18, temperature 0) and GPT-5.6 Luna (reasoning none, provider
default sampling) at 8,192 records and 90% nominal record depth, using 32 fresh seeds
4101–4132. All cases are deterministic and identical across the models. This tests
configured systems, not the isolated effect of model age, sampling, or architecture.
Report each model's 95% Wilson interval and the paired discordance counts; an exact
two-sided McNemar test is the single prespecified inferential contrast. No omnibus
model ranking or corrected significance claim is made for the secondary cells.

Secondary descriptive questions: how do length and evidence placement change exact
success; does repeating the answer-format instruction change strict compliance and
correct final-line answers? These plots are descriptive. Seeds repeat across depths
and lengths; do not treat all those cases as independent observations. The primary
32-seed condition has one observation per model and seed.

## Cases and panels

The `games-v2` seed excludes N, depth and prompt wording. Increasing N retains the
same target fact and adds distractors from the same deterministic pool. Changing
depth moves the target while preserving all records. K=2 four-letter symbols,
separated by a vertical bar. N counts records, not tokenizer units.

OpenAI main panel: three models (GPT-4o Mini, GPT-4.1 Mini, GPT-5.6 Luna), 128 records
with 8 seeds, 4,096 with 16 seeds, 8,192 with 32 seeds, each at 10%, 50%, 90% record
depth. Eight additional absent-key controls use 8,192 records. 176 cases × 3 models.

Claude main panel: Haiku 4.5 only, matching the first four main-panel seeds at 128
and 8,192 records and all three positions; two matching absent controls. 26 cases.
Its smaller sample is explicit. Compare models on their shared cases when directly
contrasting Claude with the OpenAI panel; never disguise the unequal panels.

Format panel: two-hop lookup and revision selection, each at 128 records, 16 seeds
4201–4216, baseline wording vs a final answer-format reminder. Four models receive
all 64 cases (192 OpenAI requests, 64 Claude). The paired prompts differ only in the
reminder; records, expected answer, evidence positions and system prompt are equal.
Both evidence records have fixed nominal positions (25%, 75%) in this panel. No
position/separation effect is inferred from it. This intervention changes prompting,
not the model's reasoning setting. Max output 2,048, identical across the panel.

Smoke checks use separate seed 4001 and are excluded from substantive results.
Needle main-panel max output is 256 for every model. No escalation of tested-model
reasoning. No output-budget fishing or alternate prompts after observing outcomes.

## Two output measurements

1. Strict exact output after line whitespace normalization, unchanged from edition 1.
2. A standalone final-line answer: the last nonempty line must contain only a valid
   K-symbol code or UNKNOWN. A complete pair of backticks or bold markers around that
   line may be stripped. No other words, labels or code-fence blocks are accepted.
   The extractor never receives the answer key. Its returned value is then compared
   with the key. This is a narrow final-answer measure, not universal semantic grading.

A refusal or output-limited request is not evidence of failed retrieval. It does
count as unsuccessful delivery for exact-success-per-dispatched reporting and is
also shown explicitly as a separate outcome. Conditional accuracy among completed
responses is secondary. Transport uncertainty is kept separate; incomplete pairs
are excluded from the paired test and disclosed. Never infer failure of internal
attention mechanisms from a task score.

## Counts, budgets and stopping

Use official model-specific full-request count endpoints, save actual usage and
returned model IDs, preserve full prompts/responses and immutable event ledgers.
Anthropic preflight is an estimate; no generic Claude tokenizer is substituted.
Depth is labeled in records, with exact character spans saved. No token-offset claim.
Prices were checked against official model pages on 2026-09-09; sources are in each
model profile. All input is conservatively charged at 1.25× ordinary price, including
cached input; this is a planning bound rather than an invoice. Serial requests and
configured input-token pacing reduce rate-limit risk. Uncertain requests are not
retried automatically.

Provider caps for this pass: OpenAI $20 total including narration and transcription;
Claude $5 (Haiku only). Stage ceilings are in WORKING-PLAN.md. Reserve before dispatch,
stop at the stage cap, and report every planned, observed, skipped and unattempted
request. No early success stopping, post-result expansion, or pooling across stages
to hide missing conditions. The final film's story and conclusion follow the data.
