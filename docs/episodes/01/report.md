# One hidden fact in 111,000 tokens

**Episode 01 of GPT Learning — experiments run on September 9, 2026.**

Eight fresh, identical-text trials produced a specific contrast: **GPT-4o Mini
answered 0/8 correctly; GPT-5.6 Luna answered 8/8 correctly**. Each prompt contained
8,192 synthetic records, with the target near 90% of the record list. All 16 API
responses completed normally. This is evidence about that task and those settings,
not a universal memory limit, general intelligence ranking, or production reliability estimate.

We also repaired methodological problems in the old FTAAT code and collected a
broader four-game pilot and a small current-model panel. The complete campaign has
**373 observed responses including four smoke tests**. The episode evidence bundle
contains 369 responses after excluding those smoke tests.

## Fresh-seed check

| Model and settings | Exact success | 95% Wilson interval | Actual input tokens |
|---|---:|---:|---:|
| GPT-4o Mini, snapshot 2024-07-18, temperature 0 | 0/8 | 0%–32.4% | 111,389–111,556 |
| GPT-5.6 Luna, reasoning effort none, default sampling | 8/8 | 67.6%–100% | 111,388–111,555 |

Same text, system instructions, record depth and fresh seeds (2901–2908). The output
cap was 256 for both, and no response was incomplete. The generation controls are
not identical: the profiles are disclosed above, so this is a comparison of configured
systems rather than an isolated causal effect of release year or architecture.

This condition was selected after exploratory failures at long context. It is an
independent-seed follow-up to that selected condition, not a preregistered survey of
all possible tasks. The intervals are descriptive and do not correct for the entire
exploratory search. Eight trials are still a small sample.

## Matched four-model pilot

The pilot used 16 and 128 records, three seeds, three evidence positions (where
applicable), two symbols per code and absent-key controls. Every model received all
66 cases. The table shows exact requested output among completed responses.

| Model | Needle | Two-hop | Revision selection | Bulk recall |
|---|---:|---:|---:|---:|
| GPT-4o Mini | 24/24 | 11/18 | 9/18 | 3/4, plus 2 incomplete |
| GPT-4.1 Mini | 24/24 | 17/18 | 17/18 | 6/6 |
| GPT-5.6 Luna | 24/24 | 16/18 | 18/18 | 5/6 |
| Claude Haiku 4.5 | 24/24 | 0/18 | 18/18 | 5/6 |

**A strict failure is not necessarily lost information.** All 18 Haiku two-hop
responses had a formatting problem; many explicitly included the expected answer.
All nine GPT-4o Mini revision-selection strict failures had a formatting problem.
GPT-4o Mini also produced wrong but correctly shaped two-hop answers, a different
failure category. The complete response audit preserves these distinctions.

One concrete example: GPT-4.1 Mini returned
`revision 9: TXHS|OQYB => EDHU|RHBX` when only `EDHU|RHBX` was requested. That is a
strict-contract failure with the requested information present. Calling it a memory
failure would misrepresent the response.

Counts in this overview pool conditions for readability. Positions reuse the same
underlying facts; they are not independent trials to pool for statistical inference.
The machine-readable per-cell reports retain depth, N, K, seed and outcome details.

## Current-model panel

These models each received the same 15 cases at 128 records, three fresh seeds,
and middle placement. This is a separate panel from the cheaper-model pilot.

| Model | Completed exact answers | Refusals |
|---|---:|---:|
| GPT-6 Astra, low reasoning | 15/15 | 0 |
| Claude Sonnet 5, provider defaults | 15/15 | 0 |
| Claude Opus 5, provider defaults | No scored answers | 15 |

Opus returned `stop_reason: refusal`, empty content, and zero output tokens. We
cannot infer its retrieval ability from these responses, and we do not know why the
provider refused these benign synthetic inputs. An independent recheck with a small
ordinary-language control would be useful; this campaign did not establish a cause.

Astra and Sonnet's perfect scores on 15 small cases do not establish reliability at
the much longer contexts used in the separate exploration. No seven-model combined
leaderboard is claimed.

## Longer-context exploration

The 4,096/8,192-record exploration planned 80 requests. It collected 44 responses,
skipped two capacity checks, and left 34 unattempted when its budget guard stopped
it. Observed input usage reached **186,127 tokens**. The model panels are therefore
incomplete and unequal; raw success totals should not be used to rank them.

The initial GPT-4o Mini needle example returned `UNKNOWN` with the target present
among 8,192 records and 111,513 actual input tokens. The API reported normal completion.
That motivated the fresh-seed check above. Long two-hop trials also contained both
wrong-answer and explanation/format cases.

## What the repaired experiment measures

The four games test literal retrieval, short linked lookup, a revision rule, and
ordered bulk recall. The record list remains available throughout generation. This
is not a measurement of hidden attention weights or persistent conversational memory.

We use model-specific official request-counting endpoints and save actual response
usage. No generic Claude tokenizer is substituted. Preflight counts and actual
usage are distinct fields, including the difference. Evidence depth is labeled in
records, not mislabeled as an exact token offset. K denotes pipe-delimited symbols.

The local inventory check found 1,000/1,000 sampled four-symbol GPT-4o Mini sequences
used seven tokens after adding the separators. The original N×K output cap ignored
that extra length. The old scoring helper also used truncated denominators, and its
batch path matched replies by order rather than request ID. The unsafe paid path is
retired; the new workflow has deterministic cases, durable reservations, exact
request identities and separate non-completed outcomes.

A final QA correction (`score-v1.1`) recognizes `UNKNOWN` as a validly formatted absence claim, even when wrong. It corrects secondary format labels only; no exact/sequence/symbol success score changes. The raw ledgers retain their original grades, and the evidence bundle includes both stored and corrected grades. See [correction log](scoring-correction.json).

The secondary format flag checks line and pipe-delimited symbol counts, not a complete lexical grammar.

Primary scoring is exact output after line whitespace normalization. Secondary
sequence/symbol accuracy retains the entire expected denominator. A post-hoc
expected-string-mention diagnostic helps inspect formatting failures; it is not
semantic correctness and does not replace the prespecified primary score.

## Cost and artifacts

The conservative experiment token-cost estimate is **$4.137084**, including the
smoke test. It charges all input at 1.25× ordinary input rates to cover short cache
writes, so it is not an invoice. It excludes narration production. Production reserves allow up to $0.65 for narration and $0.20 for duration-bounded spoken-number/caption QA transcriptions. Together with the experiment estimate, these planning allowances remain below the $5 overall budget.

- [Campaign and confirmation summary](summary.json)
- [Methodology](../../methodology.md)
- [Audit of the original code](../../audits/2026-09-09.md)
- [Experiment protocol](../../../experiments/PROTOCOL.md)
- [Reproduce the local tokenizer measurement](../../../scripts/audit_token_accounting.py)
- [Video treatment](../../../video/TREATMENT.md)

The release evidence archive includes full synthetic cases, raw response/usage
records, manifests, per-cell reports and the complete non-exact response audit.
All API credentials are excluded. Narration is AI-generated using a stock voice;
all diagrams and the paper-clerk character are original procedural graphics.

## Useful next experiments

Repeat the selected needle condition with more seeds and earlier evidence positions;
match generation controls where supported; try natural-language documents; separately
check the unexplained Opus refusal behavior; and distinguish lost facts from lost
state in a future chess experiment. The current evidence supports specific questions,
not a universal winner.
