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

## hooks-and-the-hook-adapter-give-the-same-result-under-a-legacy-code-page

- **Implemented:** 2026-11-17 (issue #25)
- **Files changed:** `source/scripts/write-gate.py`, `source/scripts/stop-nudge.py`,
  `source/scripts/feedback-capture.py`, `source/scripts/session-start.py`,
  `source/scripts/precompact-recap.py`, `source/scripts/recap_checkpoint.py`,
  `source/scripts/module_start_apparatus.py`, `hosts/_shared/hook_adapter.py`,
  `tests/test_hooks_under_a_legacy_code_page.py` (new),
  `tests/test_a_finished_bootcamp_is_never_resumed.py` and
  `tests/test_module_start_reminder.py` (one mutation anchor each),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes how the hook scripts and the hook adapter read and write bytes, and asserts
  nothing about Senzing. No absence claim about the Senzing MCP server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** The ten hook scripts and the hook adapter now give the same exit code and the
  same bytes on stdout and stderr whatever encoding Python's standard streams have. Before,
  under a legacy code page, a payload holding a curly quote made the write gate exit 1 where
  it had to block, and the write was then allowed through all four packages that run the
  adapter.
  - **Verified by simulation only.** Every result below comes from running the scripts with
    `PYTHONIOENCODING=cp1252` and again with `PYTHONIOENCODING=utf-8`, on Linux with Python
    3.12.3. No run on Windows happened, and no run on a real assistant happened. No run is
    added to any `hosts/<assistant>/checks.json`. `PYTHONIOENCODING` changes the three
    standard streams only: the encoding `open()` and `subprocess` take from the locale is not
    simulated.
  - **Reading a payload.** `write-gate.py`, `stop-nudge.py` and `feedback-capture.py` read
    stdin as bytes and decode it as UTF-8 with replacement characters. A payload that is not
    valid UTF-8 is then judged as usual, so the write gate still blocks a temp path and a
    secret-shaped write in it. The four hooks that already gave `json.loads` the bytes are
    unchanged.
  - **Writing.** `stop-nudge.py` writes its decision as ASCII-escaped JSON. `session-start.py`
    and `precompact-recap.py` write their plain text, the write gate writes its block message,
    and `recap_checkpoint.py` writes its stderr report, as UTF-8 bytes. The two that share
    `recap_checkpoint.py` use its new `write_utf8`. No message is reworded: the em dashes in
    the resume message and in the container summary stay, and are now bytes `e2 80 94` under
    cp1252 where they were byte `97`. `docker_lifecycle.py` needed no change, because it
    returns the summary and `session-start.py` writes it.
  - **The adapter.** `run_script` gives each script ASCII JSON as bytes, reads its output as
    bytes and decodes it as UTF-8 with replacement characters, so the exit code is always
    used. `write_result` writes ASCII-escaped JSON, and writes the `text` dialect's context
    and every denial reason as UTF-8 bytes through a new `write_text`.
  - **Files that are not valid UTF-8.** A transcript is unreadable to `stop-nudge.py`, as a
    missing one is, so the hook stays silent. The preferences file is read with replacement
    characters, so `disable_stop_nudge: true` still holds. An `event-data` transcript is
    unreadable to the adapter's `final_message`, as it already was to `canonical_transcript`.
  - **Decided here, because the issue names the rule and not these three places.** Each
    follows from "JSON is ASCII-escaped" or from "its ASCII keys are still read", and each has
    its own test and negative control. (1) The payload the adapter hands a script is ASCII
    JSON. (2) So is the adapter's canonical copy of an `event-data` transcript. A lone
    surrogate, which is valid JSON and cannot be encoded as UTF-8, failed both writes and
    ended the event quietly: measured before the change, a temp-path write was allowed through
    the Copilot package when the transcript held one. (3) `module_start_apparatus.py` reads
    `bootcamp_complete` from the preferences file with replacement characters, as the stop
    nudge reads its opt-out from the same file, so a finished bootcamp is not nudged.
  - **Compatibility.** Exit codes and the parsed content of every result are unchanged under
    UTF-8. The bytes of JSON results change, because non-ASCII characters are now escaped. No
    existing test compared those bytes. Two tests that mutate `session-start.py` to prove a
    guard fails now name the `write_utf8` call where they named `print`; the mutations are the
    same.
  - **Unchanged.** Hook commands, payload shapes and `bootcamp_host.json`. The hooks and the
    adapter are standard-library Python, invoked as before (INV-052), and the change adds no
    branch on the platform (INV-001).
  - **Found and not fixed.** `docker_lifecycle.py`'s `_run` decodes a container CLI's output in
    the locale's encoding and catches no decode error, so `session-start.py` exits 1 with a
    traceback when that output cannot be decoded. Reproduced on 2026-11-17 with a stand-in
    `docker` on `PATH`. The simulation cannot see it and the issue does not name it. An issue
    is drafted in the run's handoff and is **not filed**.
  - **Tests.** The new module holds 24 tests. Each starts a hook script from `source/scripts/`,
    or the adapter of a freshly built Copilot, ChatGPT, Gemini or Kiro package, as its own
    process under both encodings and compares exit code, stdout bytes and stderr bytes. The
    denied writes use the tool name each package's `tool_categories` maps, and each denial and
    each context is read in that package's own result dialect. Negative controls, each run in
    a throwaway clone: against the scripts at `1f7c4d9`, 19 of the 24 tests fail
    (`FAILED (failures=47, errors=2)`); with one earlier line restored at a time in the fixed
    scripts, each of 17 mutations fails at least one test. Two changes have no failing
    control, because the text they write is ASCII today: the write gate's block message and
    the pre-compact reminder.
- **Invariants.** The register is not edited here (INV-365). The change ships one hard-rule
  line, in the new test module's docstring. `since` does not report it, because `tests/` is
  not a rule home. The block below covers it.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** A hook script and the hook adapter give the same result whatever Python's I/O encoding is. The rule already shipping, quoted:
    - ⛔ **A hook script and the hook adapter give the same exit code and the same bytes on stdout and stderr whatever Python's I/O encoding is.** — in `tests/test_hooks_under_a_legacy_code_page.py`

  Enforced by `tests/test_hooks_under_a_legacy_code_page.py`.

  **Why it is not an existing invariant:** INV-001 names the three platforms and says nothing
  about how a hook reads or writes text. INV-052 says how a hook is invoked: a Python 3
  script, named in a quoted `command`. INV-055 says the stop nudge has an opt-out, and not
  that the opt-out survives a preferences file saved in another encoding. INV-200 and INV-109
  say what the write gate blocks, and not that the block survives a payload the console's
  encoding cannot decode. None of them says that a hook's result is independent of the
  encoding of Python's standard streams.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Every hook script `source/bootcamp.json` names, and the hook adapter `hosts/_shared/hook_adapter.py`, MUST give the same exit code and the same bytes on stdout and stderr whatever encoding Python's standard streams have. A hook payload MUST be read as bytes and decoded as UTF-8. JSON a hook or the adapter writes MUST be ASCII-escaped, and plain text and stderr MUST be written as UTF-8 bytes. Text that is not valid UTF-8 MUST NOT produce a traceback and MUST NOT lose a block: a payload and a script's output are decoded with replacement characters, a transcript is treated as unreadable, and the ASCII keys of `config/bootcamp_preferences.yaml` are still read. The adapter MUST use a script's exit code whatever that script wrote. Enforced by `tests/test_hooks_under_a_legacy_code_page.py`, which runs the scripts and each built package's adapter with `PYTHONIOENCODING=cp1252` and with `PYTHONIOENCODING=utf-8`, and **cannot** establish behavior on Windows, behavior on a real assistant, or anything about the encoding `open()` and `subprocess` take from the locale. (Source: `hooks-and-the-hook-adapter-give-the-same-result-under-a-legacy-code-page`, GitHub issue #25, 2026-11-17.)

- **Commit:** uncommitted

## the-cited-or-deferred-gate-checks-outside-the-corpus-lines-against-truncated-text

- **Implemented:** 2026-11-17 (issue #49)
- **Files changed:** `tests/test_new_hard_rules_are_cited_or_deferred.py`,
  `tests/test_the_gate_checks_outside_lines_at_their_source.py` (new),
  `tests/test_since_states_its_corpus.py` (one test, for the new return shape),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it decides which report lines a test module checks and what text it checks them against, and
  asserts nothing about Senzing. No absence claim about the Senzing MCP server is made, so
  INV-213's `owner-checked:` clause is not owed.
- **Summary:** The cited-or-deferred gate now checks every line `conformance.py since` reports,
  the `+` lines inside the Markdown corpus and the `!` lines outside it, in every range, and
  tests each one against its whole source line. `conformance.py` is unchanged, and nothing in
  a built package changes.
  - **The heading is kept.** `outside_lines` returns `(heading, line)` pairs, the shape
    `parse_since` already uses for `+` lines. The heading is the path on the `<path>  (<n>)`
    line `since` prints above each file's `!` lines.
  - **One lookup.** `_full_source_line` serves both populations. A source line matches when,
    with its leading whitespace removed, it starts with the reported text, so an indented
    line is found. Before, the raw line was compared with text `since` had stripped, and no
    indented line matched in either population.
  - **The fallback.** The display text is tested instead when no single source line can be
    named: no heading above the line, a file that is missing or unreadable, no matching line,
    or more than one distinct matching line. A cited rule can be flagged that way. An uncited
    rule never passes. Before, the first match was taken, so an uncited rule could be tested
    against a longer, cited line that starts with the same words.
  - **Every range.** Both populations are checked before any skip. A range holding `+` lines
    and an uncited `!` line now fails; before, the `+` line switched the outside check off.
    One failure names the unaccounted lines of both populations.
  - **Decided here, because the issue allows more than one reading.** Two matching lines are
    distinct when they differ after leading and trailing whitespace is removed, so the same
    rule at two indentations is one line. The check also runs before the `SUSPECT-REF` skip:
    a widened range holding only an uncited `!` line now fails, where it skipped before. The
    breakdown line on stderr gains the number of outside lines checked, a zero included.
    Recorded on the issue as its Clarifications comment.
  - **Unchanged.** A range holding only accounted-for `!` lines still ends in the skip that
    says "Accounted for, NOT verified", and an empty range still skips as an empty range.
  - **Not done.** The gate does not compare the number of `!` lines it read with the count on
    the `OUTSIDE the corpus` line. The issue does not ask for it.
  - **Measured on this branch, 2026-11-17.** `since --since-last-audit` reports 0 lines added
    and 0 outside the corpus since `ffc5f4e`, so the live gate skips as an empty range and the
    fixtures carry every case. The one hard-rule line in `hosts/kiro/host.json` has its first
    citation 624 characters into the text `since` reports, past the 110 it displays; a range
    holding only that line now comes out with no line unaccounted for.
  - **Tests.** The new module holds 47 tests. It points the gate at throwaway trees with their
    own ledger and runs the gate's own parser, lookup, predicate and test method over `since`
    reports for them. One class runs `conformance.py since` itself over a throwaway git
    repository and requires the gate to read the hand-built reports exactly as it reads the
    real one. Another reads the real `hosts/kiro/host.json`. Negative controls, each run and
    then reverted: the old lookup (30 failures, 1 error), `!` lines tested as displayed
    (22 failures), `!` lines checked only in a range with no `+` line (5 failures), the
    heading dropped (18 failures, 1 error), the `SUSPECT-REF` skip ahead of the check
    (1 failure), and the first of several matches taken (4 failures).
- **Invariants.** The register is not edited here (INV-365). The change ships one hard-rule
  line, in the gate's docstring. `since` does not report it, because `tests/` is not a rule
  home. The block below covers it.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The cited-or-deferred gate checks every line `since` reports, in every range, at its source line. The rule already shipping, quoted:
    - ⛔ **Every line `since` reports, `+` or `!`, is checked in every range, at its whole source line.** — in `tests/test_new_hard_rules_are_cited_or_deferred.py`

  Enforced by `tests/test_the_gate_checks_outside_lines_at_their_source.py`.

  **Why it is not an existing invariant:** INV-282 says how a guard derives its matcher and
  names the gate as one of its enforcers. INV-431 says `since` reports a hard rule added under
  `hosts/` or `tools/bootcamp_build/`. INV-308 says a tool reports what it could not verify.
  INV-183 is the duty to cite at the rule's own line. None of them says that the gate checks
  the lines `since` marks `!`, that it does so in a range that also holds `+` lines, or which
  text a reported line is tested against.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — The cited-or-deferred gate, `tests/test_new_hard_rules_are_cited_or_deferred.py`, MUST apply its check to every hard-rule line `conformance.py since` reports: the lines marked `+`, inside the Markdown corpus, and the lines marked `!`, outside it. It MUST do so in every range, including a range that holds both kinds and a range whose ref was widened, and before any skip. It MUST test each line against its whole source line and not against the 110-character text `since` displays. The source line is found in the file `since` lists the line under, and a source line matches when, with its leading whitespace removed, it starts with the displayed text. When no single source line can be named (no file heading, a file that is missing or unreadable, no matching line, or more than one distinct matching line), the gate MUST test the displayed text instead, so that a cited rule may be flagged and an uncited rule never passes. Enforced by `tests/test_the_gate_checks_outside_lines_at_their_source.py`, which runs the gate over fixture trees and **cannot** establish that a cited invariant governs the rule beside it, that `since` reports every rule a range adds, or that the gate read as many `!` lines as `since` counted. (Source: `the-cited-or-deferred-gate-checks-outside-the-corpus-lines-against-truncated-text`, GitHub issue #49, 2026-11-17.)

- **Commit:** uncommitted

## auto-test-2026-11-17

**Not a spec** — a dated record of an `/auto-test` run, **unattended**: the maintainer started
it and was away. The MCP probe only; no walk was asked for, so none ran.

- **Implemented:** 2026-11-17 (**0 BREAKING, 10 WATCH, 14 INFO; nothing fixed; filed on
  2026-11-17 as #50**)
- **Files changed:** this record only. The baseline `mcp-snapshot.json` was not refreshed:
  accepting a server change is the maintainer's decision.
- **MCP re-check:** Senzing MCP server 1.46.1, 2026-11-17, by `mcp_probe.py` through
  `autotest.py` at `bdd9d19`. `submit_feedback` and `download_resource` are blocked by flag.
  Outcome: no value the bootcamp sends is rejected and the static contract in
  `tests/test_mcp_call_contracts.py` holds; the server's prose has changed since the baseline.
- **Summary:** No regression detected by the probe. No interaction invariant was checked, and
  phase 3 with the maintainer is not yet done.
  - **WATCH, server prose changed since the committed baseline, each to be re-read:** the
    server `instructions` text; the descriptions of `find_examples`, `get_sdk_reference`,
    `mapping_workflow`, `reporting_guide`, `sdk_guide` and `search_docs`; and the
    `get_capabilities` response, whose `common_confabulations` feed `CONFABULATIONS`.
    `dry-run-2026-11-17` findings 6 and 11 are two places where that prose moved under
    shipped text.
  - **WATCH, `silent-accept`, known since 2026-07-27:** `search_docs.category` accepts a
    nonsense value without an error, so a typo returns wrongly scoped results. Server side.
  - **WATCH, `contract-stale`:** `CONTRACT_VERIFIED_ON` is 2026-08-12, 97 days old against a
    limit of 90. Re-verify and bump it.
  - The full report is `~/senzing-autotest/reports/20261117-091143-terse.json`, outside this
    repository.
- **Filed 2026-11-17** as #50, after the maintainer's yes (INV-314): re-read the changed
  prose, re-verify the contract and refresh the baseline.
- **Invariants.** This record establishes no invariant and queues no block.
- **Commit:** 34911be

## dry-run-2026-11-17

**Not a spec** — a dated record of a dry run, phases 1 and 2, **unattended**: the maintainer
started it and was away. Phase 3 was not run.

- **Implemented:** 2026-11-17 (**18 findings recorded below; none fixed; 16 filed on 2026-11-17 as the
  issues named under "Filed"; four upstream messages drafted, none sent**)
- **Files changed:** this record only.
- **MCP re-check:** Senzing MCP server `sz-mcp-coworker` 1.46.1, 2026-11-17, docs index built
  2026-11-14. Tools called, read-only: `get_capabilities`, `search_docs`, `get_sdk_reference`,
  `sdk_guide`, `find_examples`, `generate_scaffold`, `mapping_workflow` (synthetic labels, no
  data), `explain_error_code`, `get_sample_data`, `analyze_record`, `reporting_guide` (no
  content call). `submit_feedback` and `download_resource` were never called. Outcome by
  finding below: two shipped claims are contradicted by the server, several rationales no
  longer reproduce, and the calls the bootcamp makes are still accepted.
- **Baseline.** Branch `1-docktermj-5` at `ffc5f4e`, tree clean, suite green at
  `Ran 9601 tests`, `OK (skipped=13)`.
- **Environment.** Present: the `senzing` package, `/opt/senzing/er/lib/libSz.so` (loads only
  with `LD_LIBRARY_PATH` set, on this machine), `fpdf2` 2.8.5, `pdftoppm`, `docker`,
  Google Chrome, `ffmpeg`. Absent: `imageio_ffmpeg`, `chromium`. No container was started.
- **Phase 1, verified correct.** Every `action=`, `topic=`, `workflow=`, `platform=` and
  `category=` literal in `source/` is valid on the server. `mapping_workflow` start and
  advance, its enforcement notice, `sdk_guide` install, configure and load, `get_sample_data`,
  `generate_scaffold` initialize, the why-key fields, and `explain_error_code` for 7426,
  SENZ7221 and SENZ9000 are as the shipped text states. No `add_data_source` or `G2Engine`
  appears in shipped text. `hosts/` holds no MCP call text.
- **Phase 1, the dated negatives.** `coverage_reports.py negatives --server 1.46.1` lists 40
  markers, all due; `unmarked` lists none. Re-asked: 1 false (finding 2), 26 hold, 7 hold in
  part, 4 are stale beyond a wording drift (`ground-rules.md:629`, `phaseD-validation.md:504`,
  `visualization-api-reference.md:516`, `phase2-data-mapping.md:876`), 2 were not re-asked
  (`ground-rules.md:1056`, `:1083`). ⚠️ Every `search_docs` re-ask read the top 3 to 5 hits,
  not the default 10, so a "holds" here is weaker than the marker's own check.
- **Phase 2, verified correct.** All eleven Claude hook entries and every adapter event on the
  four other assistants are silent outside a bootcamp. The write gate held on about 75 cases.
  The fold hooks are idempotent. The recap PDF rendered with fpdf2 at 36 pages with 13 of 13
  images, and its pages were looked at; a Latin name with accents renders, and a CJK name falls
  back with a warning. The video, screenshot, discoveries and packaging scripts ran. With
  `LD_LIBRARY_PATH` set, the real engine loaded four records into a scratch SQLite database and
  the visualization server answered every endpoint on 127.0.0.1.
- **Findings, most serious first. All open; see "Filed" below.** P1 is phase 1, P2 is phase 2.
  1. **P2-F1. Three hooks and the adapter fail under a Windows legacy code page.** Simulated
     with `PYTHONIOENCODING=cp1252`; not run on Windows. `write-gate.py:47`,
     `stop-nudge.py:233` and `feedback-capture.py:52` read stdin as text, so a payload holding
     a curly quote raises `UnicodeDecodeError`; the write gate then exits 1 where it should
     block, and through the Copilot adapter the write is allowed. `stop-nudge.py:303` cannot
     print 👉. `hosts/_shared/hook_adapter.py:402-404` loses the session-start context.
     `checkpoint-tick.py:197` already reads bytes for this reason. Verdict: plugin.
  2. **P1-F3. A shipped negative is false.** `module-02-sdk-setup/SKILL.md:1879-1884` says a
     `search_docs` query for the record limit returns EULA prose with no figure. The top hit is
     now the FAQ "What is the 500 record limit…". The routing to `sdk_guide` still works; the
     stated reason does not. `tests/test_record_limit_negative_is_rescoped.py` and
     `tests/test_prescribed_search_queries.py:712` pin the retired wording. Verdict: plugin.
  3. **P1-F1. "Preview Release — Unsupported" is relayed as fact and the server no longer
     carries it.** `module-02-sdk-setup/SKILL.md:676-682` (also `:671`, `:706`). The Scoop
     bucket README came back in full with no such notice; for the Homebrew tap only the
     prescribed query's top four hits were read.
     owner-checked: `search_docs` is the corpus route for both READMEs and the one the text
     names — the Scoop README returned whole, without the notice; `sdk_guide(topic='install')`
     for `macos_arm` and `windows` carries no such wording. `tests/test_sdk_update_offer.py`
     pins the retired wording. Verdict: plugin; the Homebrew half needs one more read.
  4. **P2-F2. On the four non-Claude packages the feedback hook says the version is
     "Unknown"**, and the packager records "unknown" on ChatGPT and Kiro.
     `feedback-capture.py:39-43` and `package_bootcamp.py:377` look for a Claude manifest
     path; `bootcamp_host.json` beside each script carries the version. Verdict: plugin.
  5. **P1-F2. The server indexes the bootcamp's own repositories.**
     `find_examples(query='multi-source')` returns only two bootcamp `CHANGELOG.md` files, and
     a `search_docs` query ranks a bootcamp script first. No shipped text says a hit from a
     bootcamp repository is not Senzing evidence. The marker at
     `phaseC-multi-source.md:214` still holds; its rationale does not. Verdict: both.
  6. **P1-F5. `get_sdk_reference(topic='flags', filter=<method>)` changed shape.** It returns
     lines of text under group headers, with no `source_file`, and points at a `flag_details`
     topic that no shipped file names. `phaseD-validation.md:492-495`,
     `ground-rules.md:819-822`, `phase2b-discover.md:34-36`. Verdict: plugin.
  7. **P1-F4. That compact list renders "depends on" and "member of" as `NAME = X`**, which
     reads as a definition; `phase1-query-visualize.md:317-322` sends the guide there for the
     opposite lesson. Verdict: both.
  8. **P2-F3. After graduation, three hooks still treat the bootcamp as in progress.**
     `checkpoint-tick.py:204`, `precompact-recap.py:18` and `session-end.py:21` test
     `bootcamp_active()` and not `bootcamp_complete()`, so a later prompt recreates the recap
     checkpoint. Verdict: plugin.
  9. **P2-F4. PowerShell writes to a temp directory pass the write gate on Copilot.**
     `hosts/copilot/host.json:68` maps `powershell` to the shell tool, and
     `write-gate.py:180` and `:319` parse POSIX shell only. Verdict: plugin.
  10. **P2-F5. The unprintable-name warning names the wrong file.**
      `generate_recap_pdf.py:4688-4692` says to fix the name in the recap; only the preferences
      file changes the certificate. Verdict: plugin.
  11. **P1-F6. The mixed-type rationale is stale** (`phase2-data-mapping.md:595-602`): the
      server no longer declares `record_type` as an enum and now says to send the dominant
      type itself. The guidance is still right. Verdict: plugin.
  12. **P2-F7. Three gaps in what the packager promises**: symlinked directories are left out
      and not named (`package_bootcamp.py:247`); UTF-16 text is not scanned for secrets
      (`:346`); and the `share` profile carries the feedback file and the recap checkpoint,
      which the consent question does not name. Verdict: plugin; the third is a design call.
  13. **P2-F6. The stop nudge prints a traceback on an undecodable transcript**
      (`stop-nudge.py:171` catches `OSError` only). Verdict: plugin.
  14. **P1-F7. A consequence the text calls observation-only is now documented**
      (`phase2-data-mapping.md:865-873`). Verdict: plugin, low.
  15. **P2-F8. In the stdlib PDF fallback the page-1 title and subtitle touch**
      (`generate_recap_pdf.py:4074-4075`). Verdict: plugin, cosmetic.
  16. **P2-F9. The write gate blocks an Edit that removes a secret**, with a message telling
      the guide to do what it is doing (`write-gate.py:421-427`). Verdict: plugin, low.
  17. **P1-F8. Two server tools disagree on the Las Vegas source count** (11 against 10). The
      bootcamp hardcodes neither. Verdict: mcp-server.
  18. **P1-F9. Two server documents disagree on the Java jar name** (`sz-sdk-java.jar` against
      `sz-sdk.jar`). The bootcamp uses the second only. Verdict: mcp-server.
  - **Stale wording, claim still true:** `module-02-sdk-setup/SKILL.md:1649` and `:2381`,
    `module-05-data-quality-mapping/SKILL.md:97`, and two quotations of server text at
    `phase2-data-mapping.md:190-191` and `:398` that the server has reworded.
  - **Confirmed by execution from `production-readiness-audit-2026-11-17`:** its findings 3
    (slash command in the session-start message), 17 (the adapter half) and 18.
- **Upstream messages, drafted and not yet sent — each needs maintainer approval.** Four: on the flags list (finding 7), the indexed bootcamp repositories
  (finding 5), the source count (finding 17) and the jar name (finding 18). Findings 5 and 7
  are `both`, so their messages belong inside a GitHub issue; 17 and 18 are `mcp-server`.
  Upstream: not yet sent — needs maintainer approval. The drafted text, as of server 1.46.1:
  - **Flags list (finding 7).** "`get_sdk_reference(topic='flags', filter=<method>)` (tried
    with export_json_entity_report, why_records, find_network_by_entity_id) returns one line
    per flag, and the tool description says composites are shown as `NAME = A|B|C`. Several
    lines use `=` for relationships that are not composites:
    `SZ_INCLUDE_MATCH_KEY_DETAILS = SZ_ENTITY_INCLUDE_ALL_RELATIONS` (the row for that flag
    says it 'is dependent on using one of' the relations flags) and
    `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA = SZ_RECORD_DEFAULT_FLAGS` (the row says 'Member of').
    A reader takes these as definitions and may pass the dependent flag alone. The export
    listing also carries `SZ_EXPORT_INCLUDE — (undocumented)` and `SZ_ENTITY — (undocumented)`,
    which look like name prefixes. Suggest a distinct marker for 'requires' and 'member of'."
  - **Indexed bootcamp repositories (finding 5).** "The example and docs corpus includes
    Senzing bootcamp plugin repositories. `find_examples(query='multi-source')` returns only
    two results, both CHANGELOG.md files from those repositories, one with provenance
    'official'. `search_docs(query='NEED_REEVALUATION how entity final state')` ranks a
    bootcamp helper script first. These are teaching-plugin housekeeping files, not Senzing SDK
    examples, and a client that treats this server as its source of Senzing facts can be handed
    its own text. Suggest excluding these repositories, or at least their changelogs and
    non-SDK scripts."
  - **Source count (finding 17).** "`get_capabilities` describes the las-vegas dataset as
    '11 sources', while `get_sample_data(dataset='list')` names 10 and
    `get_sample_data(dataset='las-vegas', source='list')` returns 'Found 10 sources'."
  - **Jar name (finding 18).** "The anti-patterns article 'Ecosystem and Dependencies' shows
    artifactId `sz-sdk-java` and `/opt/senzing/er/sdk/java/sz-sdk-java.jar`. The Java SDK
    reference served by search_docs shows artifactId `sz-sdk` and
    `${SENZING_PATH}/er/sdk/java/sz-sdk.jar`, and the sdk_guide install gotchas for macos_arm
    and windows also use `sz-sdk.jar`. One of the two is wrong."
- **Filed 2026-11-17**, after the maintainer's yes to the whole list shown in one message
  (INV-314). By finding number: 1 and 13 are #25; 2 and 3 are #35; 4 is #31; 5 is #37; 6 and 7
  are #36; 8 is #32; 9 is #33; 10, 15 and 16 are #47; 11, 14 and the stale wording are #38; 12
  is #46. Findings 17 and 18 are the server's alone and have no issue: each is an upstream
  draft above, not yet sent. The drafts for findings 5 and 7 are named in #37 and #36.
- **Invariants.** This record establishes no invariant and queues no block.
- **Coverage limits.** ⛔ Phase 3 was not run, so the conversational layer is untested.
  Phase 1 did not reach `reporting_guide` content (Modules 6 and 7), `mapping_workflow` steps 4
  to 8, several `sdk_guide` and `generate_scaffold` topics, or about 25 prescribed
  `search_docs` queries. Phase 2 ran no real assistant, no Windows or macOS machine and no
  container; findings 1 and 9 are simulations.
- **Mistakes in this run.** Both phases were run by agents under a no-change limit, so no
  finding was drafted here as it was found; this entry was written from their reports
  afterwards, and nothing was re-run by the lead. Phase 1's re-asks were looser than the
  markers in three ways its report lists. Phase 2's scratch loader was written from memory,
  not from the server.
- **Commit:** bdd9d19

## production-readiness-audit-2026-11-17

**Not a spec** — a dated record of an audit run, **unattended**: the maintainer started it and
was away. It follows the six issues merged on 2026-11-16 (#9 to #14) and the invariant review
that registered INV-428 to INV-432.

- **Implemented:** 2026-11-17 (**33 findings recorded below; none fixed; all filed on 2026-11-17 as the
  issues named under "Filed"**)
- **Files changed:** this record only.
- **MCP re-check:** n/a (no Senzing fact). Every finding is internal consistency, and no
  Senzing MCP tool was called. No absence claim is made about the Senzing MCP server, so
  INV-213's `owner-checked:` clause is not owed. Findings that would rest on what an
  assistant other than Claude does are listed as not checked, not asserted.
- **Baseline.** Branch `1-docktermj-5` at `419de72`, tree clean.
  - **Suite green:** `Ran 9601 tests`, `OK (skipped=13)`.
  - `citations.py verify` clean at 430 invariants; `bootcamp_build check` OK;
    `coverage_reports.py shipped` lists nothing; `pending_invariants.py list` shows
    `pending: 0`, three held.
  - `since --since-last-audit` resolved `dc79183` from `production-readiness-audit-2026-11-16`,
    for the first time: 2 hard-rule lines added in the corpus, both cited at the line
    (INV-427, INV-308), and 6 outside it, each cited (INV-431, INV-432, INV-308, INV-252).
    `reverse-check` says `NOT CLEAN` for one reason: one of the two lines is on the maintainer
    surface, which `per-rule` does not read.
  - Reachable here: `fpdf2`, `pdftoppm`, `docker`, Google Chrome. Not found: `chromium`.
- **Scope, chosen deliberately.** Not a full forward sweep. Three read-only sweeps, each
  re-verified, and the lead read the most serious findings against the files again:
  1. forward, over the invariants the six merges touched (INV-114, 247, 252, 426 to 432), in
     all five built packages and the site pages;
  2. the five packages side by side: file lists, rendered differences, cross-references,
     install pages, hooks, and the layout documents;
  3. what the previous audit skipped: the per-module outcome blocks (INV-028 to INV-050), 38 of
     the 95 enumerating invariants, duplicated passages and the heaviest files.
- **Verdict by property.**
  - **Consistent:** no. Shared text states one assistant's facts in all five packages (A2-02,
    A2-03, A2-04, A2-05, F2, F4).
  - **Coherent:** mostly. Two wrong or stale citations (F5) and several drifted restatements
    (A3-5, A3-6, A3-7).
  - **Complete:** no. Four packages point at a file they do not carry (A2-01), and one step
    assumes a choice no step makes (A3-2).
  - **Concise:** not a verdict. One duplicated deliverable found (A3-10); file sizes are
    unchanged in kind from the previous audit.
- **Verified correct.**
  - INV-028 to INV-049: every outcome is produced where the invariant, as amended, says; the
    banners, journey map, stage table and module list are byte-identical across packages.
  - INV-247: no non-Claude package names a Claude control or "Don't show again", apart from
    F6; both rules read as complete sentences in all five.
  - INV-428, INV-429, INV-426, INV-430, INV-432 and the INV-114 and INV-252 notes hold at
    every site found. `options.skill_location_sources` matches `hosts/kiro/checks.json`.
  - 38 enumerating invariants match what ships: INV-001, 016, 029, 047, 048, 057, 065, 074,
    094, 099, 103, 107, 133, 137, 140, 141, 155, 157, 195, 248, 249, 255, 260, 281, 340, 342,
    354, 367, 368, 375, 413, 419, 426, 431, and INV-050 except A3-3.
  - Every other relative path, anchor and `file.md → "Heading"` reference resolves in all five
    packages; each install page's verification note matches its `checks.json`.
- **Findings, most serious first. All open; each is filed, see "Filed" below.** Ids are the sweep's own: A2 is the
  cross-package sweep, A3 the outcome and enumeration sweep, F the forward sweep.
  1. **A2-01. Four packages send the guide to `hooks/README.md`, which they do not carry.**
     `hosts/{copilot,kiro,chatgpt,gemini}/host.json:28` maps it to null, and
     `source/skills/bootcamp-onboarding/SKILL.md:77` and `ground-rules.md:408`, `:886` and
     `:1271` name it in every package. It is also the only place the stop-nudge off switch is
     documented. The recorded reason for the drop does not cover the references.
  2. **A2-02. Every package states one assistant's shell as the guide's shell.**
     `ground-rules.md:1134-1135` says a guide-run block runs "with its Bash tool" in "the
     guide's POSIX shell, which on Windows is Git Bash", and 55 stamps repeat it. The hosts'
     own profiles name the shell tool `bash`, `execute_bash` and `run_command`, and Copilot's
     lists a PowerShell tool. INV-163 registers the sentence with no assistant scope. What
     shell each assistant uses on Windows was not checked.
  3. **A2-03 and A3-1, found twice. Slash commands are named to bootcampers on four assistants
     that ship no command.** 28 mentions per non-Claude package, among them the line
     `graduation/SKILL.md:1943` pins verbatim ("Run `/package-bootcamp` anytime…"), which
     INV-057's 2026-11-10 note pins in that form. Every `host.json` declares `command_prefix`
     (`$` on ChatGPT) and nothing uses it. Whether typing the command works on those
     assistants was not checked.
  4. **A2-04. The fallback rules and the ground rules state opposite facts about the same
     hooks**, in the four non-Claude packages. `source/hooks/fallbacks/*.md:3` says "Nothing
     checks a write before it happens"; `ground-rules.md:860`, `:885`, `:1296-1302`, `:1540`
     and `module-02-sdk-setup/SKILL.md:831` say a hook does. The fallback exists, so no
     safeguard is missing. `module-05…/phase3-test-load.md:389` already uses a neutral form.
  5. **F1. INV-427 is written for every file the guide is told to read, and ships at one
     site.** The instruction is at `bootcamp-onboarding/SKILL.md:23` only. Each package has 17
     other Markdown files over the 30,000 characters Kiro's read was cut at. If INV-427 means
     the first-turn ground rules only, its first clause is wider than the rule.
  6. **A3-2. Windows with Python has two install routes and no step chooses.**
     `module-02-sdk-setup/SKILL.md:688-694` describes a container and WSL2; `:628` says
     "Detect first, do not ask"; `:2711-2712` says "Do NOT offer alternatives".
  7. **A2-05. The MCP failure message names `.mcp.json` in every package**
     (`onboarding-flow.md:82`). Copilot and Kiro ship `mcp.json`; Gemini ships
     `mcp_config.json`.
  8. **F2. The Kiro package says both that Kiro gives no skill path and that "the harness
     supplies that directory"** (`onboarding-flow.md:39-41`, shared text, against the note
     appended to every Kiro skill).
  9. **A3-3. INV-050 says `config/license.json` is "written in Module 4"** and that "Module 2
     only reads the detected limit" (`specs/INVARIANTS.md:177`, `:239-243`). Module 2 Step 5a
     saves it first (`module-02-sdk-setup/SKILL.md:1816`), as INV-244 and INV-295 require. The
     invariant's text is what is stale; a dated note on INV-050 is owed and is not drafted as
     a block here, because the wording is the maintainer's.
  10. **A2-06. The Kiro install page's Python requirement contradicts the Kiro package**
      (`hosts/kiro/fragments/site-before.html:2`: "Python 3.10 or later… `python3`, `python`
      or `py`"; the package and the other four pages require `python3` on `PATH`).
  11. **F3. The Kiro location note gives two instructions for one condition.** With
      `KIRO_HOME` set and the bootcamp absent, one sentence sends the guide to `.kiro` in the
      home directory and the next says "look only inside `powers/` in the Kiro home".
  12. **F4. A Claude model ID is the example in all five packages**
      (`feedback.md:191`: `"claude-opus-5-5[1m] / high"`). The build's foreign-term match is
      case-sensitive, so lowercase `claude-` passes.
  13. **A2-07. Two packages name an interface their install page does not cover**: VS Code on
      Copilot (`hosts/copilot/fragments/interface-naming.md:9`) and the Codex CLI on ChatGPT
      (`hosts/chatgpt/fragments/interface-naming.md:3,8`).
  14. **A3-4. `selected_modules` is kept in two files and the text disagrees on which is
      read** (`bootcamp-preparation/SKILL.md:440-442` against `ground-rules.md:1437-1438`).
  15. **F5. Two citations name the wrong invariant.** `ground-rules.md:1486-1487` cites
      INV-140 for "one level per row", which is INV-141; `:1518-1520` lists INV-141 among the
      retired nudge rules, and it is in force.
  16. **A2-08. The Kiro package calls itself "plugin" on 127 lines and "Power" on 3**;
      `package_noun` is read by the certificate only.
  17. **A2-09. The ChatGPT and Kiro hook matchers exclude tools their own adapter maps**
      (`hosts/chatgpt/host.json:46-50` against `:77-83`). The assistants' real tool names were
      not checked.
  18. **A2-10. Kiro's hook-install disclosure describes three of the five hooks it installs**
      (`hosts/kiro/files/skills/bootcamp-hooks-setup/SKILL.md:18-26`).
  19. **F6. `visualization-api-reference.md:1627-1628` names a "background-task" mechanism** in
      four packages whose control list is empty. It is a technical note, not a question.
  20. **A3-5. The module-completion citation has drifted across module closes**: Modules 1 and
      2 omit Step 0, and Module 5 puts the summary before the recap, against the fixed order
      in `module-completion.md:4-11`.
  21. **A3-6. Module 4 offers synthesized data beside free raw data at Step 2 and calls it a
      last resort 900 lines later** (`module-04-data-collection/SKILL.md:868-876`, `:1786`).
  22. **A3-7. "all four report one version"** (`onboarding-flow.md:52-54`) no longer describes
      the feedback entry, which reads `bootcamp_host.json` first. The values agree.
  23. **A3-8. Three stale lists or pointers in shipped text**: the readers of
      `bootcamp_complete()`, the readers of the generated-scenario marker, and
      `hooks/fallbacks/checkpoint-tick.md:4-5` naming the wrong file as the rule's owner.
  24. **A2-11. One layout sentence is false in the Kiro package**
      (`graduation/SKILL.md:786-787`).
  25. **A2-12. Update and uninstall steps are uneven across the five install pages.**
  26. **A2-13. The ChatGPT catalog and manifest give different categories**
      (`tools/bootcamp_build/emit.py:602`, `hosts/chatgpt/host.json:61`).
  27. **A2-14. The Copilot package breaks its own interface-naming rule** ("the Copilot app").
  28. **A3-9. `source/scripts/package_bootcamp.py:150` names the wrong test file** for a pin
      that `tests/test_quoted_sizes_say_what_they_missed.py` holds.
  29. **A3-10. Module 5 step 18 writes two overlapping per-source documents**
      (`phase2-data-mapping.md:1935`, `:1944-1946`).
  30. **A2-15. Layout documents state things the build no longer does**: `tests/README.md`
      names `propagate.sh`; `README.md` and `.claude/CLAUDE.md` list three markers where
      `host:except` is a fourth; `README.md:31` says text outside a marker is copied
      unchanged; `README.md:49` overstates what `check` fails on.
  31. **A3-11. Maintainer skills cite guards that are not in this repository**:
      `tests/test_specs_are_frozen.py`, `specs/FROZEN-MANIFEST.txt` and `propagate.sh`. The
      absent tests are accepted in `NOT_CARRIED`; the invariant text that names them is not
      queued for a note.
  32. **F7. Maintainer text lags the tools.** `production-readiness-audit/SKILL.md:167-168`
      and `:180-181` and `since --help` describe the range start without the fallback;
      `duplication` and `size` print no roots line, which INV-431 asks of every view; and
      `docs/model-selection.md:145-146` says every shipped skill has a row where it has 12.
  33. **Carried from the previous run, still open and not filed:** the cited-or-deferred gate
      checks outside-the-corpus lines against 110-character display text, on a path that does
      not run on today's range.
- **Filed 2026-11-17**, after the maintainer's yes to the whole list shown in one message
  (INV-314). By finding number: 1 is #26; 2 is #27; 3 is #28; 4 is #29; 5 is #39; 6 is #40;
  7, 8, 12, 16, 19 and 24 are #30; 9 is #41; 10 and 11 are #42; 13, 25 and 27 are #43; 14 is
  #44; 15, 20, 21, 28 and 29 are #45; 17, 18 and 26 are #34; 22 is #31; 23 is #32 for the
  readers of `bootcamp_complete()` and #45 for its other two lists; 30, 31 and 32 are #48; 33
  is #49. No issue carries the `unattended-ok` label.
- **Invariants.** This record establishes no invariant and queues no block. Findings 9 and 31
  each call for a dated note on a registered invariant, and finding 5 for a decision about
  INV-427's scope; the wording of each is the maintainer's, so none is drafted here.
- **Coverage limits.** ⛔ The conversational invariants (INV-005, INV-006, INV-008, INV-009,
  INV-014, INV-251 and every gate ordering rule) were not tested; reading cannot establish
  them and they need `dry-run` phase 3. No assistant was run. About 55 enumerating invariants
  were not checked. `module-02-sdk-setup/SKILL.md`, `phase2-data-mapping.md`,
  `phase1-query-visualize.md` and the Module 6 phases were searched, not read in full. What a
  non-Claude assistant's tools, events, shell and commands really are was not checked.
- **Mistakes in this run.** The sweeps were done by three agents and the lead re-read only
  the first twelve findings against the files; the rest stand on the agents' own second
  check. One sweep first reported two recorded items as new and withdrew them.
- **Commit:** ffc5f4e

## invariant-review-2026-11-16-loop

**Not a spec** — the record of a third `/review-invariants` session on 2026-11-16, attended by
the maintainer. It decided the eight blocks the unattended run of that day queued, from issues
#9 to #14. A review record mints ids and adds citations; it establishes no invariant of its own.

- **Implemented:** 2026-11-16
- **Files changed:** `specs/INVARIANTS.md`, `specs/IMPLEMENTED.md`,
  `tools/bootcamp_build/emit.py`,
  `.claude/skills/production-readiness-audit/conformance.py`,
  `tests/test_invariant_enforcer_citations.py`, `tests/test_model_docs_name_no_switch.py`,
  `tests/test_partial_shipping_has_a_reason.py`, `tests/test_since_states_its_corpus.py`,
  `tests/test_the_gate_sees_every_scanned_root.py`,
  `tests/test_reverse_check_counts_what_it_cannot_test.py`,
  `tests/test_sites_states_the_corpus_it_scanned.py`, `tests/test_coverage_reports.py`,
  `tests/test_kiro_skills_say_where_they_are.py`,
  `tests/test_since_last_audit_falls_back_to_the_ledgers_commit.py`
- **MCP re-check:** n/a (no Senzing fact)
- **Summary:** The maintainer gave a verdict on each block, one at a time, and every verdict
  was to register or apply the drafted wording unchanged. Nothing was held, amended or split.
  - **Registered, five new invariants:** INV-428 (an install page that names a model takes it
    from `model_capable`, issue #13), INV-429 (no install page mentions an effort, issue #13),
    INV-430 (a source file ships to every assistant or to none unless a reason is recorded,
    issue #12), INV-431 (the audit and review tools read every directory the build takes
    package text from, issue #9), INV-432 (the since-last-audit views take their range start
    from the ledger alone, issue #10).
  - **Applied, three dated notes:** on INV-114 (the derived table is a maintainer page no
    package carries, issue #12), on INV-247 (the class of control binds on every assistant;
    the list is one assistant's dated examples, issue #14), on INV-252 (a stated location
    holds on every supported platform and its sources are recorded, issue #11).
  - **One citation outside a block's site list.** INV-430 names a shipped artifact, and no
    shipped text cited it, so `tests/test_every_invariant_is_cited_in_shipped_text.py` failed
    after the registration. One sentence in the `placed_files()` docstring of
    `tools/bootcamp_build/emit.py` now cites it.
  - **Enforcer pairs.** `EXPECTED_PAIRS` went from 350 to 360, re-derived by running the
    extractor after each decision: one pair each for INV-428, INV-429, INV-430 and INV-432,
    five for INV-431, and one for the INV-252 note, whose test gained its back-citation.
  - **What remains.** The queue is empty: `pending: 0`. Three blocks stay held, each with its
    recorded revisit condition, and none of those conditions was met in this session.
  - **Verification.** After each decision: `citations.py verify` clean, `pending_invariants.py
    check` with no mismatch and no unresolved quote, and the full suite, last read as
    `Ran 9601 tests`, `OK (skipped=13)`.
- **Commit:** 419de72

## the-install-page-and-the-welcome-name-different-models-on-chatgpt

- **Implemented:** 2026-11-16 (issue #13)
- **Files changed:** `hosts/chatgpt/host.json`, `hosts/chatgpt/fragments/site-install.html`,
  `hosts/chatgpt/fragments/site-tips.html`, `hosts/claude/fragments/site-install.html`,
  `tests/test_model_docs_name_no_switch.py`, `tests/test_model_guidance_sync.py`,
  `tests/README.md` (one phrase), `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16 against the change itself:
  it changes which model two install pages and one welcome name, removes the effort steps from
  two install pages and adds tests. It asserts nothing about Senzing. No absence claim about
  the Senzing MCP server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** On ChatGPT the install page, the model tip and the welcome now name one model,
  from one value, and no assistant's install page sets or names an effort. Audit finding 6 of
  `production-readiness-audit-2026-11-16`.
  - **ChatGPT's `model_capable`.** It was "a high-capability Codex model" and is now
    "GPT-5.6 Terra", the name the install page already carried. The built ChatGPT welcome and
    the ChatGPT model tip both read "GPT-5.6 Terra suits it well". The name was moved, not
    re-checked against Codex: the issue says so, and no run on a real assistant was made. No
    `hosts/<assistant>/checks.json` gained an entry.
  - **The install fragments.** The Claude and ChatGPT fragments name the model through
    `{{host.model_capable}}` and nowhere as literal text: the Claude Desktop step, the Claude
    CLI sentence and the ChatGPT step. They are the first fragments to use a host token. The
    build already substitutes tokens in a fragment, so the build tool did not change.
  - **Effort removed.** Six mentions are gone: "Choose the Effort medium", "at medium effort"
    and `--effort medium` on Claude, "Choose the effort Medium" on ChatGPT, and the word from
    the two lines that introduce those steps, which now read "set the mode and model" and
    "select the model". The Claude CLI command reads
    `claude --model claude-opus-5-5 --permission-mode auto`. The ChatGPT step keeps its
    lettered list, now with one item, because the issue removes words and keeps the lines.
  - **What a build shows.** Three built files differ from `main`, measured by building both:
    one line of the ChatGPT package's `onboarding-flow.md`, and the Claude and ChatGPT install
    pages. The Copilot, Gemini and Kiro install fragments are byte-for-byte unchanged, and the
    other four packages are unchanged.
  - **The new checks**, in `tests/test_model_docs_name_no_switch.py`, on all five assistants.
    Each install fragment is read as written and as the build renders it, with
    `substitute_tokens`, the function the build calls on a fragment.
    - A fragment that names a model must use the token, must not spell its own
      `model_capable` value, and must render that value. A fragment names a model when its
      visible text holds the word "model" or its source holds the token. One that names none
      passes; Copilot, Gemini and Kiro are in that state. The rendered page is also held
      against the built welcome, so both sides are read. The check fails when the Claude or the
      ChatGPT page names no model, so it cannot pass on nothing (INV-265).
    - The Claude CLI command must equal `claude --model <ID> --permission-mode auto`, where
      the ID is derived from Claude's `model_capable`: "Opus 5.5" gives `claude-opus-5-5`. A
      page with no such command is reported.
    - No fragment's rendered visible text may hold the word "effort".
  - **Negative controls, in the module.** The retired ChatGPT pairing, a page saying
    "GPT-5.6 Terra" under a welcome saying "a high-capability Codex model", is reported with
    two problems. A model spelled out in place of the token is reported, in every place and in
    one. A stale model ID, the command with `--effort medium` and a moved `model_capable` are
    each reported. Each of the six removed effort mentions is reported, and an effort put back
    on the real ChatGPT and Claude pages is reported. Against the host files as they were on
    `main`, run in a throwaway clone, the module reports 16 failures.
  - **Existing tests changed, because the old expectation is now wrong.** Three, none deleted:
    - `test_model_docs_name_no_switch.py`: the walkthrough check read the Claude fragment as
      written and looked for "Choose the Model Opus 5.5". It now reads the rendered text.
      The samples for the mid-bootcamp-switch pattern quoted `--effort medium` and "select the
      model and effort:"; they quote the new wording.
    - `test_model_guidance_sync.py`: two cases looked for "Opus 5.5" in the Claude fragment as
      written. The superseded-name scan now reads the Claude fragments as rendered, through
      one function, `repo_doc_text()`. One control was added: a superseded `model_capable`
      value reaches the scan through the fragment.
    `tests/test_interface_naming.py` passes unchanged. With the host edits alone, the full
    suite failed on exactly those three cases.
  - **Tests.** 18 added: 17 in `test_model_docs_name_no_switch.py`, which goes from 13 to 30,
    and one in `test_model_guidance_sync.py`. No new file reads a corpus line by line.
  - **Audit views, measured 2026-11-16.** `conformance.py since --since-last-audit` prints the
    same report before and after: 2 lines added in the corpus, 6 outside it. The fragments are
    `.html` and hold no hard-rule line.
    `tests/test_new_hard_rules_are_cited_or_deferred.py` passes.
  - **Known limits.** The checks cannot establish that a `model_capable` value names a model
    the assistant offers, or that a model ID exists. They do not report a page that names a
    second model beside the token. The model tips stay literal text, held to `model_capable`
    by the existing tip test. The effort check reads the fragments, not the shared page
    template `site/_install.html`.
- **Invariants.** The register is not edited here (INV-365). The change ships three hard-rule
  lines, in the test module's docstring, which no `conformance.py` view reads. The two blocks
  below cover them: one for the model, one for the effort, because they are two subjects.
  INV-426 is not amended: it governs what the bootcamp asks and what a package ships, and an
  install page is neither.

- **DEFERRED INVARIANT (resolved INV-428, registered by the maintainer 2026-11-16).** An install page that names a model names the welcome's model, from one value. The rule already shipping, quoted:
    - ⛔ **An install page that names a model takes the name from `{{host.model_capable}}`, the value the welcome is built from.** — in `tests/test_model_docs_name_no_switch.py`
    - ⛔ **The model ID in the Claude CLI start command is the one derived from Claude's `model_capable`.** — in `tests/test_model_docs_name_no_switch.py`

  Enforced by `tests/test_model_docs_name_no_switch.py`.

  **Why it is not an existing invariant:** INV-426 says the welcome names one suitable model
  exactly once, and says nothing of the install pages. INV-114 says model guidance names only
  current models and IDs. A current name on the install page and a different one in the
  welcome contradicts neither, and that is the state ChatGPT was in.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Where an assistant's install page (`hosts/<assistant>/fragments/site-install.html`) names a model, it MUST take the name from `{{host.model_capable}}`, the value in `hosts/<assistant>/host.json` that the welcome's one-model statement is built from, and MUST NOT spell that value as literal text. An install page MAY name no model. The model ID in the Claude CLI start command is a second spelling of the same value: it stays literal in the fragment, it MUST equal the ID derived from Claude's `model_capable` (lowercase, each space and dot replaced by a hyphen, prefixed with `claude-`), and the command MUST read `claude --model <that ID> --permission-mode auto`. Enforced by `tests/test_model_docs_name_no_switch.py`, which reads each fragment as written and as the build renders it, holds the rendered page against the built welcome, and fails when the Claude or the ChatGPT page names no model, so that it cannot pass on five pages that name none (INV-265). It **cannot** establish that a `model_capable` value names a model the assistant offers, or that a model ID exists. It does not report a page that names a second model beside the token, or a model named without the word "model" and without the token. The model tips in `site-tips.html` stay literal text, held to the same value by the same module. (Source: `the-install-page-and-the-welcome-name-different-models-on-chatgpt`, GitHub issue #13, 2026-11-16.)

- **DEFERRED INVARIANT (resolved INV-429, registered by the maintainer 2026-11-16).** No install page sets or names an effort. The rule already shipping, quoted:
    - ⛔ **No install page mentions an effort.** — in `tests/test_model_docs_name_no_switch.py`

  Enforced by `tests/test_model_docs_name_no_switch.py`.

  **Why it is not an existing invariant:** INV-426 holds the bootcamp to never asking for an
  effort change and to shipping nothing that sets one. An install page is in no package, and a
  step taken once before the bootcamp starts is not a change made during it. So two install
  pages set an effort, three did not, and none contradicted a registered rule.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — An assistant's install page (`hosts/<assistant>/fragments/site-install.html`) MUST NOT mention a reasoning effort: no step that sets one, no command flag that sets one, and no sentence that names a level. The Bootcamper runs at their assistant's default effort, and how carefully the guide works at each stage is set by instruction alone (INV-426). Enforced by `tests/test_model_docs_name_no_switch.py`, which searches the visible text of every assistant's install fragment, as the build renders it, for the word "effort", and requires each of the five fragments to hold text. It reads the fragments, not the shared page template `site/_install.html`. (Source: `the-install-page-and-the-welcome-name-different-models-on-chatgpt`, GitHub issue #13, 2026-11-16.)

- **Commit:** uncommitted

## a-maintainer-page-ships-in-the-claude-package-only-and-links-to-a-file-no-package-carries

- **Implemented:** 2026-11-16 (issue #12)
- **Files changed:** `docs/model-selection.md` (moved from `source/docs/model-selection.md`),
  `hosts/chatgpt/host.json`, `hosts/copilot/host.json`, `hosts/gemini/host.json`,
  `hosts/kiro/host.json`, `source/skills/bootcamp-onboarding/ground-rules.md` (one line),
  `tests/test_partial_shipping_has_a_reason.py` (new), `tests/test_model_guidance_sync.py`,
  `tests/test_interface_naming.py`, `tests/test_model_docs_name_no_switch.py`,
  `tests/test_model_selection_covers_every_skill.py`,
  `tests/test_hard_rule_detector_sees_mid_line_stop_signs.py`,
  `tests/test_any_language_citations_name_the_right_rule.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16 against the change itself:
  it moves a maintainer page, removes four layout entries and adds two invariant ids to one
  line of the ground rules, and asserts nothing about Senzing. No absence claim about the
  Senzing MCP server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** The maintainer page on model and effort is now `docs/model-selection.md` in this
  repository, beside `docs/effort-mechanisms.md`, and no package carries it. A new test holds
  one table of the source paths that ship to some assistants and not others, with a reason
  for each. Audit finding 5 of `production-readiness-audit-2026-11-16`.
  - **The move.** `git mv`, so the page's history follows it. Five lines changed, in four
    places, and nothing else: its two paths to the onboarding skill now start
    `../source/skills/`; it names the research page as `effort-mechanisms.md`, beside this
    file; and its staleness note says "this file or the shipped plugin". Its tables, model
    names, prices and dates are untouched.
  - **The layouts.** The `"docs/model-selection.md": null` entry is gone from the ChatGPT,
    GitHub Copilot, Gemini and Kiro layouts. The Claude layout never named the page. The Claude
    package goes from 93 files to 92; the other four keep their counts (92, 92, 92 and 93).
  - **One line of shipped text changed, which the issue did not foresee.** The page was the
    only file under `source/` that cited INV-114 and INV-140. With it gone,
    `coverage_reports.py shipped` listed both, and
    `tests/test_every_invariant_is_cited_in_shipped_text.py` failed. That guard says to add the
    id at the site that states the rule, so the lead-in to the working-depth table in
    `ground-rules.md` now ends "row (INV-140). This table is the authoritative copy
    (INV-114):" where it ended "row:". Every package's `ground-rules.md` gains those words.
    The issue's Compatibility section says the other four packages are unchanged; they change
    by this one line. Issue #12's Clarifications comment records it.
  - **The new test.** `tests/test_partial_shipping_has_a_reason.py` takes, for every file under
    `source/`, the set of assistants whose layout places it, from the build's own
    `placed_files()`, and holds that against all five built packages. `PARTIAL` has two
    entries: `commands` and `hooks/README.md`. A partial path that no entry covers fails. An
    entry fails when it names no source file, or covers a file that ships to every assistant
    or to none. A directory entry covers the files under it. The ten files under
    `source/hooks/fallbacks/` ship to no assistant and need no entry. The same module fails
    when a package carries `model-selection.md`, when a file in any package holds the text
    `effort-mechanisms`, and when a path the page names does not resolve from `docs/`.
  - **Tests repointed, none deleted.** Six modules read the page at its new path: the five the
    issue names and `tests/test_any_language_citations_name_the_right_rule.py`. Four
    assertions kept their text and changed what they are about:
    - `test_model_guidance_sync.py` walked the Claude package to find superseded model names
      and met the page there. The page is now named in `shipped_markdown()`, and a new case
      fails if it drops out of the scan. The table comparison now holds the Claude package's
      `ground-rules.md` against a page outside the package.
    - `test_interface_naming.py` said no shipped file names a model or effort control. Its
      third file is now the maintainer page, which is not shipped.
    - `test_hard_rule_detector_sees_mid_line_stop_signs.py` reads its fixture line in a file
      that `rules` no longer reads. It asserts what the classifier does with the line, which is
      the same.
    - `test_any_language_citations_name_the_right_rule.py` counted the page as shipped text.
      Its two floors on shipped text now read shipped text alone, and a new assertion holds
      the page's INV-124 citation by name.
    A test that scans all of `source/` no longer reads the page.
  - **Measured on this branch, 2026-11-16.** `rules` and `per-rule` report 848 hard-rule lines
    before and after, 275 with no citation at the rule: the page held no hard-rule line. Their
    `CORPUS:` line goes from `source (55 file(s))` to `source (54 file(s))`. `size` goes from
    55 files and 278,859 words to 54 files and 276,964 words. `duplication` goes from 264
    repeated passages across 168 file pairs to 228 across 166: the 35 passages the page shared
    with `ground-rules.md` are no longer counted, because `duplication` reads `source/` alone.
    `since --since-last-audit` and `reverse-check --since-last-audit` print the same report
    before and after. `coverage_reports.py shipped` lists nothing, as before.
  - **Negative controls, each run and then reverted.** With the page back under `source/` and
    the four `null` entries restored, the new module reports 4 failures, among them
    `docs/model-selection.md (only in: claude)`. With `docs/examples` dropped from one layout
    it reports 1 failure. With `hooks/README.md` placed by every layout it reports 2, the
    stale entry among them. With one skill file naming `docs/effort-mechanisms.md` it
    reports 5, one for each package. Before the ground-rules line changed, the full suite
    failed on `test_no_invariant_naming_a_shipped_artifact_is_uncited`.
  - **Known limits.** The table records a reason; it cannot establish that the reason is true
    or still current. The test does not cover a file one package takes from
    `hosts/<assistant>/files/`, and it does not check that every path a package names resolves
    inside that package: the issue puts that general test out of scope. The page's opening
    sentence still says it "does not ship as bootcamper-facing content", which is true and no
    longer the whole of it; the issue limits edits to what the move requires.
- **Invariants.** The register is not edited here (INV-365). The change ships two hard-rule
  lines, in the new test's docstring, which no `conformance.py` view reads. The first block
  below covers both. The second proposes a dated clarification on INV-114, whose two paths now
  start from different roots.

- **DEFERRED INVARIANT (resolved INV-430, registered by the maintainer 2026-11-16).** A source file that ships to some assistants and not others has a recorded reason, and no package carries the maintainer page. The rule already shipping, quoted:
    - ⛔ **A source file that ships to some assistants and not others has a recorded reason.** — in `tests/test_partial_shipping_has_a_reason.py`
    - ⛔ **No package carries the maintainer page `model-selection.md`, and no package names `effort-mechanisms`.** — in `tests/test_partial_shipping_has_a_reason.py`

  Enforced by `tests/test_partial_shipping_has_a_reason.py`.

  **Why it is not an existing invariant:** The build already stops on a source file that a
  host's layout neither places nor drops, so a drop is always written down. Nothing asks why.
  No registered invariant says the five packages carry the same source files, names a layout,
  or says where a maintainer page lives. INV-426 holds one table identical in every package and
  INV-252 holds where a package says its files are; neither reaches which files a package
  carries.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — A file under `source/` MUST ship to every assistant's package or to none, unless its path, or a directory above it, has an entry in the `PARTIAL` table of `tests/test_partial_shipping_has_a_reason.py` that states the reason in a sentence. A file ships to an assistant when that assistant's layout in `hosts/<assistant>/host.json` places it in the package. An entry MUST be added in the change that makes a path partial and removed in the change that ends that: an entry that names no source file, or that covers a file now shipping to every assistant or to none, is a defect. A page written for maintainers MUST NOT live under `source/`. `docs/model-selection.md` is such a page: no package may carry it, and no file in any package may name `docs/effort-mechanisms.md`, which no package carries. Enforced by `tests/test_partial_shipping_has_a_reason.py`, which takes the shipped sets from the build's `placed_files()` and holds them against all five built packages. It **cannot** establish that a recorded reason is true or still current, or recognize a maintainer page other than the one it names; it does not cover a file one package takes from `hosts/<assistant>/files/`, and it does not check that every path a package names resolves inside that package. (Source: `a-maintainer-page-ships-in-the-claude-package-only-and-links-to-a-file-no-package-carries`, GitHub issue #12, 2026-11-16.)

- **PROPOSED AMENDMENT to INV-114 — applied 2026-11-16 by the maintainer.**
    - ⛔ **`ground-rules.md` is the authoritative copy of this table; the copy below is derived.** — in `docs/model-selection.md`

  INV-114 names two files. When it was written both shipped in the plugin, so both paths
  started at the package root. `docs/model-selection.md` now starts at the root of this
  repository and no package carries the page. The words are the same and name a different
  place. Without the note below, a reader looks for the derived copy inside a package and
  finds none, and nothing registered says the page is still held to the rule. Enforced by
  `tests/test_model_guidance_sync.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-114** — (⚠️ **Dated clarification, 2026-11-16 (issue #12): the derived copy is a maintainer page that no package carries; the rules above are unchanged.** `docs/model-selection.md` is a path from the root of the development repository, where the page moved from `source/docs/`. It is not bootcamper-facing. The authoritative table is the "Working depth by stage" table in `skills/bootcamp-onboarding/ground-rules.md`, which every assistant's package carries and which cites this invariant at the table. `tests/test_model_guidance_sync.py` still holds the page to this rule: its table and its level instructions match the authoritative copy, it carries a dated verification note, and it names a superseded model only inside that note.)

- **Commit:** uncommitted

## the-never-ask-list-names-one-assistants-controls-in-every-package

- **Implemented:** 2026-11-16 (issue #14)
- **Files changed:** `source/skills/bootcamp-onboarding/ground-rules.md`,
  `hosts/chatgpt/host.json`, `hosts/claude/host.json`, `hosts/copilot/host.json`,
  `hosts/gemini/host.json`, `hosts/kiro/host.json`,
  `tests/test_no_host_control_is_offered_as_a_question.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16 against the change itself:
  it decides which controls of an assistant's own interface the ground rules name as examples,
  and asserts nothing about Senzing. No absence claim about the Senzing MCP server is made, so
  INV-213's `owner-checked:` clause is not owed.
- **Summary:** Both ground rules that keep a session control out of the bootcamp's questions now
  state the control by kind on every assistant, and name examples only from that assistant's
  own host values. Audit finding 7 of `production-readiness-audit-2026-11-16`.
  - **The two rules.** The rule that every 👉 question traces to a skill file, and the any-time
    entry "A host control the bootcamper raises", each name three kinds: a mode, a permission
    setting, a conversation command. The second keeps "any other setting belonging to their
    session". The list of eight controls is gone from `source/`.
  - **The host values.** Every `hosts/<assistant>/host.json` declares two values under `vars`.
    `session_control_examples` holds the assistant's example controls and
    `dismissal_control_example` holds the dismissal control its rule names. Claude's first
    value names nine: the eight the rule named, and `bypass permissions`, which only the guard
    listed before. Claude's second names "Don't show again". GitHub Copilot, Kiro, ChatGPT and
    Gemini declare both empty: their controls are not verified.
  - **How a value reaches the rule.** The source puts the value's `{{host.<name>}}` token
    straight after the kinds, and the build places the value as written. A filled value is a
    piece of the sentence: one space, then the controls in parentheses. An empty one leaves
    a complete sentence. The build tool is unchanged, and filling a value later changes no
    file under `source/`.
  - **What each package says.** The Claude package names all nine controls in both rules and
    still says: not "Don't show again", not any other. The other four name no control and do
    not contain "Don't show again". The rule against naming a dismissal control is in all five.
    The rule's meaning is unchanged on every assistant.
  - **Two values, where the issue's scope says one.** One value holds the example controls, as
    the scope says. The second exists because "Don't show again" sits in the middle of a
    sentence and a `host:only` block works on whole lines. With it, another assistant can name
    its own dismissal control later with no change to `source/`.
  - **The guard.** `HOST_CONTROL` in `tests/test_no_host_control_is_offered_as_a_question.py`
    holds no list. It is built from every assistant's `session_control_examples`, and matches
    each control by its first two words joined by a hyphen, a space or nothing, in any letter
    case. It matches everything the old list matched; 21 probes in three letter cases assert
    that. It is slightly wider: the old pattern allowed the joined form only for the two `auto`
    controls, so `planmode` now matches too. The dated snapshot marker and both disclosed
    limits stay. Limit 2 now also says that every control of an assistant whose value is empty
    passes.
  - **Chosen by a race.** Two implementations were built and judged against a rubric written
    first; issue #14's Approach comment has the table. The other added a block marker to the
    build tool that keeps its lines only where a value is not empty.
  - **Tests.** The module grew from 25 tests to 42, in three new classes. They build all five
    packages and assert: the three kinds in both rules, a complete sentence around each
    assistant's own value with no empty clause, no control in a package whose own value does
    not list it, "Don't show again" only where the dismissal value names it, and both values
    declared in every `host.json` in the shape the rules need. One class renders the source for
    every assistant with both values emptied and then with invented ones, so the check holds
    whichever values are filled today. Negative controls are in the module: an empty clause in
    seven forms, an invented control, a lookalike that must not match, and an empty word list.
    A further control was run and then reverted: against the ground rules as they were on
    `main`, the module reports 64 failures, in 10 of its tests.
  - **Also corrected.** The guard's docstring said a search for the control names matched only
    the rule text and the guard. It now names the five files the search matches.
  - **No real run was made.** No `hosts/<assistant>/checks.json` is changed.
  - **Known limits.** A filled value carries its own punctuation, and a value in another shape
    stops the guard module at load, with a message naming the file and the shape. The scan of
    pinned questions still reads the Claude package alone, so a question kept only for another
    assistant is not scanned for that assistant's controls once its value is filled. The Claude
    package has two long lines where the list is placed, since the build does not re-wrap.
- **Establishes no new invariant** (INV-309), and proposes a change to one in force. The
  register is not edited here (INV-365). No hard-rule line is added: the five lines edited in
  `ground-rules.md` sit inside two rules that cite INV-247, and `conformance.py since` reports
  nothing from this change. The block below proposes the dated note on INV-247 that would
  bind the rule by kind and name the list as one assistant's examples. Until the maintainer
  applies it, only the test holds them.

- **PROPOSED AMENDMENT to INV-247 — applied 2026-11-16 by the maintainer.**
    - ⛔ **Every 👉 question traces to a step in a shipped skill file — never originate one (INV-247).** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **never present a session- or host-level control as a bootcamp question** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **Do not name a dismissal affordance either** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-247's registered text lists eight controls (auto mode, auto-accept edits, permission
  mode, plan mode, fast mode, background tasks, `/compact`, `/loop`) as if they were the class,
  and names "Don't show again" as the dismissal affordance. They are one assistant's controls.
  Until issue #14 they shipped in all five packages, so four assistants were told to avoid
  controls they do not have and told nothing about their own. Without the note below the
  register reads as binding Claude's list on every assistant, and the next editor writes the
  list back into `source/`. Enforced by `tests/test_no_host_control_is_offered_as_a_question.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-247** — (⚠️ **Amended 2026-11-16 (issue #14): the class of control binds on every assistant; the list is Claude's dated examples.** The MUST condition is unchanged. On every assistant the guide MUST NOT present a session- or host-level control as a bootcamp question, and the class is stated by kind: a mode, a permission setting, a conversation command, or any other setting belonging to the Bootcamper's assistant session. The eight controls listed above, with `bypass permissions`, are examples naming the Claude Code CLI's affordances as of 2026-08-15. They are not the class and not a closed set. A package names example controls only where they have been verified for its assistant, taken from that assistant's own `session_control_examples` value in `hosts/<assistant>/host.json`; an assistant with no verified examples declares the value empty, and its package states the rule by kind alone. "Don't show again" is likewise Claude's example of a dismissal affordance, held in `dismissal_control_example`; the rule against naming any dismissal affordance binds on every assistant. Enforced by `tests/test_no_host_control_is_offered_as_a_question.py`, which builds its word list from those values, builds all five packages, and **cannot** establish which controls an assistant other than Claude has: only a check against that assistant can, and on 2026-11-16 none has been made.)

- **Commit:** uncommitted

## audit-and-review-tools-do-not-scan-rule-text-under-hosts

- **Implemented:** 2026-11-16 (issue #9)
- **Files changed:** `.claude/skills/production-readiness-audit/conformance.py`,
  `.claude/skills/review-invariants/pending_invariants.py`,
  `.claude/skills/dry-run/coverage_reports.py`,
  `.claude/skills/production-readiness-audit/SKILL.md`,
  `.claude/skills/review-invariants/SKILL.md`, `.claude/skills/dry-run/SKILL.md`,
  `tests/test_since_states_its_corpus.py`, `tests/test_the_gate_sees_every_scanned_root.py`,
  `tests/test_reverse_check_counts_what_it_cannot_test.py`,
  `tests/test_sites_states_the_corpus_it_scanned.py`, `tests/test_coverage_reports.py`,
  `tests/test_since_last_audit_falls_back_to_the_ledgers_commit.py` (one assertion),
  `tests/test_every_invariant_is_cited_in_shipped_text.py` (one docstring note),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-16 against the change itself:
  it decides which directories three maintainer scripts read, and asserts nothing about
  Senzing. No absence claim about the Senzing MCP server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** The three audit and review tools now read the host-side inputs, the files under
  `hosts/` and `tools/bootcamp_build/` that the build turns into package text. No file that
  ships to a bootcamper changes.
  - **`conformance.py`.** `hosts` joins `SCAN_ROOTS` and `tools/bootcamp_build/` joins
    `UNCOUNTED_RULE_HOMES`. `since` reports a hard rule added to a Markdown file under `hosts/`
    with `+`, and one added to `host.json`, an `.html` or `.py` file under `hosts/`, or the
    build tool with `!`. `rules`, `per-rule` and `reverse-check` read the Markdown under
    `source/` and `hosts/` through one function, `rule_markdown()`, so a rule added to host
    Markdown is TESTED. `rules` and `per-rule` print a `CORPUS:` line with a file count for
    each root and a `NOT READ:` line, on every run. `duplication` and `size` still read
    `source/` alone.
  - **`pending_invariants.py sites`.** The candidate scan reads `source/`, `hosts/` and
    `tools/bootcamp_build/`. `.json` joins the candidate suffixes for every root at once, so
    the scanned and not-scanned counts still measure one set of suffixes, and the scope
    statement names that set. It prints one `SCANNED` line for each root, a root holding no
    file included.
  - **`coverage_reports.py`.** `shipped` counts a citation in any text file under `source/`,
    `hosts/` or `tools/bootcamp_build/`, and its heading names the three. `negatives` reads
    `hosts/` as well, in `.md` and `.py` files as under its other roots. `unmarked` reads
    Markdown under `source/` and `hosts/`. `negatives` and `unmarked` print a `CORPUS:` line
    on every run.
  - **The gate.** `tests/test_new_hard_rules_are_cited_or_deferred.py` is unchanged: it reads
    `SCAN_ROOTS` from the producer, so it checks a rule reported under `hosts/` from this
    change on.
  - **Chosen by a race.** Two implementations were built and judged against a rubric written
    first; issue #9's Approach comment has the table. This one gives each tool the new roots
    in its own constants. The other stated the host-side inputs once and had two tools load
    `conformance.py` by path. No tool under `.claude/skills/` loads another today.
  - **Skill text corrected.** Five sentences in the three `SKILL.md` files described the old
    corpora. One of them is a hard-rule line, in `review-invariants/SKILL.md`, and still cites
    INV-308 at the line.
  - **Measured on this branch, 2026-11-16.** `rules` and `per-rule` report 848 hard-rule lines
    before and after, 275 citing no invariant at the rule: no hard rule sits in host Markdown
    today. Both print `CORPUS: source (55 file(s)), hosts (11 file(s))`. `sites` prints
    `SCANNED source: 82`, `hosts: 21`, `tools/bootcamp_build: 9` and `NOT SCANNED 554`.
    `shipped` and `unmarked` list nothing. `since --since-last-audit`, from `dc79183`, reports
    2 lines with `+`, both cited at the line, and 6 with `!`, among them the `host.json` and
    `emit.py` rules no view listed before.
  - **Tests.** 39 test methods added across the five modules that already pin these corpora,
    with no new test file. Each acceptance criterion has a test, and each new view statement
    is tested on a run that finds nothing. Three existing assertions changed because the old
    expectation is now wrong: the call `reverse-check` shares with `per-rule`, the `shipped`
    heading, and the roots a live `unmarked` hit may sit under. A fourth, added by issue #10,
    pinned `TESTED … in source`; the view now prints `in source, hosts`. Negative control, run
    and then reverted: against the three tools as they were on `main`, the six modules report
    51 failures and 4 errors.
  - **Known limits.** The three tools hold their roots separately, so a later root means three
    edits. `negatives` does not read `.json` or `.html`, and says so in its `CORPUS:` line. A
    rule the build composes from pieces, so that no single input line holds it, is seen by no
    view. `site/` and `public/` are not read.
  - **A limit of the gate, found here and not changed.** The gate checks `!` lines only when
    the range has no `+` line, and it checks the 110-character display text, not the source
    line. `hosts/kiro/host.json`'s rule is one long line whose `(INV-252)` sits past column
    110, so that branch would flag it although it is cited. The branch does not run on today's
    range, which has two `+` lines. Changing it is outside this issue.
- **Invariants.** The register is not edited here (INV-365). The change ships one new
  hard-rule line, in `conformance.py`'s module docstring, which `since` reports with `!`. The
  block below covers it. One existing hard-rule comment in `conformance.py` was reworded and
  cites INV-308 at the line.

- **DEFERRED INVARIANT (resolved INV-431, registered by the maintainer 2026-11-16).** The audit and review tools read every directory the build takes package text from. The rule already shipping, quoted:
    - ⛔ **A directory the build takes package text from is read by the audit and review tools.** — in `.claude/skills/production-readiness-audit/conformance.py`

  The other two tools state their roots as constants and carry no rule line:
  `.claude/skills/review-invariants/pending_invariants.py` (`HOST_SIDE_INPUTS`) and
  `.claude/skills/dry-run/coverage_reports.py` (`SHIPPED_ROOTS`, `NEGATIVE_ROOTS`,
  `PROSE_ROOTS`). Enforced by `tests/test_since_states_its_corpus.py`,
  `tests/test_the_gate_sees_every_scanned_root.py`,
  `tests/test_reverse_check_counts_what_it_cannot_test.py`,
  `tests/test_sites_states_the_corpus_it_scanned.py` and `tests/test_coverage_reports.py`.

  **Why it is not an existing invariant:** INV-308 requires one definition of the roots a tool
  resolves against and a statement of what it could not verify. INV-246 requires a guard to
  derive its sites by scanning. Neither says which directories the corpus must cover, so the
  three tools went on reading `source/` and `.claude/` alone after package text gained a
  second home, and contradicted no registered rule.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — The maintainer tools that audit and review rule text MUST read every directory the build takes package text from, and not the shared source alone. Today those directories are `source/`, `hosts/` and `tools/bootcamp_build/`. A hard rule added to any file under `hosts/` or `tools/bootcamp_build/` MUST be reported by `conformance.py since`; one in a Markdown file under `hosts/` MUST be listed by `rules` and `per-rule` and tested by `reverse-check`. `pending_invariants.py sites` MUST scan `hosts/`, its `.json` files included, and `tools/bootcamp_build/` for candidates. `coverage_reports.py shipped` MUST count a citation in either directory, and `negatives` and `unmarked` MUST read `hosts/`. A directory that later holds package text MUST join the roots of all three tools in the change that adds it. The tools read the inputs and not a built package: `dist/` is ignored by git, so a range diff cannot see it, and a reported rule needs a source line where its citation can be written. Each view MUST name the roots it read on every run, a run that finds nothing in them included (INV-308). ⚠️ Limits: a rule the build composes from pieces, so that no single input line holds it, is seen by no view, and `site/` and `public/` are outside this rule. Enforced by `tests/test_since_states_its_corpus.py`, `tests/test_the_gate_sees_every_scanned_root.py`, `tests/test_reverse_check_counts_what_it_cannot_test.py`, `tests/test_sites_states_the_corpus_it_scanned.py` and `tests/test_coverage_reports.py`. (Source: `audit-and-review-tools-do-not-scan-rule-text-under-hosts`, 2026-11-16.)

- **Commit:** uncommitted

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

- **PROPOSED AMENDMENT to INV-252 — applied 2026-11-16 by the maintainer.**
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

- **DEFERRED INVARIANT (resolved INV-432, registered by the maintainer 2026-11-16).** The since-last-audit views take their range start from the ledger alone, and say when it is the fallback. The rule already shipping, quoted:
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
