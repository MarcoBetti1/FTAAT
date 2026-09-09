# Second-edition film

An original filing-office comedy built from audited experiment results. Pip is an
original paper clerk. No footage, artwork, narration, music, or character from
Numberphile or 3Blue1Brown is copied or imitated. Cedar narrates; Onyx voices Pip.
Both are disclosed stock AI voices. Sound cues are original NumPy synthesis.

The user meant more thought about entertaining production, not increased reasoning
on the models under test. The experiment retains its configured model settings.

## Build

Run from the repository root with its Python environment. Dependencies: Pillow,
NumPy, Matplotlib, httpx, python-dotenv, FFmpeg and ffprobe. The native typography
uses macOS Avenir Next, Georgia, Menlo, and Apple Symbols font files. Their font
files are not redistributed. Install equivalent licensed fonts and adjust
`art.font` to build on another operating system.

```sh
python -m scripts.analyze_v2
python -m scripts.report_v2
python -m video.v2.story
python -m video.v2.speech
python -m video.v2.audio --clip-qa
python -m video.v2.render --stills
python -m video.v2.render --jobs 2
python -m video.v2.verify
```

`speech` and uncached `audio` transcription calls spend API credit only when their
exact cached output is missing. They reserve a bounded allowance before dispatch
and never automatically retry an uncertain request. Do not rerun the experiment
to reproduce a film. Use its original evidence archive and cached audio.

`story.py` derives all result sentences from the final summary; assertions require
editorial review if the data no longer support the story. `motion.py` supplies
directed shots; explanatory illustrations are labeled separately from actual
responses. Final captions use reviewed script words aligned to ASR timestamps.
Final timing uses individual clip transcriptions to avoid word spill across cuts.
An earlier whole-film transcription is retained as an independent review. Alignment
changes are preserved for spoken-number review. The rendering pipeline
uses native 1920×1080 geometry at 30 fps, caches each shot, and concatenates encoded
shots without another video generation loss. Final AAC audio is normalized to
approximately −16 LUFS with headroom for true peaks.

The original film and all first-edition ledgers are retained. The new output is
`artifacts/episode-01-v2/GPT-Learning-01-v2.mp4`. YouTube publishing is left to the
user. Public GitHub release assets contain experiment evidence, not the video.
