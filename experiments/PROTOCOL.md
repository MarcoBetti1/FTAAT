# Episode 01 protocol — before looking at results

Working question: **Can a bigger context window still lose a tiny fact?**

1. Smoke test one case per chosen model. Confirm endpoint access, model ID, counts,
   actual usage, output status, price assumptions and the absence of silent truncation.
2. Pilot: `pilot.json`, 66 same-text cases x 4 models = 264 proposed requests.
   Three seeds per cell are exploratory, not a strong reliability estimate.
3. Small current-model panel: `current-panel.json`, 66 x 3 proposed requests. Run
   only after the cheaper pilot and within a separately recorded campaign budget.
   GPT-6 Astra uses low reasoning; Luna uses none; Anthropic profiles retain their
   defaults unless a verified model-specific profile is substituted. These are not
   identical compute allocations; report this on screen.
4. Long-context exploration: `context-sweep.json`. No growing-output recall here,
   so retrieving one answer can be studied without simultaneously requiring a long answer.
5. Choose interesting cells transparently, including surprising successes. Confirm
   with 20+ NEW seeds when affordable. Record every explored cell and selection rule.
6. Counterchecks: move the evidence; reduce distractors; increase output allowance
   for incomplete responses; include UNKNOWN controls. Distinguish a reasoning/output
   bottleneck from failed retrieval. Keep each changed condition in a separate manifest.

Do not hide all-success curves to force an entertaining failure. An episode can be
about how hard it is to break these models, or how the test itself was misleading.

## Candidate panels

- Historical low-cost OpenAI snapshots: GPT-4o Mini (2024-07-18), GPT-4.1 Mini (2025-04-14).
- Recent cost-oriented OpenAI: GPT-5.6 Luna.
- Lower-cost Anthropic: Claude Haiku 4.5 (2025-10-01).
- Current larger models: GPT-6 Astra, Claude Sonnet 5, Claude Opus 5.

IDs, context limits and standard pricing were checked in official documentation on
2026-09-09. Availability on these accounts is unverified. No unavailable model will
be silently replaced, and the set may change after the smoke test.

## Publication evidence

Publish config, generator/scorer versions, prompt hashes, actual API usage, anonymized
request metadata, all non-sensitive synthetic prompts, complete outcomes and report.
API keys never belong in an artifact. The code repository and video link to each other.
Every numerical on-screen claim must map to a run/case or report group. No synthetic
mock response, test fixture or illustration may be labeled as a model result.

## Budget

Start with a proposed $5 total pilot budget, pending the user's amount and funded keys.
This document does not authorize charging an existing unrelated key. Track cumulative
spend across directories manually in the campaign notes. Per-run budget checks do
not replace the provider's own project limits. Price tables are dated and model-specific.
