# Tests

Dev-only tests for the Senzing Bootcamp plugin. They live here at the repo top
level — **not** under `source/` — so `propagate.sh` (which mirrors `source/`
into the public repo) never ships them to bootcampers.

Standard library only; no third-party dependency (INV-108). Availability of the
optional `fpdf2` renderer is probed with `importlib.util.find_spec`, never by
importing it in a test.

Run everything:

```bash
python3 -m unittest discover -s tests
```

Install `fpdf2` first, or the tests that measure the fpdf2-rendered PDF will skip:

```bash
python3 -m pip install -r requirements-dev.txt
```

That is a dependency of the *renderer under test*, not of the tests. The shipped
generators fall back to a stdlib renderer without it, and that fallback path ships
and is tested — so the suite stays green either way, but a run without `fpdf2`
leaves the fpdf2 renderer unmeasured. `tests/_fpdf2_support.py` prints one notice
when it is absent and supplies the `@requires_fpdf2` guard; see `docs/development.md`.

- `test_write_gate.py` — exercises the PreToolUse write-gate security control
  (`source/scripts/write-gate.py`): location allow/block,
  `..`-traversal, home-relative and `$TMPDIR`/`%TEMP%` temp paths, the
  case-folded in-project exemption, and secret detection (PEM / AWS / Senzing
  `AQAAAD` license blobs). Invoked as a subprocess because the gate reads stdin
  at import time.
- `test_recap_video.py` — the recap-video renderer (`generate_recap_video.py`): storyboard
  validation naming the field at fault, the project-relative image rule, exit codes 0/1/2/3,
  every fallback stated on stderr, narration that extends its scene rather than being cut,
  frame drawing (skipped without Pillow) and an end-to-end mp4 render (skipped without Pillow
  or ffmpeg). Pillow and `imageio-ffmpeg` are in `requirements-dev.txt`. The Piper voice stage
  (#341) is tested with a stubbed `find_spec` and a fake subprocess: Piper first, the whole
  video re-voiced by the platform engine on any Piper failure, numbers spelled out for Piper
  only, and the public-domain default voice.
- `test_broll_manifest.py` — the graduation-video B-roll manifest (`docs/video/broll.json`) that
  `module-completion.md` Step 2e writes at every module's close: the entry format keyed by state
  token, the no-raw-record-values rule, replace-on-re-completion, recreate-on-unreadable,
  never-blocks, and that the documented example's facts validate as renderer scenes.
- `test_graduation_video_step.py` — graduation Step 1c, the optional graduation video: its place
  after the recap PDF, the offer and install questions verbatim, nothing written on no, the
  time budget and its rescaling over the modules taken, the Intro scene that always opens it
  (#347), the example storyboard validating through the renderer, opening on the Intro and
  ending on the certificate and the tag line, the no-raw-values rule,
  the non-blocking fallbacks for exit codes 1–3, and the duration, frame and audio checks.
- `test_model_guidance_behavior.py` — the bootcamp never asks the bootcamper to change the model
  or the reasoning effort (issue #4): a scan of every text file in every assistant's built package
  finds no switch question, no "Are you done modifying the model and effort?" gate, no 👉 question
  about either, no slash command or control that sets either and no module-start nudge; and the
  retired `model_guidance` preference is read nowhere. Negative controls paste each retired shape
  back and see it reported; a diagnostic mention in the feedback context is not. Its siblings:
  `test_welcome_names_one_model_once.py` (the welcome's one statement),
  `test_working_depth_by_stage.py` (one effort level per stage, one instruction per level, the
  same bytes in every package), `test_bootcamp_build_guidance_parity.py` (no frontmatter, agents
  directory, hook configuration or settings file sets either) and
  `test_model_docs_name_no_switch.py` (the maintainer notes, every assistant's site tips, and
  each install page: a model it names is the welcome's, and it names no effort, issue #13).
- `test_brand_sync.py` — asserts the inlined fallback palettes in
  `senzing_viz_server.py` and `generate_recap_pdf.py` stay equal to
  `brand_tokens.py`, so the hand-maintained copies cannot drift silently.
- `test_recap_pdf_guard.py` — pins the recap PDF generator's two outcome classes
  apart (`generate_recap_pdf.py`): a recognizable-but-incomplete recap warns,
  renders, and exits 0 (graduation is non-blocking), while a non-recap input or
  catastrophic content loss writes no PDF, prints no `PDF generated:` line, and
  exits non-zero. Also covers the content-retention figure, the
  never-silent `fpdf2` downgrade, the stdlib fallback's landscape certificate
  (INV-066/INV-100), and `--check`'s exit semantics.
