# Methodology: four games, narrowly stated claims

## What is measured

Synthetic associative lookup, two-edge lookup, revision selection, and ordered bulk
recall from a single prompt. The full record set remains available during answering.
Calling this "memory" is a visual metaphor, not evidence of persistent memory or a
measurement of neural attention. The experiment uses official API models, not the
ChatGPT or Claude consumer apps with their different system prompts and tools.

## Units and fairness

The primary comparison is **same text**: every provider receives the same system
instructions, records, query, seed, and ground truth. API envelopes necessarily differ.
Different models tokenize identical text differently. We report model-specific counts
rather than declaring that equal characters or equal records imply equal tokens.
N is the record count. K is the count of four-letter random ASCII symbols separated
by a vertical bar. A sequence with K symbols is not asserted to have K model tokens.
Record depth is explicitly labeled; token offsets are not inferred from character offsets.

A future **same-token-budget** study would require separate, per-model prompt fitting
and would no longer use identical text. Do not pool it with this study. A future
fixed-token FTAAT study must verify complete rendered sequences in each relevant
tokenizer, not just isolated inventory entries; Claude's count API does not provide
local token IDs. We decline to invent Claude token boundaries.

## Counting and context

OpenAI's official input-token endpoint accepts the model, input, instructions and
reasoning configuration. We send the same input fields used for generation.
Source: https://developers.openai.com/api/reference/python/resources/responses/subresources/input_tokens/methods/count

Anthropic's model-specific count endpoint includes messages and the system prompt.
Its count is documented as an estimate; response usage is retained separately.
Source: https://platform.claude.com/docs/en/build-with-claude/token-counting

Response usage is the authoritative usage record, not a recount of displayed text.
Reasoning tokens and cache fields are preserved in the raw usage. Anthropic input
usage totals include regular, cache-read and cache-creation categories. OpenAI total
input includes its cached subset. Cost is a conservative ceiling using the dated
standard rates, charging all input at 1.25x to cover short cache writes; it is not an
invoice. Long-context price tiers not explicitly verified in a profile are skipped.

No automatic truncation is requested. Complete expected output byte length plus a
margin is checked against the output cap for these ASCII tasks. This prevents obvious
under-allocation but does not guarantee enough hidden reasoning tokens. Exhausted
output remains a separate outcome. Different reasoning settings are printed in the
manifest and prevent a simple architecture-only attribution.

## Reproducibility and scoring

A versioned generator uses a local seeded PRNG. The random IDs are unique within a
trial. Moving the needle preserves its key/value. Each case stores its exact evidence
lines and character spans; each question has deterministic ground truth. Independent
solver tests reconstruct the answers from records.

The primary endpoint is exact whole-response success after outer/line whitespace
normalization. Missing, extra, reordered or duplicated answer lines fail this endpoint.
Secondary sequence and pipe-symbol scores use the entire expected denominator.
A perfect prefix cannot get a perfect whole-trial score. Format validity is separate.
No LLM judge is used. Responses with a non-completed API status are unscored and shown
as other outcomes, not hidden. A response can be content-wrong but format-valid.

95% Wilson intervals use independent seeds within a fixed model/task/N/K/depth/control
cell. Answers within one recall response are correlated and not separate trials.
Different depths reuse the same underlying facts, so they must not be pooled as
independent trials. A pilot with three seeds gives very wide intervals. No corrected
multiple-comparison claim or "statistically significant winner" is made.

## Confounds and honest interpretation

- Larger N changes input length and distractor count together; it does not isolate them.
- Recall also grows output length. A failure there cannot alone prove input retrieval failure.
- Revision selection is partly instruction-following; two-hop is partly composition.
- Synthetic random codes differ from meaningful documents and can favor some tokenizers.
- Provider load, caching and request order affect latency. Randomized order helps but
  does not make a few timings a provider-speed benchmark.
- Historical price, release age, and capability are different variables. Older does
  not automatically mean cheaper or available. Account access is checked live.
- Successful needle retrieval does not establish good summarization, reasoning or RAG.

## Prior work

RULER already evaluates real context capability across synthetic tasks:
https://github.com/NVIDIA/RULER

NoLiMa explains a limitation of literal-overlap retrieval and uses latent associations:
https://github.com/adobe-research/NoLiMa

Our four games are an accessible experiment, not a claim to invent long-context evaluation.
The original old runner's outputs are not trusted as new evidence without re-auditing.
