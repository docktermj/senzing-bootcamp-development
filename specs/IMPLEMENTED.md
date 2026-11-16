# Implementation ledger

Record of changes that have landed in this repository, newest first: one `## <name>` entry per
implemented GitHub issue, review or maintainer run. Do not delete history; append or update in
place.

This ledger starts on 2026-11-14, when the bootcamp moved to one development repository for
every AI assistant. Everything implemented before that is recorded in the ledger of the
repository this one replaced, kept as an archive at
<https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/blob/195c17dcc2fe6af7cf8097cc10cdc80f5da18eb2/specs/IMPLEMENTED.md>.
An invariant whose `(Source: …)` names an entry that is not below resolves there.

**The `Commit:` field.** It holds a commit hash, `uncommitted`, or
`committed (hash not recorded)`, and nothing else. An entry written before its commit exists
records `uncommitted`, and the next run that touches the entry fills the hash in.

**The fallback commit.** `conformance.py since --since-last-audit` and
`conformance.py reverse-check --since-last-audit` measure from the newest audit entry whose
`Commit:` names a commit in this repository. When no audit entry yields one, they measure from
the commit on the line below and print a `FALLBACK` line saying so. It is the commit that
brought this ledger and the maintainer skills across. `conformance.py` reads the hash from this
line and holds no copy of it, so changing the line changes the range.

- **Fallback commit:** 4587b43

<!-- New entries go directly below this line. Format:


## <spec-name>

- **Implemented:** YYYY-MM-DD
- **Files changed:** `path/one`, `path/two`
- **MCP re-check:** <server version + date + outcome, or "n/a (no Senzing fact)">
- **Summary:** <what was done and how the acceptance criteria were satisfied>
- **Commit:** <hash, "uncommitted", or "committed (hash not recorded)">

-->

## the-kiro-package-states-its-installed-path-for-linux-only

- **Implemented:** 2026-11-16 (issue #11)
- **Files changed:** `hosts/kiro/host.json`, `tests/test_kiro_skills_say_where_they_are.py`,
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16 against the change itself:
  it says where Kiro keeps an installed Power and what that statement rests on, and asserts
  nothing about Senzing. The two pages the record names are Kiro's and JFrog's. No absence claim
  about the Senzing MCP server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** The note the build appends to every Kiro `SKILL.md` no longer gives a path under
  `~`, and the repository records what the stated location rests on for each platform.
  - **The note.** `options.skill_location_note` gives the bootcamp's directory as
    `powers/installed/senzing-bootcamp/` inside the Kiro home and the skill's directory as
    `powers/installed/senzing-bootcamp/skills/<skill>/` inside it. It defines the Kiro home: the
    `KIRO_HOME` environment variable when it is set, otherwise `.kiro` in the user's home
    directory, with `%USERPROFILE%` named for Windows. It still says what "this skill
    directory", `<this-skill-dir>`, every `../` path and `${PLUGIN_ROOT}` resolve to, and still
    forbids a search of the rest of the filesystem.
  - **A `KIRO_HOME` that Kiro ignores.** When the bootcamp is not under `KIRO_HOME`, the note
    sends the assistant to `.kiro` in the home directory next. When the bootcamp's directory is
    missing, the assistant looks only inside `powers/` in the Kiro home.
  - **The record.** `options.skill_location_sources` has one entry each for `linux`, `macos` and
    `windows`, with `status`, `source` and `date`. Linux is `observed`: Kiro IDE 1.4.26,
    2026-11-15, the run in `hosts/kiro/checks.json`. macOS and Windows are `documented`,
    2026-11-16, and each says no run was observed there. The build reads `options` by key, so
    the record is in no package; a test asserts that.
  - **Not read again here.** The two pages were read on 2026-11-16 while the issue was refined.
    This run did not fetch them, and the record's wording follows the issue's.
  - **No real run was made.** `hosts/kiro/checks.json` is unchanged.
  - **Decided here, because the issue leaves it open.** The skill's directory is one path from
    the Kiro home, so the assistant composes nothing, and
    `tests/test_bootcamp_build_hosts.py` passes unchanged. The Linux entry says no recorded run
    tested `KIRO_HOME`: `observed` covers the default location only.
  - **Tests.** The module grew from 3 tests to 14. For every Kiro skill it asserts the note is
    stated once and carries each sentence above, with no `~` in it. For the record it asserts
    the three platforms, the three statuses, a source and a date for any status other than
    `unchecked`, a recorded run with the same date and client behind `observed`, and a page and
    "no run was observed" behind `documented`. The check that the Claude and GitHub Copilot
    packages carry no note is kept and now also looks for the note's heading, `KIRO_HOME` and
    "Kiro home", because the new wording no longer contains `.kiro/`. Negative control, run and
    then reverted: against the old note the module reports 109 failures and 1 error. The
    module finds the note by line, and says why at the read: the build appends it as one
    unwrapped line.
  - **Coverage limit.** Reading cannot establish where Kiro installs a Power. The test reads the
    note's wording and the record's shape. On macOS and Windows the location rests on
    documentation, and the `installed/<power-name>/` subfolder on a third-party guide.
- **Establishes no new invariant** (INV-309), and proposes a change to one in force. The
  register is not edited here (INV-365). The note's one hard-rule line still cites INV-252 at
  the line. `conformance.py since --since-last-audit` does not report it: `hosts/` is outside
  the corpus that view reads (audit finding 2, issue #9). The block below proposes the dated
  note on INV-252 that would bind the new wording and the record. Until the maintainer applies
  it, only the test holds them.

- **PROPOSED AMENDMENT to INV-252 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **(INV-252) Read the files from there. If `KIRO_HOME` is set and the bootcamp is not under it, look under `.kiro` in the user's home directory next.** — in `hosts/kiro/host.json`

  INV-252, as amended on 2026-11-16, requires a package to state where a skill's files are when
  the assistant gives no path. It does not say the stated location must hold on every platform
  the bootcamp supports, or that anything records what the location rests on. Without the note
  below, a later edit can put a Linux-only path back, or mark a platform `observed` with no
  run behind it, and contradict no registered rule. Enforced by
  `tests/test_kiro_skills_say_where_they_are.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-252** — (⚠️ **Amended 2026-11-16 (issue #11).** A location a package states for a skill's files MUST hold on every platform the bootcamp supports (INV-001). It MUST NOT rest on `~` alone, and where a setting of the assistant's own can move the directory, the location MUST be given inside a directory the note itself defines. On Kiro that directory is the Kiro home: the value of the `KIRO_HOME` environment variable when it is set, otherwise `.kiro` in the user's home directory (`%USERPROFILE%` on Windows), with the bootcamp at `powers/installed/senzing-bootcamp/` inside it. The assistant's `host.json` MUST record, for Linux, macOS and Windows each, whether the stated location is `observed`, `documented` or `unchecked`, with a source and a date unless it is `unchecked`; `observed` MUST name a run recorded in that assistant's `checks.json`, and `documented` MUST say that no run was observed. Enforced by `tests/test_kiro_skills_say_where_they_are.py`, which reads the note's wording and the record's shape and **cannot** establish where Kiro installs a Power on any platform: only a run there can, and on 2026-11-16 only Linux has one.)

- **Commit:** uncommitted

## the-since-last-audit-views-cannot-run-in-this-repository

- **Implemented:** 2026-11-16 (issue #10)
- **Files changed:** `.claude/skills/production-readiness-audit/conformance.py`,
  `specs/IMPLEMENTED.md` (the opening section and this entry),
  `tests/test_since_last_audit_falls_back_to_the_ledgers_commit.py`,
  `tests/test_all_runs_every_argument_free_view.py`,
  `tests/test_new_hard_rules_are_cited_or_deferred.py` (one docstring sentence)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16 against the change itself:
  it decides which commit a maintainer script measures from, and asserts nothing about Senzing.
  No absence claim is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** `conformance.py since --since-last-audit` and `reverse-check --since-last-audit`
  now resolve a range start in this repository and say where it came from.
  - **The fallback.** The opening section of this ledger states the fallback commit on a
    `- **Fallback commit:**` line. When no audit entry yields a commit here, `last_audit_ref`
    measures from it, exits 0 and prints one `FALLBACK` line on stdout naming the commit and
    every skipped entry with its reason. A ledger with no audit entry falls back the same way.
    A run that adds nothing still prints the line.
  - **One copy of the hash.** `conformance.py` holds no fallback hash. The opening section is
    everything above the first `## ` heading; a `Fallback commit:` line inside an entry is not
    read.
  - **An entry that resolves always wins**, including an older one behind a newer
    `uncommitted` one. Where an entry resolves, the output is byte-identical with and without
    the fallback line.
  - **The refusal.** With no fallback stated, a value that is not a hash, a hash that is not a
    commit here, or no ledger at all, both views exit 2, say on stderr what they read of the
    audit entries and of the fallback, and print no count.
  - **Decided here, because the issue leaves it open.** The fallback is measured from as
    stated: the `SUSPECT-REF` widening tests what an audit record's commit carries, and the
    fallback is not an audit record. For the commit stated today the result is the same either
    way, since it touches nothing under `source/`, `hosts/`, `site/` or `public/`. A fallback
    run prints the first-range `BOUNDARY` line.
  - **Already on `main`, not redone.** The issue's first scope item, recording `dc79183` in the
    `Commit:` field of `production-readiness-audit-2026-11-16`, landed in `eead1c6` (pull
    request #16). Verified on this branch before the work began.
  - **Measured on this branch, 2026-11-16.** Both views exit 0 and print
    `(ref dc79183 from ledger entry production-readiness-audit-2026-11-16)`. `since` reports 1
    line added since `dc79183`, the INV-427 rule, and `reverse-check` says `VERDICT: clean`.
    `since --ref` against the fallback commit reports 10 lines across 6 files.
  - **Tests.** The new module builds a throwaway repository with four commits and runs both
    views as subprocesses: 29 tests over the fallback, the ledger with no audit entry, the
    refusals, the entry that wins and the live ledger. A fallback report is compared byte for
    byte, from its `== ` header on, with the same view run with `--ref`, so the reverse
    check's verdict is the ordinary one. Negative controls, each run and then reverted: the
    script without the change (44 failures, 2 errors), without the `BOUNDARY` call (2
    failures), and reading the fallback from anywhere in the ledger (2 failures).
    `test_all_runs_every_argument_free_view.py` accepts the `FALLBACK` line as a third outcome,
    keyed on the resolver's own line.
  - **Not changed.** `.claude/skills/production-readiness-audit/SKILL.md`: it is not in the
    issue's file list, and the `FALLBACK` line and the opening section above explain a
    fallback run where it happens.
- **Invariants.** The register is not edited here (INV-365). The change ships two hard-rule
  lines in a docstring, which `since` reports as outside its corpus. One block below covers
  both.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The since-last-audit views take their range start from the ledger alone, and say when it is the fallback. The rule already shipping, quoted:
    - ⛔ **The fallback commit is stated in the ledger's opening section and read from there.** — in `.claude/skills/production-readiness-audit/conformance.py`
    - ⛔ **A fallback run prints a FALLBACK line on stdout, every time, zero included.** — in `.claude/skills/production-readiness-audit/conformance.py`

  Enforced by `tests/test_since_last_audit_falls_back_to_the_ledgers_commit.py`.

  **Why it is not an existing invariant:** INV-308 requires a tool to say what it could not
  verify and to keep one definition of the scope it resolves against. It does not say where a
  range start comes from, that a fallback exists, or what a run measured from one must print.
  No registered invariant names the resolver, its `SUSPECT-REF` widening or its `BOUNDARY`
  report.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — `conformance.py`'s `--since-last-audit` views MUST take their range start from `specs/IMPLEMENTED.md` and from nowhere else: the newest audit entry whose `Commit:` names a commit in the repository and, only when no audit entry yields one, the commit on the `- **Fallback commit:**` line in the ledger's opening section. `conformance.py` MUST NOT hold a fallback hash of its own. A run measured from the fallback MUST print a `FALLBACK` line on stdout naming the commit and the audit entries it skipped, including a run that reports zero lines added, and is otherwise an ordinary run with the usual exit code and verdict. When the ledger states no fallback, or states one that is not a commit in the repository, the views MUST exit 2, say on stderr what they read, and print no count. Enforced by `tests/test_since_last_audit_falls_back_to_the_ledgers_commit.py`, which builds throwaway repositories and **cannot** establish that the commit the live ledger states is the right one to measure from; that is the maintainer's choice, recorded in GitHub issue #10. (Source: `the-since-last-audit-views-cannot-run-in-this-repository`, GitHub issue #10, 2026-11-16.)

- **Commit:** uncommitted

## invariant-review-2026-11-16-audit

**Not a spec** — the record of a second `/review-invariants` session on 2026-11-16, attended by
the maintainer.

- **Implemented:** 2026-11-16
- **Files changed:** `specs/INVARIANTS.md`, `specs/IMPLEMENTED.md`,
  `source/skills/bootcamp-onboarding/SKILL.md`, `tools/bootcamp_build/emit.py`,
  `hosts/kiro/host.json`, `tests/test_ground_rules_are_read_to_the_end.py`,
  `tests/test_invariant_enforcer_citations.py`, `tests/test_supersession_has_one_syntax.py`
- **MCP re-check:** n/a (no Senzing fact)
- **Summary:** One block was decided, from `production-readiness-audit-2026-11-16`. The
  maintainer chose to amend by splitting it, and approved both texts as shown.
  - **Registered:** INV-427, the read-to-the-last-line rule. Cited at the step that names the
    ground rules, and enforced by a new test that cites it back; the enforcer pair count was
    re-derived by the extractor, 349 to 350.
  - **Amended, still in force:** INV-252, with a dated note that it binds on every assistant
    and that a package states where a skill's files are when the assistant gives no path. The
    two notes the build appends to skills now cite INV-252.
  - **Why the split:** the audit's draft repeated INV-252 without weighing it. The review found
    the overlap before anything was minted.
  - **Held:** nothing new. The three earlier holds were not re-offered.
  - **Remains:** the queue is empty.
- **Establishes no invariant of its own** (INV-309): the id it registered and the one it
  amended were established by the entry named above and by INV-252's own source.
- **Commit:** uncommitted

## production-readiness-audit-2026-11-16

**Not a spec** — a dated record of an audit run, **attended**. It is the first audit in this
repository, after the move to one source for five assistants, the two Kiro fixes (#3), the
effort research (#5), the removal of the model and effort question (#4) and the 2026-11-16
invariant review.

- **Implemented:** 2026-11-16 (**7 findings recorded below; none fixed; six filed as #9 to
  #14 with the maintainer's yes; one unregistered rule queued as a deferral**)
- **Files changed:** this record only.
- **MCP re-check:** n/a (no Senzing fact). Every finding is internal consistency. No absence
  claim is made, so INV-213's `owner-checked:` clause is not owed.
- **Baseline.** `main` at `bfa4f8a`, tree clean.
  - **Suite green:** `Ran 9454 tests`, `OK (skipped=15)`, run on the identical tree at `9e71a30`
    before its merge; not re-run after the merge commit, whose tree is the same.
  - `citations.py verify` clean at 424 invariants; `bootcamp_build check` OK;
    `coverage_reports.py shipped` lists nothing.
  - Reachable here: `fpdf2`, `pdftoppm`, `docker`, Google Chrome. Not found: `chromium`.
- **Scope, chosen deliberately.** Not a full forward sweep. Swept: everything issue #4 and the
  invariant review touched, in all five built packages; the hard rules added to `source/` since
  the import commit `55971ad`; cross-references to the model page; live citations of the
  retired invariants; the install pages' model wording. Not swept: the per-module outcome
  blocks (INV-028 to INV-049), the 93 enumerating invariants, duplication and file size.
- **Verified correct.** No built package holds a leftover of the model and effort question. The
  retired invariants (INV-063, 069, 098, 138, 139) are cited in shipped text only where the
  ground rules say the nudge is retired. The welcome sentence renders in all five packages.
- **Findings, most serious first. All open.** Each carries its issue number; finding 1 is the
  deferral below.
  1. **Corrected 2026-11-16, at review.** This finding overstated the gap: INV-252 already
     forbids searching the filesystem for a bundled file, and `feedback.md` and
     `graduation/SKILL.md` already cited it. What was unregistered was the read-to-the-last-line
     rule and the extension of INV-252 to an assistant that gives no path. As first written:
     **Reverse contract: hard rules shipped with no invariant and no deferral.** #3 and commit
     `f7540ef` added four ⛔ rules on one subject, and neither wrote a block: the read-to-the-
     last-line rule in `bootcamp-onboarding/SKILL.md`, the two "never by searching" rules for
     the version and assistant lines in `feedback.md` and `graduation/SKILL.md`, and the
     never-search note the build appends to skills (`tools/bootcamp_build/emit.py`,
     `hosts/kiro/host.json`). Queued below as one deferral. This run's author wrote those
     changes and omitted the blocks.
  2. **The audit's own tools cannot see where assistants differ.** (#9) `conformance.py` reads
     `source/` and `.claude/` only. Rule text that reaches bootcampers from `hosts/*/fragments/`,
     `hosts/kiro/files/`, `hosts/kiro/host.json` and `tools/bootcamp_build/emit.py` is scanned by
     no view, and `pending_invariants.py sites` reports `hosts/` as not scanned.
  3. **`since --since-last-audit` and `reverse-check --since-last-audit` cannot run.** (#10) The newest
     audit entry before this one records `committed (hash not recorded)`, and its commit is in
     the archived repository. Both views stop with "no audit entry has a resolvable commit".
     This entry's commit gives the next run a range start.
  4. **Completeness, platforms (INV-001).** (#11) The Kiro package tells the assistant its files are at
     `~/.kiro/powers/installed/senzing-bootcamp/`. That path was observed on Linux only; nothing
     states or tests the location on macOS or Windows.
  5. **Consistency across assistants: a maintainer page ships in one package.** (#12)
     `docs/model-selection.md`, titled "maintainer notes", is in the Claude package and in no
     other. No shipped file refers to it, and it points at `docs/effort-mechanisms.md`, which no
     package carries.
  6. **Consistency: the install page and the welcome name different models on ChatGPT.** (#13) The
     install page says to choose GPT-5.6 Terra at Medium; the welcome says "a high-capability
     Codex model". The Claude install page also sets an effort, which the bootcamp otherwise
     never mentions; an install-time choice is allowed, but only two of five pages make one.
  7. **Coherence: the never-ask list names one assistant's controls in every package.** (#14) The
     ground rules list `/compact` and `/loop` among the controls never offered as a question, on
     all five assistants. Carried from the migration's open threads.
- **Concision:** not audited this run. The heaviest shipped file is
  `module-02-sdk-setup/SKILL.md` at 29,328 words; `ground-rules.md` is 18,764 words and is the
  file Kiro had to read in five pieces.
- **Coverage limits.** ⛔ The conversational invariants (INV-005, INV-006, INV-008, INV-009,
  INV-014, INV-251 and every gate ordering rule) were not tested; reading cannot establish them
  and they need `dry-run` phase 3. No assistant has run a bootcamp built from this `main`.
  Whether an assistant works more carefully on a "high" stage (INV-426) is unmeasured.

- **DEFERRED INVARIANT (resolved INV-427, registered by the maintainer 2026-11-16, after an amendment that split it).** The bootcamp reads its own files from where it is installed and to the end, and never searches the disk for them. The rule already shipping, quoted:
    - `source/skills/bootcamp-onboarding/SKILL.md:23` — ⛔ the ground rules are read to the last line, continuing after a read that was cut short *(covered: …)*
    - `tools/bootcamp_build/emit.py` — ⛔ the note appended to every command rendered as a skill says to read sibling skills from beside it and never to search the filesystem *(covered: …)*
    - `hosts/kiro/host.json` — ⛔ the note appended to every Kiro skill names its installed directory and forbids a wider search *(covered: …)*

  Enforced by `tests/test_kiro_skills_say_where_they_are.py` and `tests/test_bootcamp_build_hosts.py`.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **As registered, after the split.** The read-to-the-end half is INV-427, with the wording the
  maintainer approved in review. The never-search half was already INV-252, which this block
  failed to weigh; it went there as a dated note extending INV-252 to every assistant, and the
  two appended notes now cite INV-252. The original draft is kept below as the record.

  **INV-NNN** — Where an assistant gives the guide a skill's text without its location, the package MUST state where that skill's files are, and the guide MUST read a bootcamp file from the running package's own location and MUST NOT search the filesystem for one, because a second copy of the bootcamp on the same machine is normal. A file the bootcamp tells the guide to read in full MUST be read to its last line, continuing after a read that was cut short.

- **Commit:** dc79183

## invariant-review-2026-11-16

**Not a spec** — the record of a `/review-invariants` session, attended by the maintainer.

- **Implemented:** 2026-11-16
- **Files changed:** `specs/INVARIANTS.md`, `specs/IMPLEMENTED.md`,
  `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/bootcamp-onboarding/onboarding-flow.md`, `tests/test_invariants_index.py`,
  `tests/test_invariant_enforcer_citations.py`, `tests/test_supersession_has_one_syntax.py`,
  `tests/test_coverage_reports.py`, `tests/test_working_depth_by_stage.py`,
  `tests/test_model_guidance_behavior.py`, `tests/test_welcome_names_one_model_once.py`
- **MCP re-check:** n/a (no Senzing fact)
- **Summary:** Nine blocks were decided, all from
  `adjust-effort-automatically-instead-of-asking-the-bootcamper` (issue #4), each on its own yes.
  - **Registered:** INV-426, as drafted and as one invariant. Cited at both rules in the ground
    rules and at the welcome's "said once" rule, and cited back by its three enforcing tests;
    the enforcer pair count was re-derived by the extractor, 346 to 349.
  - **Fully superseded by INV-426:** INV-063, INV-069, INV-098, INV-138 and INV-139. Each
    carries a dated note and a `Superseded by` marker, and the index lists it as fully
    superseded.
  - **Narrowed:** INV-137. Its nudge clauses went to INV-426; the no-preference rule still
    binds. The maintainer approved one clause added to the draft, that a stale `model_guidance`
    value is ignored.
  - **Amended, still in force:** INV-141 (one effort level per row and no model) and INV-247
    (the model and effort exception is withdrawn).
  - **Wording changed from the drafts, with the maintainer's yes:** each retiring note opens
    "Fully superseded 2026-11-16 (issue #4): superseded by INV-426", because the index guard
    reads a supersession only in that form.
  - **Guard changed:** `tests/test_invariants_index.py` now treats a dated "fully superseded"
    note as overriding an earlier restoration. INV-063 and INV-069 say INV-137 "restores this",
    and the register is append-only, so without it they could never leave the partly
    superseded list.
  - **Markers added so each supersession reads both ways:** `Supersedes` under INV-426 for the
    five it retires, and `Partly superseded by: INV-426` under INV-137.
  - **Two more guards adjusted:** `tests/test_supersession_has_one_syntax.py` records INV-141
    and INV-247 as amended and not superseded, and drops INV-138 from its reviewed list now that
    it carries a marker. `tests/test_coverage_reports.py` reads only index lines when it looks
    for partly superseded ids, since an entry's own marker can name a rule retired later.
  - **Held:** nothing new. The three earlier holds were not re-offered; none of their revisit
    conditions was met.
  - **Remains:** the queue is empty. Stale in wording only, with no block written: INV-086,
    INV-096, INV-102, INV-114, INV-140, INV-158, INV-236 and INV-420 mention the retired nudge
    or the model column in passing, and INV-236 has no shipped site left to bind.
- **Establishes no invariant of its own** (INV-309): every id it registered or amended was
  established by the entry named above.
- **Commit:** uncommitted

## adjust-effort-automatically-instead-of-asking-the-bootcamper

- **Implemented:** 2026-11-16 (issue #4)
- **Files changed:** `source/skills/` (ground rules, onboarding flow, Bootcamp preparation,
  graduation, every module), `source/scripts/module_start_apparatus.py`,
  `source/scripts/module-start-reminder.py`, `source/hooks/`, `source/docs/model-selection.md`,
  `source/docs/examples/`, `hosts/` (both `model-guidance.md` fragments deleted; every
  `host.json`, `interface-naming.md` and `site-tips.html`; Claude's `site-install.html`),
  `docs/effort-mechanisms.md`, `.claude/skills/auto-test/`, `.claude/skills/dry-run/`, `tests/`
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16: the change is about how the
  guide works and what it asks about the assistant, and asserts nothing about Senzing.
- **Summary:** The bootcamp no longer recommends a model or a reasoning effort at a module or
  graduation start and no longer asks the bootcamper to change either. The switch question, its
  step-down wording and the "Are you done modifying the model and effort?" gate are gone on every
  assistant. The welcome names the assistant's capable-tier model once, as a statement. The
  ground rules carry one table, "Working depth by stage", with one effort level per stage and one
  fixed instruction per level, applied silently and identical in all five packages; nothing the
  bootcamp ships sets a model or an effort. The host values `model_balanced`, `model_top` and
  `model_controls` are removed. The model-selection page and the site tips say one model is fine
  throughout. `docs/effort-mechanisms.md` now recommends instructions only, because a skill's
  effort setting on Claude lasts one turn and a module runs for many. The auto-test walker no
  longer answers a switch question, and its transcript lint reports one as a finding.
  Tests: the nudge's tests are replaced by `test_working_depth_by_stage`,
  `test_welcome_names_one_model_once`, `test_model_docs_name_no_switch` and rewritten
  `test_model_guidance_behavior`, `test_bootcamp_build_guidance_parity` and
  `test_model_guidance_sync`.
- **Invariants.** The register is not edited here (INV-365). The change contradicts eight
  invariants in force; each has a block below. Also stale in wording only, with no block:
  INV-086, INV-096, INV-102, INV-114, INV-140, INV-158, INV-236 and INV-420 mention the nudge or
  the model column in passing, and INV-236 has no shipped site left to bind.

- **DEFERRED INVARIANT (resolved INV-426, registered by the maintainer 2026-11-16).** The bootcamp never asks for a model or effort change, and effort follows the stage by instruction. The rule already shipping, quoted:
    - ⛔ **(INV-426) It changes no setting.** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **(INV-426) Apply the instruction silently.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  Enforced by `tests/test_working_depth_by_stage.py`, `tests/test_model_guidance_behavior.py` and
  `tests/test_welcome_names_one_model_once.py`.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — The bootcamp MUST NOT ask the Bootcamper to change the model or the reasoning effort, MUST NOT change either itself, and MUST NOT ship anything that sets either. Every stage the bootcamp can run MUST have exactly one effort level in the "Working depth by stage" table, each level MUST map to exactly one instruction to the guide, the table and instructions MUST be identical in every assistant's package, and the guide MUST apply them without showing or mentioning them. The welcome MUST name one suitable model exactly once, as a statement.

- **PROPOSED AMENDMENT to INV-063 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no module-start model or effort question.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-063 requires the model and effort recommendation and its switch question at every module and graduation start. Issue #4 removes both, so the register describes a question the bootcamp no longer asks.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-063** — *Superseded 2026-11-16 (issue #4).* The bootcamp no longer surfaces a model or effort recommendation at a module or graduation start and asks no switch question. How carefully the guide works is set by instruction ("Working depth by stage"), and the welcome names one suitable model once.
- **PROPOSED AMENDMENT to INV-069 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no module-start model or effort question.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-069 pins the confirmation gate that followed an accepted switch. With no switch question there is no yes for it to follow.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-069** — *Superseded 2026-11-16 (issue #4).* The "Are you done modifying the model and effort?" gate no longer exists, because the switch question it followed no longer exists.
- **PROPOSED AMENDMENT to INV-098 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no module-start model or effort question.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-098 makes the nudge adapt to the Claude interface in use. There is no nudge to adapt.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-098** — *Superseded 2026-11-16 (issue #4).* No model or effort nudge is presented in any interface. Naming the interface for any other control stays under INV-158.
- **PROPOSED AMENDMENT to INV-137 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no module-start model or effort question.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-137's first half says model and effort guidance is unconditional. The guidance is gone; only the second half still holds, and shipped text still cites it for that.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-137** — *Narrowed 2026-11-16 (issue #4).* There is no module-start model or effort guidance to be unconditional about. What remains in force: the Bootcamper is never asked how they want model or effort handled, and there is no `model_guidance` preference.
- **PROPOSED AMENDMENT to INV-138 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no module-start model or effort question.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-138 says how the nudge decides whether to ask. Nothing is compared and nothing is asked.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-138** — *Superseded 2026-11-16 (issue #4).* No comparison is made between a recommendation and the running model or effort, and no question follows from one.
- **PROPOSED AMENDMENT to INV-139 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no module-start model or effort question.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-139 words the step-down case of the switch question. The question no longer exists.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-139** — *Superseded 2026-11-16 (issue #4).* There is no switch question, so there is no step-down wording.
- **PROPOSED AMENDMENT to INV-141 — applied 2026-11-16 by the maintainer.**
    - ⛔ **Working depth by stage.** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-141 requires each per-stage row to name exactly one model and one effort. The table has no model column.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-141** — *Amended 2026-11-16 (issue #4).* A per-stage row names exactly one effort level and no model. A conditional or two-branch level stays forbidden.
- **PROPOSED AMENDMENT to INV-247 — applied 2026-11-16 by the maintainer.**
    - ⛔ **There is no exception:** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-247 forbids presenting a session-level control as a bootcamp question, with one exception: the module-start model and effort switch. The exception is removed, so the prohibition has none.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-247** — *Amended 2026-11-16 (issue #4).* The model and effort exception is withdrawn. The bootcamp asks the Bootcamper to operate no assistant-interface control at all.
- **Commit:** uncommitted

## research-how-each-assistant-can-adjust-reasoning-effort

- **Implemented:** 2026-11-16 (issue #5)
- **Files changed:** `docs/effort-mechanisms.md`, `tests/test_effort_mechanisms_covers_every_assistant.py`
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16: the change is research
  about AI assistants and asserts nothing about Senzing.
- **Summary:** `docs/effort-mechanisms.md` records, for each of the five assistants, whether a
  package can change the main session's reasoning effort, whether a helper agent can run at a
  chosen effort, the effect on the conversation cache, the source and what was not verified.
  Claude Code 2.1.325 was checked live: a skill's `effort:` frontmatter applied for its turn, a
  plugin agent ran at its own effort, and the conversation cache was kept. Copilot CLI 1.0.112
  was checked live: a plugin agent's documented `reasoningEffort` was not applied. Kiro, Codex
  and Antigravity are from documentation only; no mechanism was found for Kiro, so the Kiro live
  check the issue allows for was not needed. The file recommends, for issue #4, instructions on
  every assistant plus the skill `effort:` setting on Claude only. The test checks that every
  assistant under `hosts/` has exactly one row, that each row says how it was verified and that
  the file ends with a recommendation.
- **Establishes no invariant** (INV-309): the file is a dated research record, and the test
  guards its coverage, not a rule of the bootcamp.
- **Commit:** uncommitted

## one-development-repository-for-every-assistant

- **Implemented:** 2026-11-14
- **Files changed:** `source/`, `hosts/`, `tools/bootcamp_build/`, `site/`, `tests/`, `specs/`, `.claude/`
- **MCP re-check:** n/a (no Senzing fact)
- **Summary:** The bootcamp is one host-neutral source, `source/`, imported from
  `docktermj/senzing-bootcamp-claude-plugin-development` at commit `195c17dc` (0.7.0 plus 320
  commits). A build writes each assistant's package from it, and the Claude package built at
  import was identical to the plugin at that commit, file for file. The invariant register,
  the declined-work record and the MCP coverage ledger came with it. The spec archive, the
  earlier ledger, `BLUEPRINT.md` and the family workflow document stayed in the old repository.
- **Establishes no invariant of its own** (INV-309).
- **Commit:** uncommitted

<!-- The three entries below were carried from the archived ledger on 2026-11-14, by the
maintainer's decision, because each holds an invariant draft that is still on hold with a
revisit condition. Four other held drafts were left in the archive: the maintainer had
already decided each needs no invariant of its own. -->

## production-readiness-audit-2026-10-22

**Not a spec** — a dated record of an audit run, **attended**. It follows the 2026-10-12 audit (`aecbc38`) and roughly 300 commits since: the #530–#757 fixes, the 2026-10-13 to 2026-10-22 `/review-invariants` sessions (INV-360 to INV-410), and #770's review-queue change.

- **Implemented:** 2026-10-22 (**63 distinct findings, filed in 23 root-cause groups as #776–#798; 4 unregistered rules queued as deferrals and 6 invariant corrections queued as amendments below; no shipped file modified by this audit**)
- **Files changed:** this record only.
- **MCP re-check:** server `sz-mcp-coworker` **1.39.1**, docs index 2026-10-15 22:11 UTC, 2026-10-22. Two filed groups assert a Senzing fact, and each was re-asked this session:
  - #789 — **server now contradicts the plugin**: `search_docs(query='temporary evaluation license for a dataset larger than the default limit')` returns `eval_license.message` "Need a Senzing license to try this? Open Ask Senzing — the assistant pop-up on https://docs.senzing.com — and just ask it for a free evaluation license; it will give you one.", while Module 6 Phase A hardcodes `support@senzing.com`.
  - #792 — **still reproduces**: `get_capabilities` describes `get_sample_data` record retrieval through the Connectors Directory as possibly "filtered at the platform layer with a 'Denied.' response"; `get_sample_data(dataset='list')` returned the four datasets unfiltered, so the exposure is record retrieval, not listing.
  - Every other finding is internal consistency. ⚠️ No absence claim is made, so INV-213's `owner-checked:` clause is not owed.
- **Baseline.** `main` at `b7085c53`, tree clean.
  - **Suite green:** `Ran 8446 tests`, `OK (skipped=13)` (unittest).
  - `citations.py verify` clean at **408** invariants.
  - `rules`: **835** hard-rule lines (569 line-anchored + 266 mid-line), **0** in a section citing no invariant. `per-rule`: **291** citing no invariant at the rule. `enumerations`: **83 of 408**. `size`: 45 shipped files, **270,059** words. `duplication`: 245 repeated passages across 163 file pairs.
  - `since --since-last-audit` resolved to **`aecbc38`** (the 2026-10-12 entry), no `SUSPECT-REF`: **173** hard-rule lines (130 plugin, 43 maintainer surface).
  - `reverse-check`: **TESTED 130 (129 cited, 1 not)**, **UNTESTED 43 (34 cited, 9 not)**, **VERDICT: NOT CLEAN**. The one uncited tested line is `phaseD-validation.md:755`, whose INV-404 citation this run's own session placed at the sentence end on 2026-10-22 (#787).
  - `pending_invariants.py list`: 0 pending, 6 held; the next free id is **411** — written as a bare number deliberately; read it off `INVARIANTS.md` at mint time.
  - **Zero open issues** at the start of the run, so no finding is a duplicate.
  - Environment: fpdf2 2.8.5, `pdftoppm`, `docker`, `google-chrome` and `libSz.so` present.
- **Scope, stated rather than implied.** Four read-only sweeps run in parallel; the lead re-checked every high and medium finding at its site before filing.
  - **(A)** The reverse contract: all 173 lines `since` reports, each classified (153 cited correctly, 10 wrongly, 6 partially, 2 deferred-in-effect, 1 unregistered, 1 not a durable rule), plus about 60 of the 587 citing lines added to `plugins/` since `aecbc38`, spot-checked for mis-attachment.
  - **(B)** The forward contract for INV-360–INV-410 (id 385 was never minted) and the 66 dated notes added since `aecbc38` on 38 older invariants, at every site each binds, with each guard read against its text.
  - **(C)** The per-module outcome blocks the previous audit did not read: Modules 0, 1, 4 and 7, bootcamp-onboarding and graduation, read in full, with every Markdown link and quoted section pointer resolved by script.
  - **(D)** About 30 of the 83 enumerating invariants checked against what ships (subjects changed since `aecbc38` first), 22 of 57 duplication groups read side by side, and the maintainer surface changed since `aecbc38`.
  - ⚠️ **Modules 2, 3, 3b, 5 and 6 were read only where a sweep's lines or invariants led there.** About 42 enumerating invariants (mostly MCP and SDK contract enumerations) were not checked and need an MCP re-check.
- **Findings, filed.** No issue carries any label (INV-318).
  - **High:** #776 (Phase D routes a never-computed UAT % to the strong branch; Module 5 step 16's gate is untotal; INV-404), #777 (the INV-146 #671 and INV-079 #683 amendments marked applied but absent from the registry).
  - **Medium:** #778 (the review queue's decision words match a negated word; INV-409, introduced by #770 in this run's own session), #779 (Module 4 generation size), #780 (Module 4 Step 8a's license gate), #781 (Module 7 gate item 6 and Discover exits), #782 (`current_module` timing), #783 (external feedback sharing), #784 (registry sample shape), #785 (Module 1 Step 10a values), #786 (native-Windows build and run), #787 (wrong and off-line citations, INV-396), #788 (INV-408 clipping in the rich renderer and the video), #789 (Phase A's license channel, INV-403), #790 ("your data", INV-399), #791 (INV-394 and INV-393 at sibling sites), #792 (INV-378 and INV-160 at sibling sites), #793 (INV-401 and INV-370 at Module 5 and Module 4), #794 (auto-test walk failure and isolation), #795 (INV-402's rebuild and CORD fields).
  - **Low:** #796 (guards narrower than their invariants), #797 (maintainer-surface stale claims and restatements), #798 (cross-reference and wording defects).
- **Verdicts.** **Consistent:** no — Module 4 contradicts itself on generation size (#779), Module 1 and Module 4 disagree on the license gate (#780), the registry sample's shape (#784), and two "applied" amendments disagree with the registry (#777). **Coherent:** no — a gate routes a never-established reading to the strong branch (#776), `current_module` is decided before the choice it records (#782), and Module 7's gate asks after a no-question close (#781). **Complete:** no — native-Windows build and run (#786), five rules honored in Modules 2 and 3b only (#791, #792), and unregistered rules (below). **Concise:** unchanged; the generation-size rule sits about 290 lines below the action it governs (#779), and the error-handling block is restated across eight skill files (#798).
- **Verified as correct, so the next audit need not re-check it.** INV-400 to INV-410 are cited on their rules' lines except INV-404 at `:755` (#787); all 31 INV-366 sites; INV-225, INV-264, INV-393 and INV-394 at their Module 2 and 3b sites; INV-360, 362, 363, 364, 366, 368, 369, 371, 372, 374, 375, 377, 379–383, 387, 388, 390–392, 395–398, 407, 409 (live ledger) and 410 fully honored; the INV-050 notes #616, #618, #685 and #686; every quoted section pointer in Modules 0, 1, 4 and 7, onboarding and graduation; every enforcer path named in `INVARIANTS.md` exists.
- ⚠️ **Coverage limits.** The conversational invariants (INV-251, INV-006, INV-014, INV-005/008/009 and every gate-ordering rule) govern a live turn and were **not tested**; they need `dry-run` phase 3. #786's native-Windows route and #794's isolation question rest on behavior this environment cannot exercise (a Windows shell; how Claude Code loads `./.claude/CLAUDE.md`).
- ⚠️ **This run's own mistakes, reported.** Two of its findings are defects the same session introduced earlier that day: #770's decision-word pattern (#778) and the INV-404 citation placed at a sentence end (#787).
- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The recap renderer draws a Markdown subset, and a diagram is referenced from the recap, never embedded. The rule already shipping, quoted:
    - ⛔ **Do not embed the Mermaid source into `docs/bootcamp_recap.md`.** — in `source/skills/module-01-business-problem/phase2-document-confirm.md`

  **Why it is not an existing invariant:** the `IMPLEMENTED.md` block for INV-389 quotes this line as "a pre-existing rule, and NOT the one being deferred … no registered invariant governs the recap renderer's Markdown subset"; INV-091 governs offline rendering, not what the recap may contain; INV-142 governs how a construct is drawn once it is present.

  The drafted wording:

  **INV-NNN** — Content written into `docs/bootcamp_recap.md` MUST stay within the Markdown subset the bundled recap renderer draws (headings, bullets, `**Label:**` lines, plain text, `![alt](path)` images); a diagram or other fenced block MUST be referenced from the recap by path, never embedded, because a construct the renderer does not handle reaches the PDF as literal source text. Enforced by no test today; `conformance.py reverse-check` counted the line as cited because INV-091 sits in the sentence before it.

  *(written as NNN deliberately: this command cannot mint an id, and a literal id here would cite an invariant that does not exist and turn `citations.py verify` red. If the maintainer registers it, mint at the next free id — read it off `INVARIANTS.md` rather than trusting a number written here.)*

  **HELD 2026-10-22:** the maintainer held it at review: no test enforces the rule, and the drafted wording lists the renderer's Markdown subset, which can go stale. Revisit when a test enforces the rule and `generate_recap_pdf.py` states its supported subset in one place the invariant can point to.
- **DEFERRED INVARIANT (resolved INV-271, folded in at review 2026-10-22 as a dated note on the invariant it extends rather than minted as a new id).** Graduation offers to re-capture a missing visualization before rendering the recap. The rule already shipping, quoted:
    - ⛔ **(INV-193) Offer the remedy — it is cheap while the artifacts are still on disk.** — in `source/skills/graduation/SKILL.md`

  **Why it is not an existing invariant:** INV-193 governs where an external denominator comes from; INV-271 governs reporting a missing manifest. Neither says to offer a re-capture (#787 re-cites the line).

  The drafted wording:

  **INV-NNN** — When graduation's coverage check reports an expected visualization with no capture manifest, graduation MUST offer to re-start that module's app and re-run the bundled capture, then backfill the recap, before rendering it; declining MUST NOT block graduation.

  *(written as NNN deliberately: this command cannot mint an id, and a literal id here would cite an invariant that does not exist and turn `citations.py verify` red. If the maintainer registers it, mint at the next free id — read it off `INVARIANTS.md` rather than trusting a number written here.)*
- **DEFERRED INVARIANT (resolved INV-411, registered by the maintainer 2026-10-22, after an amendment).** Module Completion's recap structural check never blocks completion, and a check that cannot run is recorded. The rule already shipping, quoted:
    - ⛔ **Non-blocking and Bootcamper-invisible (INV-012).** — in `source/skills/bootcamp-onboarding/module-completion.md`

  **Why it is not an existing invariant:** INV-012 covers invisibility only; the non-blocking clause lost its INV-048 credit in `589a18d0` (#685), and no invariant states that the per-module `--check` never blocks. The same line says "If the script is missing or fails to execute, continue silently", which sits uneasily with INV-163 ("a verification check that cannot run … MUST be recorded as skipped").

  The drafted wording:

  **INV-NNN** — Module Completion's recap structural check MUST NOT block module completion: a finding is corrected in the just-appended recap section, and the module completes whether or not the check finds anything or can run. How an unrunnable check is reported is INV-163's to govern, not this invariant's. No test enforces it today.

  *(written as NNN deliberately: this command cannot mint an id, and a literal id here would cite an invariant that does not exist and turn `citations.py verify` red. If the maintainer registers it, mint at the next free id — read it off `INVARIANTS.md` rather than trusting a number written here.)*
- **DEFERRED INVARIANT (resolved INV-412, registered by the maintainer 2026-10-23, after an amendment).** Which module may write a source's `record_count`. The rule already shipping, quoted:
    - ⛔ **`record_count` stays the measured count:** — in `source/skills/module-04-data-collection/SKILL.md`

  **Why it is not an existing invariant:** the line cites INV-243, which governs reconciling a per-source figure shown to the Bootcamper, not who writes the field; INV-326 comes closest, for samples; INV-402 governs the registry entry's existence (#787 re-cites the line).

  The drafted wording:

  **INV-NNN** — A source's top-level `record_count` in `config/data_sources.yaml` MUST be written only by the module that collects or generates the source file and counts it (Data collection), as the measured count; no earlier module writes it, and it stays null until measured. A sample's or subset's own `record_count` is INV-326's, not this invariant's. No test enforces it today.

  *(written as NNN deliberately: this command cannot mint an id, and a literal id here would cite an invariant that does not exist and turn `citations.py verify` red. If the maintainer registers it, mint at the next free id — read it off `INVARIANTS.md` rather than trusting a number written here.)*
- **PROPOSED AMENDMENT to INV-094 — applied 2026-10-23 by the maintainer.**
    - (a) a database backup under the reserved top-level `backups/` directory (a `pg_dump` for PostgreSQL — via `docker exec` when the database runs in a container — or a file copy of the SQLite repository) — in `specs/INVARIANTS.md`

  The shipped backup runs `<runtime> exec` (`graduation/database-backup.md:47-49`), as INV-195's 2026-10-15 (#613) note requires, and that note forbids `docker exec` in shipped skills; INV-050's 2026-07-26 clarification removed "reserved" from `backups/`. **What breaks if it does not change:** a later edit can restore `docker exec` and cite INV-094 as permission.

  **INV-094** — (⚠️ **Dated note, 2026-10-22 (production-readiness-audit-2026-10-22): the container command and the directory's status; the bundle's contents are unchanged.** A PostgreSQL backup in a container runs through the recorded container runtime (`<runtime> exec`, INV-195), never a hard-coded `docker exec`, and `backups/` is a top-level directory without the "reserved" status INV-050's 2026-07-26 clarification removed. The rules above still bind.)
- **PROPOSED AMENDMENT to INV-059 — applied 2026-10-23 by the maintainer.**
    - never rewriting a completed `## Module N:` section — in `specs/INVARIANTS.md`

  Recap sections are now name-based, `## {Name} — {timestamp}` (`module-completion.md:78`; the example recap), and `recap_checkpoint.py` protects `## {module}` sections. The property holds; the literal heading is stale.

  **INV-059** — (⚠️ **Dated note, 2026-10-22 (production-readiness-audit-2026-10-22): the protected heading is the module's named section; the property is unchanged.** "A completed `## Module N:` section" reads as a completed module section, headed `## {Name} — {timestamp}` since module numbers left bootcamper-facing text (INV-079). The rules above still bind.)
- **PROPOSED AMENDMENT to INV-093 — applied 2026-10-23 by the maintainer.**
    - at the start of Data collection (Module 4), after the Bootcamper's data volume is known and before any load — in `specs/INVARIANTS.md`

  The prompt runs at Data collection Step 8a, after all sources are collected (`module-04-data-collection/SKILL.md:1241-1242`; `onboarding-flow.md:185-187`), not at the start of the module. `module-01-business-problem/phase1-discovery.md:414` and `module-02-sdk-setup/SKILL.md:1737` repeat "at the start".

  **INV-093** — (⚠️ **Dated note, 2026-10-22 (production-readiness-audit-2026-10-22): where in Data collection the prompt runs; the once-only rule and its conditions are unchanged.** "At the start of Data collection" reads as Data collection Step 8a, after every source is collected and its volume measured, and before any load. The rules above still bind.)
- **PROPOSED AMENDMENT to INV-047 — applied 2026-10-23 by the maintainer.**
    - A banner is presented, "GRADUATION". — in `specs/INVARIANTS.md`

  Graduation ships "BOOTCAMP GRADUATION" (`graduation/SKILL.md:47`, renamed 2026-08-12 in `3017e0e2`); no invariant records the rename.

  **INV-047** — (⚠️ **Dated note, 2026-10-22 (production-readiness-audit-2026-10-22): the banner's text.** The banner reads "BOOTCAMP GRADUATION" since 2026-08-12 (`3017e0e2`). The rule above still binds.)
- **PROPOSED AMENDMENT to INV-102 — applied 2026-10-23 by the maintainer.**
    - after the GRADUATION banner and before the model/effort prompt it presents a journey map (all selected modules shown ✅ experienced, Graduation 🔄 as the current/final stage — in `specs/INVARIANTS.md`

  The shipped banner and journey-map label are "BOOTCAMP GRADUATION" and "Bootcamp graduation 🔄" (`graduation/SKILL.md:47`).

  **INV-102** — (⚠️ **Dated note, 2026-10-22 (production-readiness-audit-2026-10-22): the banner and stage names.** "The GRADUATION banner" reads as the BOOTCAMP GRADUATION banner, and "Graduation 🔄" as "Bootcamp graduation 🔄", since 2026-08-12 (`3017e0e2`). The rules above still bind.)
- **PROPOSED AMENDMENT to INV-317 — applied 2026-10-23 by the maintainer, amended at review.**
    - It ships today in `/dry-run` (its command, skill and phase 3) and in `/production-readiness-audit` (its command and Step 8, which says to follow dry-run's discipline). — in `specs/INVARIANTS.md`

  The rule also ships in `/auto-test`, `/feedback-to-issues`, `/retrofit-from-public`, `/delegate-to-mcp-server` and `/release-cycle`, so the enumeration is stale.

  **INV-317** — (⚠️ **Dated note, 2026-10-22 (production-readiness-audit-2026-10-22): the sites are every maintainer run that produces findings; the rule is unchanged.** The list above is a sample taken when the rule was registered; the rule binds every maintainer run that produces findings, whatever skill runs it. The rules above still bind.)
- **Establishes no invariant of its own.** This audit modifies no shipped or maintainer-surface file beyond this record, so it adds no hard-rule line. It queues 4 new invariants and 6 amendments above for `/review-invariants` (INV-365); the maintainer runs it to decide them.
- **Commit:** committed (hash not recorded)
- **Archive commit:** ee4788d (a commit of the archived repository; see `specs/README.md`)

## open-me-first-says-only-what-the-manifest-includes

- **Implemented:** 2026-10-01 (**Not a spec** — a dated record of one issue-driven run, #321, spec revision 1; source: `/dry-run` 2026-10-01 phase 2, P2-1, `Source: self-observed (assistant dry run)`)
- **Commit:** uncommitted
- **Files changed:** `source/scripts/package_bootcamp.py` (`open_me_first()` and new helpers `included_parts()`, `_share_block()`, `_transfer_block()`, `_restore_step()`, `_para()`, `_series()`), `source/skills/bootcamp-onboarding/packaging.md` (Step 4's `OPEN_ME_FIRST.md` bullet), `source/skills/graduation/database-backup.md` ("Restore" opening sentence), `tests/test_open_me_first_matches_the_manifest.py` (new), `specs/IMPLEMENTED.md`. `specs/INVARIANTS.md` and `invariant-manifest.json` are unchanged.
- **MCP re-check:** n/a (no Senzing fact), server `sz-mcp-coworker` 1.37.16 (Senzing "current"), 2026-10-01, `get_capabilities`. Re-confirmed, not assumed: the change is the packager's own text about its own archive. The restore steps it now prints (copy a SQLite file back to `database/`; `pg_restore`, or `psql <` for a plain dump, into a fresh database) are SQLite and PostgreSQL steps already stated in `graduation/database-backup.md`, quoted from there, not Senzing facts. No absence claim is made, so no `owner-checked:` is owed. Nothing is upstream-bound.
- **Approach:** implemented directly (Phase 5a). The change is one function and its tests in one script, plus two one-sentence doc edits.
- **Summary:** `OPEN_ME_FIRST.md` now says only what `PACKAGE_MANIFEST.json`'s `included` list carries. Before, its "Start here" and "What this package is" sections were static text. A pre-graduation `transfer` package told the recipient it carried "the revisit bundle (state snapshot and database backup)" and to open `docs/REVISIT_BOOTCAMP.md`, when neither was in the archive.
  - **Parts.** `included_parts()` reads the manifest's posix paths only, never the disk, per the issue's table: the recap PDF, a database backup (under `backups/revisit/database/`), a state snapshot (`RESUME_STATE.json` or `backups/revisit/state/`), the restore guide, `config/`, `docs/mapping/`, `src/`, keepsakes (a `.pdf` directly under `docs/`), visualizations and `production/`.
  - **Complete package.** With every part included, the text is byte-identical to the old static text: prose is wrapped at 85 columns, which reproduces the original line breaks. This was checked against the pre-change function on `tests/test_package_bootcamp.py`'s fixture for both profiles.
  - **Start here.** Without the recap PDF, it says the recap PDF is written at graduation and is not in this package, and points at the manifest's `included` list.
  - **Transfer, partial.** It says the package is partial, lists what it carries and what it does not. Then: with the guide, the "To resume" pointer, plus "no database backup" when there is none. With a backup and no guide, each backup's path and its restore step by file type (SQLite, `.dump`, or the path alone), and that no full restore guide is included. With neither, that the recipient must redo SDK setup, the database and the load.
  - **Share, partial.** The keepsakes, visualizations and `production/` are each named only when included.
  - **Docs.** `packaging.md` Step 4 and `database-backup.md` "Restore" now describe the recap-PDF and restore-guide pointers as conditional.
  - **Tests.** `tests/test_open_me_first_matches_the_manifest.py`, 20 tests, stdlib only, loading the script as `tests/test_package_bootcamp.py` does. One fixture per acceptance case: no bundle and no guide, everything, database only, restore step by file type, guide without a backup, present but excluded (secret pattern and unreadable), recap PDF in both profiles, each share part. Each case also checks the issue's rule that every path the contents sections name is in `included`. Each partial case's predicate is also run against a static stand-in (the real function fed a complete package's `included` list) and must fail there. Replacing `open_me_first()` with the pre-#321 static function fails 13 tests. `test_open_me_first_points_at_the_restore_guide` is unchanged and passes.
- **Verification:** the verdict lines of both CI legs (empty `HOME` outside `/tmp`) and of `citations.py verify` (run after this entry was written) are in the PR. `lint-workflows` was not run locally, because it is a remote reusable workflow and no workflow file changed.
- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** `OPEN_ME_FIRST.md` says only what the manifest includes. The rule already shipping, quoted:
    - ⛔ **Included means "listed in ``included``", never "exists on disk"** — in `source/scripts/package_bootcamp.py` (`included_parts()` docstring) — **cite INV-NNN**

  **Every site a citation must reach:** the docstring above; `open_me_first()`'s docstring in the same file; and `packaging.md` Step 4's `OPEN_ME_FIRST.md` bullet, which states the conditional pointers. **Checked, not a site:** `graduation/database-backup.md` "Restore" names the condition but states no rule of its own.

  ⚠️ **Why a new id, and why it may wait.** The packaging feature's own invariant, Draft 1 of 2 in `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md`, is HELD until `dry-run` phases 2 and 3 have exercised the flow. It says the manifest names what was included and excluded, and says nothing about what `OPEN_ME_FIRST.md` claims. Phase 2 of the 2026-10-01 dry run found exactly that gap. The maintainer may fold this wording into Draft 1 when registering it, or hold it with Draft 1.

  The drafted wording:

  **INV-NNN** — Every statement `OPEN_ME_FIRST.md` makes about what a package contains MUST be built from `PACKAGE_MANIFEST.json`'s `included` list, never from what exists on disk or from static text, so the two can never disagree. Every path it names as included MUST appear in that list. A part that is not included (the recap PDF, the database backup, the state snapshot, the restore guide, `config/`, the mappings, `src/`, the keepsakes, the visualizations, `production/`) MUST NOT be named as included, and the text MUST say plainly what is missing and what the recipient does instead: open the manifest's `included` list when there is no recap PDF; restore a backup by its file type when there is no restore guide; redo SDK setup, the database and the load when there is neither a backup nor a guide. The pointer to `docs/REVISIT_BOOTCAMP.md` MUST appear only when that file is included. Enforced by `tests/test_open_me_first_matches_the_manifest.py`. (Source: GitHub issue #321.)
  *(written as NNN deliberately: a literal id here would cite an invariant that does not exist and turn `citations.py verify` red. If the maintainer registers it, mint at the next free id — read it off `INVARIANTS.md` rather than trusting a number written here.)*

  **HELD 2026-10-02:** held with the packaging feature's Draft 1
  (`the-bootcamp-cannot-leave-the-machine-it-was-built-on`, held 2026-08-27), whose manifest rule this
  extends to `OPEN_ME_FIRST.md`. The 2026-10-01 dry run's phase 2 exercised packaging and found this
  gap; phase 3 has not yet exercised it. Revisit with Draft 1 once `dry-run` phase 3 has exercised
  packaging, and register the two together or fold this into it.

- **Otherwise establishes no new invariant.** The restore steps quote `graduation/database-backup.md` (INV-094's single implementation, INV-048), and no exclusion rule, path or manifest field changed. No ⛔ rule is demoted in shipped text.

## the-bootcamp-cannot-leave-the-machine-it-was-built-on

- **Implemented:** 2026-08-26
- **Files changed:** **new** — `source/scripts/package_bootcamp.py`, `source/scripts/secret_patterns.py`, `source/skills/bootcamp-onboarding/packaging.md`, `source/commands/package-bootcamp.md`, `source/skills/graduation/database-backup.md`, `tests/test_package_bootcamp.py`, `tests/test_secret_patterns_are_shared.py`, `tests/test_database_backup_has_one_implementation.py`; **changed** — `source/skills/graduation/SKILL.md` (Step 6a now cites the shared procedure; one discoverability line in the closing announcement), `specs/INVARIANTS.md` (INV-050's layout tree gains `backups/packages/`), `MIGRATION.md` — the Kiro `slash-backup-project.md` and `scripts/backup_project.py` entries are marked **superseded** by this flow (the packaging command/workflow and `scripts/package_bootcamp.py` respectively), while `hooks/backup-before-load.json` is left explicitly **open**: an automatic pre-load backup is a different decision from a bootcamper-invoked one that asks before it writes — `tests/test_invariant_layout_tree.py` (the pinned directory count).
- **MCP re-check:** n/a (no Senzing fact). This spec asserts nothing about Senzing, the SDK, the entity specification or the MCP server — it concerns the plugin's own artifacts, file layout and interaction layer — so there is no server fact to re-verify and no absence claim to substantiate; the spec says so itself and exempts the `owner-checked:` clause on that basis. `get_capabilities` confirmed server **1.33.0** at the start of this session.
- **Summary:** ⛔ **This is a NEW FEATURE, not a defect repair, and it is the one implementation in this run that a maintainer should review before trusting.** It adds a user-facing command, an any-time conversational flow and a bundled script. Everything below is verified and the suite is green, but the judgment that it should exist at all was the spec author's and mine, not the maintainer's — and the spec's own `## Invariants introduced` says the wording *"Requires maintainer-approved wording before implementation"*. Nothing is pushed. **Criterion walk — thirteen of fourteen met, one partial.** (1) `/package-bootcamp` reaches `packaging.md` from any point and writes `backups/packages/senzing-bootcamp-<profile>-<YYYYMMDD>.zip`; ⚠️ *"works at any point"* is verified structurally (an INV-254-style any-time flow, no module precondition) — a live bootcamp invocation is `dry-run` phase 3's. (2) One pinned numbered 👉 question precedes any write, its sizes come from `--dry-run`, and option 3 writes nothing; **that the dry run writes nothing is tested**, including that it does not even create the output directory. (3) The `share` archive is asserted over a fixture to carry no `*.db`/`*.sqlite`, no `data/raw/`, no `data/temp/`, no `.env`, no `licenses/`, no `config/license.json`, no `logs/`, no `.git/`, no caches — **and** a positive test that it does carry the results, so the exclusions are not passing vacuously. (4) `transfer` carries the revisit state snapshot **and** the database backup, and `OPEN_ME_FIRST.md` points at `docs/REVISIT_BOOTCAMP.md`; it is also asserted **not** to carry the live `database/G2C.db` — the backup travels, the working repository does not. (5) Step 6a's procedure is factored into `graduation/database-backup.md`, both callers cite it, and a test asserts **neither kept a copy of the branch** (Step 6a is sliced out and checked for `pg_dump`, with an anti-vacuity assertion that the slice is non-empty and does cite the file). (6) Running the packager twice shows the second archive contains neither the first nor any `packages/` member. (7) A file containing a PEM private key is excluded and **named with its class** in the manifest, a clean sibling in the same directory still travels, the manifest does **not** echo the secret, and `tests/test_secret_patterns_are_shared.py` asserts the packager's pattern string and `write-gate.py`'s inline copy are byte-identical. (8) A symlink resolving outside the project root is skipped and named (resolve-then-compare, the INV-200 rule). (9) One top-level directory, both orientation files at its root, and the manifest records profile, plugin version, date, `modules_completed`, per-file SHA-256 and size, and the exclusion rules — all asserted. (10) `testzip()` runs, the one-directory shape is re-checked, a `.sha256` sidecar is written, and the digest is asserted to appear in stdout — the archive is never announced unread (INV-067). (11) Nothing is transmitted; the closing line says so and a test asserts it. (12) Graduation gains exactly one discoverability line, as a **statement** with no 👉 and no output path — INV-251 untouched. (13) ⚠️ **Partial:** `backups/packages/` is in INV-050's tree; the **new invariant is deferred** (below). (14) stdlib `zipfile` only, no `tar`/`zip` binary, no assumption about the Bootcamper's language. **Exercised, not merely unit-tested:** the packager was run against a realistic fixture project carrying one of everything it must and must not take — both profiles, dry run and real write, twice for self-exclusion — and the finished archive was extracted and read as a recipient would. That is how the `docs/mapping/` leak was found (see deviations). Suite green at **3,605 passed, 3 skipped** (+48 tests); `conformance.py rules` **0** sections citing no invariant; `citations.py verify` clean; `coverage_reports.py shipped` clean. ⚠️ **A pre-existing test brittleness surfaced and was worked around rather than papered over:** `test_conformance_sees_a_rule_beside_a_citation` validates the **truncated display string** `since` prints rather than the source line, so a stop sign ~800 characters into a 991-character line was reported and then rejected as "not a hard rule". `classify()` accepts the full line. Rather than change the test, the discoverability rule was moved onto its own line — better prose, line-anchored, and legible to every conformance view.
- ⛔ **DEFERRED INVARIANT — and this one the spec itself says must be approved before implementation.** The spec's `## Invariants introduced` carries a fully drafted statement with `INV-NNN` unassigned and the note *"Requires maintainer-approved wording before implementation."* Step 5 requires sign-off and the maintainer is away, so **no ID was minted and nothing was appended to INVARIANTS.md's invariant list**. ⛔ **SPLIT IN TWO on 2026-08-27** by the maintainer's decision (`invariant-review-2026-08-27`), so this is now **two** drafts needing **two** consecutive IDs, not one: *Draft 1 of 2* — what the archive **is** (profiles, contents, exclusion set, byte-level secret scan with no file-type allowlist, symlink resolution, `testzip()` + SHA-256 verification, non-transmission, INV-094 reuse); *Draft 2 of 2* — what the Bootcamper **consents to** (exactly one pinned numbered 👉 question before any write, sizes from a `--dry-run` measurement rather than an estimate, cancel writes nothing). Both are in the spec's `## Invariants introduced`. On approval of either or both, mint the next free ID(s), append with index entries in the same edit, cite Draft 1 at the contents/verification rules and Draft 2 at `packaging.md:25` and `:58`, then re-run `coverage_reports.py shipped`. ⚠️ **This sentence was itself stale for one day** — it said "mint the next free ID" singular, having been written before the split, and a review on 2026-08-27 read the wrong count off it. That is the **third** instance of the class the note below records: a deferral bullet that stops tracking the diff. Corrected rather than annotated because a wrong instruction is worse than a missing one. ⚠️ **Amended 2026-08-26** by `production-readiness-audit-2026-08-26` / `specs/the-packaging-consent-gate-is-an-unregistered-guarantee.md`: this bullet originally said the drafted wording *"is already in the spec file and needs no restating here"*, which pointed at a draft written **before the conversational layer existed** and so silently omitted the consent gate. The draft has been extended to cover it, and the rules this feature ships are now listed individually — a deferral written against a pre-existing draft inherits that draft's blind spots, which is the lesson.
  - **The rules this feature ships, each unregistered pending the ID above:**
    - `skills/bootcamp-onboarding/packaging.md:8` — ⛔ the plugin writes the archive and stops; it never uploads, emails or attaches it *(covered: "MUST NOT be transmitted anywhere by the plugin")*.
    - `skills/bootcamp-onboarding/packaging.md:25` — ⛔ run the dry run first; the question quotes a measured size, never an estimate *(**was uncovered**; now in the draft's consent-gate clause)*.
    - `skills/bootcamp-onboarding/packaging.md:58` — ⛔ option 3 writes nothing at all *(**was uncovered**; now in the draft's consent-gate clause)*.
    - `skills/bootcamp-onboarding/packaging.md:63` — ⛔ run the shared database-backup procedure, never a second SQLite-vs-PostgreSQL branch *(covered by the reuse clause; cites INV-094/INV-048 at the rule)*.
    - `skills/bootcamp-onboarding/packaging.md:96` — ⛔ there is no file-type allowlist; every member is scanned and an unexamined member is excluded *(added 2026-08-26 by `specs/the-packager-secret-scan-skips-the-files-most-likely-to-be-secrets.md`; covered by the draft's corrected secret-scan clause. ⚠️ **This line was missing from this list for one iteration** — the rule shipped in iteration 4 and the list was not extended, which is the same deferral-not-written-against-the-diff mistake this very bullet was rewritten to fix. Caught by `production-readiness-audit-2026-08-26d` reading the one hard-rule line `since` attributed to that round)*.
    - `skills/graduation/database-backup.md:3` — ⛔ this file is the one implementation, two callers cite it *(covered by the reuse clause)*.
    - `skills/graduation/database-backup.md:21` — ⛔ when `database_type` is indeterminate, do not guess a branch *(**relocated**, not new — INV-094 governs it and the file cites INV-094)*.
    - `skills/graduation/SKILL.md` Step 6a — ⛔ follow `database-backup.md` *(covered by the reuse clause)*.
    - `skills/graduation/SKILL.md` closing — ⛔ the discoverability line is a statement naming no output path *(cites INV-251 at the rule)*.

  **HELD 2026-08-27:** ⛔ **Held, not merely unapproved.** The maintainer's stated reason: every
  other invariant registered on 2026-08-27 describes behavior that shipped and was exercised,
  whereas **this feature has never run in a live bootcamp** — and its most serious defect, a
  `.pem` private key packaged into an archive meant for someone else, was found only by executing
  it against a hostile fixture after static reading had passed it twice. Registering it now would
  mean amending a fresh invariant rather than approving a settled one. Revisit after `dry-run`
  phases 2 and 3 have exercised the flow.

  ⚠️ **Moved here from `specs/the-bootcamp-cannot-leave-the-machine-it-was-built-on.md` on
  2026-09-21 (#58), verbatim.** That file still carries the same paragraph and is no longer read
  by anything: `specs/` is frozen under INV-307, so it cannot be edited to say so. The ledger is
  the live copy; the spec is the 2026-08-27 record.
- **Commit:** committed (hash not recorded)
- **Archive commit:** e744eac (a commit of the archived repository; see `specs/README.md`)
