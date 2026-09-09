# Episode 01 production

The episode uses observed API results, original procedural graphics, and Pip, an
original paper-clerk character. Stock Cedar narration is AI-generated and disclosed
on screen and in the description. It does not imitate a real presenter. No external
music, footage, or character assets are used. Sparse original synthesized notes and
quiet paper-like transitions leave the numerical explanations clear.

## Render

Install `.[video]`, FFmpeg (including libass) and fonts. The current renderer uses
macOS Arial/Menlo paths; change the font constants for another operating system.
First extract the release evidence archive into the repository.

```bash
python video/render_episode.py --evidence artifacts/episode-evidence/evidence.json --stills-only
python video/render_episode.py --evidence artifacts/episode-evidence/evidence.json --voice-engine local --skip-mux
```

Local narration uses macOS `say` and is a scratch track. `--voice-engine openai`
**makes paid API requests** for uncached text; exact text/settings are cached. The
speech helper reserves $0.025 per clip, up to 26 clips ($0.65). This is a planning
allowance, not an invoice or a provider-enforced cap. It does not retry uncertain
requests. Do not delete receipts to circumvent the limit.

For the actual episode, 23 clips were generated, including replaced takes. Two
full QA transcriptions were followed by a final transcription after a spoken-number
clarification. The cumulative requested duration remains below 2,000 seconds;
Whisper's configured $0.006/minute rate puts that within the $0.20 QA allowance.
Changing prices requires reviewing these bounds before another production.

```bash
python video/audio_qa.py
python video/finalize_episode.py --captions-only
python video/sound_design.py
python video/render_polished.py
python video/brand_assets.py
```

`audio_qa.py` makes a paid transcription request when its receipt/transcript is
absent. Review the transcript against the script, especially names and numbers.
Final captions use the reviewed script for wording and ASR for timing; mismatched
spans are interpolated. All final statistics are derived from the evidence bundle.
The literal spoken long-case numbers have an assertion against the selected case.

The final motion pass draws type and graphics directly at 1920×1080. The MP4 is
24 fps, H.264/AAC with fast-start metadata. Captions are
burned in and provided separately as SRT. The voice and restrained original sound cues are mixed and normalized to approximately
−16 LUFS with a −1.5 dB true-peak target before AAC encoding. The local delivery includes an original thumbnail, captions and upload description.
GitHub holds the reviewed script and raw evidence. The channel owner handles
YouTube creation and video upload.

## Editorial boundaries

- Four-model pilot bars compare identical complete panels.
- Current models have their own 15-case panel; Opus refusals remain unscored.
- The budget-stopped long exploration is incomplete and cannot support a leaderboard.
- The eight-seed confirmation is a selected-condition check, with wide uncertainty.
- Secondary formatting flags and post-hoc expected-string mentions do not replace
  the exact-output primary metric or prove semantic correctness.
- No fabricated results or historical unre-audited runs appear as new observations.

The report documents `score-v1.1`'s secondary format-label correction. Original
ledgers remain untouched. See `scripts/validate_episode.py` for offline verification.
