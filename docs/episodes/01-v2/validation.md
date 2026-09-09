# Final validation — second edition

Final video: **7:26.733**, native **1920×1080 at 30 fps**, H.264 with stereo 48 kHz AAC. 35 shots, 34 narration clips, five short Pip interjections, and 132 timed burned-in caption cues. An SRT is supplied separately.

## Experiment checks

- 810/810 substantive requests observed; all completed. Sixteen smoke responses are separate.
- All 240 distinct case answer keys independently recomputed from the prompt records. All saved evidence spans match the prompts.
- All four substantive run identities match their committed core source at `6eed3bc7f2753abdbde10d30d60ed262339634ef`. Film work caused some dirty working-tree flags, but did not change the core used for these calls.
- Official full-request preflight counts reconciled to model-specific actual usage. Observed preflight/usage deltas were zero for this run; that does not promise future estimates will always match.
- The single prespecified paired contrast and Wilson intervals have dedicated offline tests. Other conditions remain descriptive.
- 64 tests pass locally. GitHub CI passed on Python 3.11, 3.12, and 3.13: [run 34414810352](https://github.com/MarcoBetti1/FTAAT/actions/runs/34414810352).

## Export and editorial checks

- Complete final MP4 decoded without errors. Stream dimensions, frame rate, codec, audio format, and duration passed checks.
- Final encoded audio measured **-16.0 LUFS** integrated, **-2.2 dBFS** true peak.
- Caption cues are ordered, non-overlapping, within the timeline, and limited to two lines inside the safe width.
- Representative frames from all 35 encoded scenes were visually reviewed, along with targeted full-size source frames.
- Per-clip ASR confirms the spoken headline numbers against the audited data. Canonical model names, punctuation, and caption text come from the reviewed script. ASR is a review aid, not proof of every phoneme.
- One omitted nonessential sentence was removed and that narration clip regenerated. Final captions use per-clip timing to avoid word spill across hard cuts.
- The original edition-one MP4 hash is unchanged. The user retains control of channel creation and YouTube uploading.

## Budget reconciliation

OpenAI experiments: $13.556607 conservative bound. Speech reservations: $1.85. Transcription QA reservations: $0.254730. Total bound including production: **$15.66**, within $20.

Anthropic experiments, Haiku only: **$2.97**, within this pass’s $5 cap. No unsettled experiment dispatch remains. These are conservative bounds/reservations, not provider invoices.

## Integrity

Final MP4 bytes: `20564041`.

SHA-256: `1b66ab1fb39fc78026f3c8eb1cff6ec96c14aedc7ba9ebc0aac9b4b2686e8390`.

[Machine-readable production audit](production-audit.json) · [Content review](content-review.json) · [Experiment report](report.md)
