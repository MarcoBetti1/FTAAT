# GPT Learning — Episode 01

AI-generated narration using OpenAI stock voice Cedar. Original procedural graphics.

## 00:00:00,000 — The model found it. The score said zero.

Here is a real response from GPT-4.1 Mini. The correct answer is in the response. Our strict score still says zero. That sounds like a bad memory result. It is actually a warning about how easy it is to tell the wrong story with a benchmark.

## 00:00:17,917 — We gave AI more paperwork.

Welcome to GPT Learning, our independent experiment notebook. Meet Pip, clerk at the Bureau of Misplaced Facts. Today we compare language models using deliberately artificial games. The full record list stays in the prompt while they answer. Memory is our visual shorthand. We are not measuring a hidden memory module or the model's internal attention weights.

## 00:00:39,625 — Before testing AI, test the ruler.

The project began as a fixed token attention test. But look at these four symbols. Each is one token in this tokenizer. Once we join them, the three separators count as well. The complete sequence has seven tokens. Four symbols and four model tokens are different measurements.

## 00:00:57,542 — Our first discovery was in our own code.

We checked one thousand seeded four-symbol sequences from the original inventory, using the tokenizer mapped to GPT-4o Mini. All one thousand used seven tokens. This is a local tokenizer measurement, not an inference result. Our old output allowance used the symbol count, so a long answer could run out of space for a reason we caused.

## 00:01:19,917 — A perfect prefix is not a perfect answer.

There was another problem. The old scoring helper could divide by the number of answers returned, instead of the number requested. Return one correct line and omit three, and a perfect prefix could look perfect. We fixed that. One out of four is twenty five percent. The missing lines still belong in the denominator.

## 00:01:38,375 — Same text. Model-specific token counts.

For the new experiment we used identical seeded records and deterministic answer keys. This evidence bundle contains 369 observed responses from 7 models. We counted each full request against the actual model using its official API, then saved the returned usage separately. We tested API models, not the ChatGPT and Claude websites. Settings and system prompts can make those products behave differently.

## 00:02:06,083 — The missing file

Hide a random key and value among other records. Move that fact through the list. The negative control asks for a key that is absent and expects UNKNOWN. This tests literal retrieval. It does not prove the model can understand every kind of document.

## 00:02:22,417 — Observed results / The missing file

In the matched four-model pilot for this game, 96 of 96 completed responses matched the requested output exactly. Every model passed every needle case in this small pilot, including the missing-key controls. Pip has briefly become insufferable. But these prompts had only sixteen or one hundred twenty eight records. Passing this version does not establish reliability at a hundred thousand tokens.

## 00:02:50,792 — A fact that really was in the prompt.

Here is a different kind of result. In this GPT-4o Mini trial, the model returned UNKNOWN. The target record was present among eight thousand, one hundred and ninety two records, with one hundred and eleven thousand, five hundred and thirteen actual input tokens. The API completed normally. This is a wrong answer on this specific test, not just extra formatting. It is one observation, not an estimated failure rate. The full prompt and evidence location are saved so it can be checked.

## 00:03:21,625 — Follow the paperwork

Now the first record points to a second key, and that second key points to the answer. Both clues are in the prompt. The task combines retrieval with following a short chain. We cannot attribute every failure to context length alone.

## 00:03:35,958 — Observed results / Follow the paperwork

In the matched four-model pilot for this game, 44 of 72 completed responses matched the requested output exactly. Haiku has no strict passes here, but all eighteen of its responses have a formatting problem. That is a giant sign saying: read the answers. GPT-4o Mini also makes errors in correctly shaped outputs. Those are different behaviors, even when the score paints both of them red.

## 00:04:02,167 — The stale memo

Two records disagree. The higher revision number wins, even when the stale record appears later in the text. This adds a rule the model must apply. A wrong answer could reflect rule following, interference, or retrieval. The score by itself does not tell us which.

## 00:04:18,500 — Observed results / The stale memo

In the matched four-model pilot for this game, 62 of 72 completed responses matched the requested output exactly. Haiku and Luna follow the requested contract throughout this pilot. GPT-4o Mini has nine strict failures, all flagged for formatting. The filing cabinet is sometimes finding the paperwork and delivering the entire folder when we asked for one label. The response audit keeps that distinction visible.

## 00:04:49,083 — The entire inventory

Finally we request every value in shuffled order. More records also mean a longer answer. That changes two things at once. If generation hits the output limit, we mark it separately. Hitting the output cap is not evidence that the input was forgotten.

## 00:05:06,667 — Observed results / The entire inventory

In the matched four-model pilot for this game, 19 of 22 completed responses matched the requested output exactly. Two GPT-4o Mini requests hit the output limit, and are shown as other outcomes rather than memory failures. GPT-4.1 Mini passes its six trials. Six is a small number. These games are useful for finding questions to investigate, not for awarding a permanent intelligence trophy.

## 00:05:34,375 — Fresh records. A reproducible contrast.

We checked that long-context needle condition with fresh seeds. GPT-4o Mini answered 0 of 8 correctly. GPT-5.6 Luna answered 8 of 8 correctly. Both got identical text: eight thousand one hundred ninety two records, with the target near the end. All these API responses completed normally. The samples are small, and this condition was chosen after exploration. This supports a specific reproducible contrast. It does not mean one model has a universal memory limit or never makes mistakes.

## 00:06:06,875 — What this run actually supports.

The full bundle has 281 exact successes out of 352 completed responses. 43 completed responses have formatting problems. 2 responses hit an output limit, and 15 were refusals. In 35 strict failures on single-answer tasks, the expected string still appears somewhere in the output. That is why a single red square is not enough evidence for the headline that a model forgot.

## 00:06:31,833 — The newer models got their own panel.

We also collected 45 responses in a separate small current-model panel. 15 were refusals, not scored memory failures. The separate long-context exploration reached 186127 actual input tokens. That exploration stopped at its allocated budget, so not every planned comparison is complete. We do not combine these different panels into a fair-looking seven-model leaderboard.

## 00:06:56,500 — A small experiment, not an intelligence ranking.

The random codes are intentionally arbitrary. Tokenization differs, reasoning settings differ, and our smallest cells have only a few seeds. Latency is affected by caching and provider load. Older does not always mean cheaper. The report keeps per-condition counts and uncertainty intervals, while these overview bars are only descriptive. Our fresh-seed check is a start. A stronger follow-up would use more seeds, more positions, and meaningful documents as well as random codes.

## 00:07:26,167 — Publish the paperwork. Keep asking better questions.

The conservative token-cost estimate for these responses is 4.14 dollars. The code, prompts, scoring rules, and complete response audit accompany the report. This first experiment taught us to check both the model and the measuring instrument. Sometimes the most interesting result is not that artificial intelligence failed. It is that our explanation was too simple. Pip would like that entered into the record.
