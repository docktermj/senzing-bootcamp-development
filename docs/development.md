# Senzing Bootcamp development

How a change to the Senzing Agentic AI Bootcamp moves from an issue to a release. The
repository's layout, the build and the everyday commands are in the root
[`README.md`](../README.md).

## Setup

Install the development dependencies before running the test suite:

```console
python3 -m pip install -r requirements-dev.txt
```

Run everything:

```console
python3 -m unittest discover -s tests
```

`pytest -q` also works and prints a shorter summary; it is not required.

### Why the install step matters

The dependencies are `fpdf2`, `Pillow` and `imageio-ffmpeg`, and none is a runtime
requirement of the bootcamp. The shipped PDF generators tier their renderers — `fpdf2` when
importable, a stdlib fallback otherwise — so a bootcamper without it still gets a PDF, and
that fallback path ships and is tested.

The recap-video renderer, `source/scripts/generate_recap_video.py`, draws frames with `Pillow` and
encodes them with ffmpeg, taken from `PATH` first and then from `imageio-ffmpeg`. Without
them, `tests/test_recap_video.py` skips its frame-drawing and end-to-end tests with a reason
and still runs its storyboard-validation tests.
Its Piper voice (`piper-tts`, #341) is **not** a development dependency: the renderer only runs
it as `sys.executable -m piper`, and the tests stub `find_spec` and the subprocess instead of
installing it.

Without `fpdf2` the tests that measure the *fpdf2-rendered* output cannot exercise it. They
skip, and the suite prints one notice up front naming the cause:

```text
fpdf2 is not installed for /usr/bin/python3

The tests that measure the fpdf2-rendered PDF will be SKIPPED. They are not
failing: the stdlib fallback renderer lays out pages differently, so their
assertions do not describe it. The fallback's own tests still run.
```

⚠️ **A green run without `fpdf2` is a weaker signal than a green run with it** — the fpdf2
renderer goes unmeasured. Install it before trusting a run, and always before a release.
Set `SBCP_QUIET_FPDF2_NOTICE=1` to suppress the notice for tooling that parses test output.

CI runs the suite **both ways** on every pull request
(`.github/workflows/test-suite.yaml`, a matrix over `fpdf2: [present, absent]`), so neither
path can rot unnoticed. The `absent` job is the one that catches a new fpdf2-dependent test
landing without a `@requires_fpdf2` guard — an omission that is invisible locally to anyone
who has `fpdf2` installed.

Before this was wired up (#30), those tests did not skip — they ran against the fallback and
failed as 41 assertions about certificate names, grid alignment and label wrapping, only 6 of
which named the missing package anywhere in their traceback. The suite read as 41 product
defects when the only defect was an unstated prerequisite.

## Trying a build locally

Nobody installs from this repository. It has no marketplace of its own, and bootcampers install
from the public repository, `Senzing/bootcamp`. To try a change, build the packages and start an
assistant on the built one.

1. Build every assistant's package, catalog and page. They are written under `dist/`, which is
   gitignored.

    ```console
    python3 -m tools.bootcamp_build build
    ```

1. Start the assistant on its built package. For Claude Code:

    ```console
    claude --plugin-dir dist/plugins/claude/senzing-bootcamp
    ```

    For GitHub Copilot:

    ```console
    COPILOT_PLUGIN_DIR_ONLY=true copilot --plugin-dir dist/plugins/copilot/senzing-bootcamp
    ```

1. Say "Start the bootcamp".

Both paths are relative to the repository root. The bootcamp expects a new, empty project
folder, so to walk it start the assistant in one and give the package's full path.

⚠️ **Build again after every change.** The assistant reads the package under `dist/`, never
`source/`, so an edit reaches it only through a new build.

If the published plugin is installed on the same machine, make sure the bootcamp you are
running is the build. Copilot CLI loads only the named directory when `COPILOT_PLUGIN_DIR_ONLY=true`
is set, as in the command above (checked on Copilot CLI 1.0.111).

Before opening a pull request, run `python3 -m tools.bootcamp_build check` and the test suite.
`check` builds to a scratch directory and stops a change that would reach only some assistants.

## Conventions

### Spelling: US English, not British English

**US English is the preferred spelling throughout this repository** — shipped
plugin prose, specs, invariants, tests, code comments, and identifiers alike.
Prefer `-ize`/`-yze` over `-ise`/`-yse`, `-or` over `-our`, `-er` over `-re`,
`license` over `licence`, and a single `l` before a suffix (`labeled`,
`modeled`, `traveled`).

| British (avoid) | US (use)     | British (avoid) | US (use)     |
| --------------- | ------------ | --------------- | ------------ |
| analysed        | analyzed     | judgement       | judgment     |
| artefact        | artifact     | labelled        | labeled      |
| behaviour       | behavior     | licence         | license      |
| catalogue       | catalog      | millimetre      | millimeter   |
| centre          | center       | normalise       | normalize    |
| colour          | color        | organisation    | organization |
| defence         | defense      | recognise       | recognize    |
| favour          | favor        | sanitise        | sanitize     |
| honoured        | honored      | summarise       | summarize    |

Two deliberate exceptions, both verified rather than assumed:

- `source/scripts/vendor/d3.v7.min.js` — a vendored
  third-party bundle whose `grey` is a CSS color-name key, not prose.
- `D:\Programme` in `tests/test_windows_browser_discovery.py` (and where
  `specs/IMPLEMENTED.md` records it) — a *German* localized `%ProgramFiles%`
  fixture proving environment expansion. It is not English.

`SCOPE_VERBS` in `.claude/skills/compact-dev-environment/widened_scope.py`
deliberately carries both `"generalis"` and `"generaliz"` so the scanner stays
tolerant of either spelling in text it reads.

This is **INV-253**, enforced by `tests/test_us_english_spelling.py`, which scans
the whole tree and matches whole words after splitting identifiers on both `_`
and CamelCase boundaries — so `test_the_..._limit` and `NoStep...Changed` are
caught as readily as prose.

⚠️ **A clean run does not mean the corpus is US English.** The guard's word list
is hardcoded and cannot be otherwise: the corpus is the thing being judged, so
there is nothing to derive the vocabulary from. A clean run means no *listed*
form is present. Two consequences worth knowing before you rely on it:

- `analyses` is deliberately absent, because it is both the British verb and the
  correct US plural of `analysis`. Those seven occurrences were converted by
  hand and would not be caught coming back.
- Stem matching is rejected: `organism`, `mechanism`, `parallelism`,
  `characteristic`, `equally`, `totally`, `radialLine` and
  `LabelLayoutAssertions` are all correct and all contain British-looking stems.

A file that must carry a British form is waived by **path plus the exact word and
count**, never as a whole file, so every other British form in it still fails and
a waiver whose word has gone fails as stale. There is no marker you can add to a
line to silence the guard — that is deliberate, or it becomes the way every
future British spelling gets waved through.

## The invariant register

`specs/INVARIANTS.md` is the one register of the bootcamp's rules, and its `INV-NNN` ids are
authoritative. An id is never renumbered and never reused for another rule, so a citation keeps
pointing at the rule it was written for. [`specs/README.md`](../specs/README.md) lists the
register's ledgers and says where the earlier history is archived.

- **One register serves every assistant.** Every package is built from this repository, so no
  assistant keeps a copy of the register that could fall behind.
- **No derived copy is published.** Until the one-repository migration (2026-11-14) each other
  assistant's bootcamp lived in a repository of its own, a port that read this one as its
  parent, and `invariant-manifest.json` was generated from the register for those ports
  (INV-311). The ports are gone, so the manifest and its generator were not carried here.
- **Supersession is marked by a bullet and by nothing else (INV-313).** An entry carrying
  `- **Superseded by:** INV-nnn — <what changed>` is superseded, and every other entry is
  active. Prose mentioning supersession is not evidence, and there is no third state.
- ⚠️ **A `Partly superseded by:` bullet leaves the entry active.** Only a clause was replaced
  and the rest still binds in full. Read the bullet when one is present.
- **`/review-invariants` registers every change.** No other maintainer command edits
  `specs/INVARIANTS.md`: a command that ships or finds an invariant change drafts it as a block
  in `specs/IMPLEMENTED.md`, and `/review-invariants` registers it after the maintainer's
  sign-off (INV-365).

⚠️ **No count of invariants is stated here deliberately.** A figure in prose goes stale silently
while reading authoritative; read the register.

## How the pieces fit together

One repository holds the bootcamp for every assistant. The root [`README.md`](../README.md)
describes the layout: the bootcamp itself in `source/`, what differs for one assistant in
`hosts/<assistant>/`, and the build in `tools/bootcamp_build/` that writes each assistant's
package from the two. Bootcampers never install from here. A tested release is promoted into
the public repository, `Senzing/bootcamp`, which is where they install from and what
`hub.senzing.com/bootcamp/` is published from.

A change moves through four steps:

1. **An issue.** New work is tracked as GitHub issues in this repository.
1. **A pull request.** The issue is implemented on its own branch and opened as a pull request.
1. **A release.** `/release` bumps the version, writes the CHANGELOG entry and creates the git
   tag as one unit.
1. **A promotion.** `/propagate-to-public` carries the tagged release into a clone of the
   public repository and stops there. The maintainer commits and pushes it.

The page these rules used to live on, the family workflow shared by one repository per
assistant, was not carried into this repository. The rules that still apply are stated on this
page.

**The maintainer chooses the issue.** `/implement-github-issue` *(user level)* takes the one
issue the maintainer names and never begins work on any other; invoked with no argument it
names no issue and stops. Choosing belongs to `/order-github-issues` *(user level)*, which
reviews the open issues, reports how they depend on each other with the evidence for each
claim, names the one it suggests and stops.

⛔ **(INV-316) A command named on a maintainer page either ships here or is marked as not shipping.**
A command that ships is a skill under `.claude/skills/<name>/` with a `SKILL.md`, or a file in
`.claude/commands/`. `/<name>` runs the skill directly (measured 2026-09-29 on Claude Code
2.1.284, #241), so every maintainer operation here is its skill, and `.claude/commands/` ships no
file (#262). One that does not ship carries its reason at the point of use: a statement of
retirement, as `/implement-spec` *(retired)* is below, or *(user level)*: the name is defined
only under `~/.claude/skills/`, and this repository keeps its obligations in
`.claude/skill-overlays/<name>.md` (#239), as for `/implement-github-issue` *(user level)* and
`/unattended-issue-loop` *(user level)*. A third marker, *(children only)*, was for a command
that only a port repository shipped. There are no port repositories now, so no name on this page
carries it.

`tests/test_documented_dev_commands_match_the_shipped_set.py` holds the list below both ways
round: a skill missing from the list fails the suite, and so does an entry that names no skill
and carries no *(user level)* marker. A *(user level)* marker also fails when no overlay backs
it, or when a skill or command of that name ships here.

⚠️ **That guard reads the numbered ``1. `/name` `` list shape only.** A command named anywhere
else on this page, inside a fenced block included, is invisible to it. The guard that read
every maintainer page was not carried into this repository.

## The unattended loop works only on labeled issues

`/unattended-issue-loop` *(user level)* works only on issues labeled `unattended-ok`. The label
is how the maintainer says an issue is safe to work with nobody watching, given one issue at a
time.

- **An unlabeled backlog is a no-op.** With no open issue carrying the label the loop finds
  nothing to do and ends without changing anything.
- ⛔ **(INV-318) The loop never applies that label itself**, and no other maintainer command
  applies it to an issue it files. Choosing work for the loop is the maintainer's decision
  alone.
- **It merges by default.** The loop merges each pull request whose checks pass, because
  starting it is the maintainer's consent. `--no-merge` leaves every PR open.

## Claude development skills

⛔ **(INV-302) This list and the maintainer operations must agree in both directions**: every
skill under `.claude/skills/`, together with any command under `.claude/commands/`. Each entry
below is a skill, and `/<name>` runs it. An entry marked *(user level)* is the exception INV-316
allows: no skill or command of that name ships here, and its overlay under
`.claude/skill-overlays/` must exist. A documented command that does not ship tells you to
run something that does not exist; one that ships undocumented is undiscoverable. Every
entry carries a description. Do not state how many there are — the set is derived and
compared, and a count in prose goes stale silently while reading authoritative.

⛔ **(INV-307) `specs/` is frozen as of the 2026-09-15 cutover; new work is tracked as
GitHub issues.** See [`specs/README.md`](../specs/README.md). ✅ **Every command that used to
write there has now been reworked**, and none is blocked: `/feedback-to-issues` files GitHub
issues (#49), `/implement-spec` was retired (#50, #60), `/unattended-issue-loop` *(user level)* is renamed and
label-gated and writes only its issues' `IMPLEMENTED.md` entries (#51, #69, #215),
`/production-readiness-audit` files issues when attended and records findings in the ledger when
not (#69), `/dry-run` drafts each finding into its run's `IMPLEMENTED.md` entry and files issues
from there (#153), and `/delegate-to-mcp-server` files issues and writes nothing under `specs/`
(#114).
⚠️ **Its ledger, `specs/mcp-coverage.jsonl`, is a named live exception to the freeze** (#142).
`IMPLEMENTED.md`, `DECLINED.md`, `INVARIANTS.md`, `README.md` and `mcp-coverage.jsonl` are
**not** frozen and are still written to. The frozen spec files themselves were not carried into
this repository: `specs/README.md` says where they are archived.

### Triage feedback

1. `/feedback-to-issues` - File GitHub issues from SENZING_BOOTCAMP_FEEDBACK.md files.

### Development loop

1. `/order-github-issues` *(user level)* - Report how the open issues depend on each other and name one to start; it changes nothing and starts nothing.
1. `/refine-github-issue` *(user level)* - Refine an issue into a complete spec, or break it into sub-issues; `/release-cycle` stage 2 runs it in batch mode.
1. `/implement-github-issue` *(user level)* - Take the GitHub issue you name to pull-request-open on its own branch; the maintainer chooses the issue.
1. `/review-invariants` - Decide the deferred invariants awaiting sign-off.
1. `/delegate-to-mcp-server` - Find Senzing facts the plugin still holds that the MCP server now serves, and file issues to delegate them.
1. `/compact-dev-environment` - Compact the development environment: overlapping invariants, redundant test traversals and stale feedback.
1. `/production-readiness-audit` - Do a thorough static review.
1. `/dry-run` - Do a thorough runtime review.
1. `/unattended-issue-loop` *(user level)* - Take the `unattended-ok` issues to pull requests unattended; the section above states its label gate and merge policy.

### Publish

1. `/auto-test` - Probe the live MCP server for drift; optionally walk the bootcamp.
1. `/retrofit-from-public` - Find changes made directly in the public repository since the last promotion and file issues describing them; writes nothing in either repository's files.
1. `/release` - Bump the version, write the CHANGELOG entry and create the git tag as one unit.
1. `/propagate-to-public` - Promote a tested release into a clone of the public repository by running `python3 -m tools.bootcamp_build promote`; never commits or pushes.
1. `/release-cycle` - Run the whole cycle, from finding issues to publishing, as one resumable run that stops only at its checkpoints.
