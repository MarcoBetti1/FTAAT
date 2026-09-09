# Second edition — working plan

User asks for a better experiment and a more entertaining, carefully crafted video.
They mean the assistant's reasoning about production, NOT increased reasoning effort
on tested models. Preserve the existing model profiles (GPT-4o Mini temp 0, GPT-4.1
Mini temp 0, GPT-5.6 Luna reasoning none/default sampling, Claude Haiku 4.5 temp 0).
No new channel or video upload: user will handle both. Main-branch GitHub updates
remain authorized. Keep edition 1 and its ledgers intact.

New spending authorization: OpenAI $20. User has $5 Claude credits and intends to
add $5 more; this pass deliberately caps fresh Claude spend at $5 and uses Haiku.
Do not pool provider limits. Include narration/QA in OpenAI's $20.

## Scientific improvement

- New deterministic games-v2 module; preserve games-v1 and its reproducibility.
- Nested record sets: target facts and the initial distractor pool are stable as N
  grows. Move the same target among 10%, 50%, 90% record positions.
- Main OpenAI panel: 3 models, N=128 (8 seeds), N=4096 (16 seeds), N=8192 (32 seeds),
  all 3 positions. Add 8 absent controls at N=8192.
- Small Claude panel: the first 4 matched seeds at N=128 and N=8192, all 3 positions,
  plus 2 absent controls. Label its smaller sample explicitly.
- Format experiment: 16 fresh seeds each for two-hop and revision lookup at N=128;
  original-style request vs a final explicit answer-format reminder. Same records
  and task, prompt wording is the intervention. All 4 models, normal reasoning settings.
- Score exact full requested output AND a predeclared standalone final-line answer.
  Extract without consulting the answer key. No expected-string-mention metric
  masquerading as semantic correctness. Keep refusals/output limits as separate
  outcomes and show success per dispatched request as well as per completed response.
- Fix two-hop/revision evidence placement metadata; do not conflate position and
  linked-record separation. The main claim remains literal needle retrieval.
- Commit the fixed protocol and seeds before new paid calls; no outcome-based
  expansion or early success stopping. Every comparison must show planned/observed
  and skipped/unattempted requests.
- Official model-specific full-request counts plus actual usage, durable no-retry
  budget reservations. Model settings disclosed as configured-system comparisons.

## Production direction

A coherent short documentary/game: Pip opens the world's worst filing office.
Three acts: easy job, growing paper mountain, the scoring trap. Real audience
prediction pauses, escalating visual scale, character reactions and recurring
bureaucracy jokes. No permanent lecture-slide header, no long blocks of caveats in
narration, no decorative motions unrelated to the explanation. Important caveats
remain beside the relevant result; full details in the report. Original Pip design,
stock disclosed narration, original sound cues. Target roughly 6–8 minutes, native
1080p, strong motion and visual storytelling. Select the final title/story beats
from actual results, without manufacturing a dramatic outcome.

Planned caps (must stay within provider totals): OpenAI main panel <=15.5, format
<=1.0, smoke <=0.1, production <=2.5, reserve 0.9. Claude main panel <=3.7, format
<=0.9, smoke <=0.1, reserve 0.3. These are ceilings, not spending targets.
