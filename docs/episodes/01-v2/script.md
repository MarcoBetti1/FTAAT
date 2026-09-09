# AI vs the World’s Worst Filing Cabinet

Original script; AI-generated stock voices Cedar and Onyx.

## 00:00 — One small job

This is Pip. Today, Pip is opening an artificial intelligence filing office. The job is simple: read the files, find one fact, return one answer. How bad could it be?

## 00:12 — The workload

We gave the office eight thousand, one hundred and ninety-two files. The answer really was in there. Some models found it. Others handed us... nothing.

## 00:23 — Pip considers his options

Pip: I have updated my résumé.

## 00:26 — AI vs the filing cabinet

So we tested older and newer GPT models, plus a small Claude. But the biggest plot twist wasn't just which model failed. It was what we were calling a failure.

## 00:37 — The challenge

Here is the game. A made-up code points to another made-up code. We ask for the value belonging to one key. No trivia. No internet. Every fact needed to answer is inside the prompt.

## 00:50 — Meet the applicants

Our applicants: GPT four O Mini, GPT four point one Mini, GPT five point six Luna, and Claude Haiku four point five. These are API models with the settings shown here, not the ChatGPT and Claude apps.

## 01:05 — Same fact, more clutter

As the filing cabinet grows, we keep the target fact and add distracting records. Move the target, keep the same files. Otherwise, a supposedly harder test could quietly become a completely different test.

## 01:19 — Fix the ruler first

And first, we fixed our own ruler. Four symbols are not necessarily four tokens. In this local tokenizer check, four symbols and their separators take seven. For the real requests, we use each provider's counting endpoint, then save actual usage.

## 01:37 — An administrative incident

Pip: The ruler has been referred to another department.

## 01:41 — Employee of the first thirty seconds

At a hundred and twenty-eight records, every model passed every present-key lookup we gave it. Excellent. Pip is employee of the first thirty seconds. Now let's see how long that certificate lasts.

## 01:54 — Eight thousand files later

We step up to four thousand records, then eight thousand. The largest GPT prompts are around a hundred and eleven thousand input tokens. That's a lot of filing. It is still inside these models' advertised context windows.

## 02:09 — Where would you hide it?

Before the results: where would you hide one fact to make it hardest to find? Near the beginning, in the middle, or near the end? Pick one. We tested all three.

## 02:21 — The prespecified showdown

Here is the comparison we picked before this run: the fact near the end, thirty-two fresh random seeds. GPT four O Mini: 2 out of thirty-two. Luna: 32 out of thirty-two. Same prompts. Very different afternoons.

## 02:36 — Inspect the failed delivery

This is one real failure. The requested key is present. Its value is right there. Four O Mini returns UNKNOWN. That is an incorrect answer, not just an untidy envelope.

## 02:49 — Location matters here

But move that fact. Four O Mini gets 6 of thirty-two near the beginning, 7 in the middle, and 2 near the end. Trouble in every location. Not exactly a reassuring floor plan.

## 03:01 — The model between them

GPT four point one Mini gets 31 of thirty-two in that same end-position comparison. These are specific model versions, settings, and synthetic files. We have measured a task failure, not filmed the inside of an attention mechanism.

## 03:19 — A smaller Claude panel

Claude Haiku gets 1 of four near the beginning, 1 of four in the middle, and 3 of four near the end. Four cases per position: a smaller budget, and a much blurrier picture. No grand league table from that.

## 03:34 — A score is not a law of nature

Even a big gap is not a law of nature. These bars show uncertainty across our sampled seeds. And the same seeds reappear at different lengths and positions. You can't count every dot as a new independent witness.

## 03:48 — Another department

Then we change the job. Instead of one lookup, follow two arrows. A points to B. B points to C. Return C. Pip calls this interdepartmental cooperation.

## 04:00 — Follow two arrows

Here are the two records from a real Claude case. Follow the first arrow, then the second. The final code is the answer. Claude found it. And then Claude wrote us a small guided tour.

## 04:13 — The guided tour

This is its actual response. First arrow. Second arrow. Correct final code. Our strict score says: failure. Why? Because we asked for only the code. The answer was right. The delivery was a lecture.

## 04:27 — Pip appeals

Pip: I would like to appeal this performance review.

## 04:32 — Two different questions

Across sixteen two-hop cases, Haiku gets 0 strict passes, but 16 correct final-line answers. Both scores matter. A program may need exactly one code. A person may care whether the answer was found. One red stamp cannot explain both.

## 04:48 — The sticky-note intervention

Can a sticky note fix the delivery? We repeat each case with one extra sentence at the end: return only the requested code, on one line, with no explanation, labels, or Markdown. Same files. Same model settings. Only that reminder changes.

## 05:05 — Read the sticky note

The reminder changed the strict two-hop score. Haiku goes from 0 to 1 strict passes out of sixteen. Its correct final-line score goes from 16 to 16. A reasonable-sounding prompt tip still has to survive an experiment.

## 05:21 — Message received

Pip: Your request for less paperwork has generated more paperwork.

## 05:25 — The stale memo

Our other small game is the stale memo. The higher revision wins, even when an older revision appears later in the file. Reading the last matching line is not enough. That is how you accidentally reinstate last year's sandwich policy.

## 05:40 — The star fails a tiny file

Remember Luna, our long-file star? Here it returns the older value. Perfectly formatted. Wrong revision. This little file has only a hundred and twenty-eight records. Pip would like that employee-of-the-month certificate back.

## 05:54 — Check a second task

Across sixteen revision cases, Luna scores 8 exact, then 13 with the reminder. Four O Mini goes from 4 to 7. So the reminder sometimes helps. But winning the giant filing game doesn't guarantee you'll survive a tiny stale memo.

## 06:12 — What the scores can say

So: a correct code with extra words is a delivery problem. UNKNOWN when the fact is present is a wrong answer. An unfinished response is a separate outcome. Calling all three 'the model forgot' throws away the interesting part.

## 06:28 — Test the test

We froze the new cases and the main comparison before running them. We saved full prompts, responses, actual token counts, and separate provider budgets. The report includes the other conditions too, including tests where the key is genuinely absent.

## 06:45 — What this does not prove

These nonsense-code files are a controlled obstacle course, not a miniature version of every real document. A model that wins here can still fail elsewhere. A context window is room for text. It is not a promise that every task inside it will work.

## 07:01 — Check the filing before firing the clerk

The lesson isn't to crown a permanent winner. Make the challenge clear. Check the ruler. Inspect the answer. Then decide what failed. The code and evidence are linked below. This is GPT Learning. Pip, any plans for our next experiment?

## 07:17 — Next: an organizational challenge

Pip: I have filed the chess knights under horses.

## 07:22 — Made for GPT Learning


