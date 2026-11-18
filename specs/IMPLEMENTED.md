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

## dated-mcp-rationales-and-quotations-in-shipped-text-no-longer-reproduce

- **Implemented:** 2026-11-18 (issue #38)
- **Files changed:** `source/skills/module-05-data-quality-mapping/phase2-data-mapping.md`,
  `source/skills/module-05-data-quality-mapping/SKILL.md`,
  `source/skills/module-02-sdk-setup/SKILL.md`,
  `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/module-03b-truthset-visualization/visualization-api-reference.md`,
  `source/skills/module-06-data-processing/phaseD-validation.md`,
  `source/skills/module-03-system-verification/phase1-verification.md`,
  `source/skills/module-04-data-collection/SKILL.md`,
  `source/skills/module-06-data-processing/phaseA-build-loading.md`,
  `source/skills/module-06-data-processing/phaseB-load-first-source.md`,
  `source/skills/module-07-query-visualize-discover/phase1-query-visualize.md`,
  `source/skills/module-07-query-visualize-discover/phase2-discover.md`,
  `source/skills/module-07-query-visualize-discover/phase2b-discover.md`,
  `source/scripts/senzing_viz_server.py`, `specs/DECLINED.md` (the two markers, by the
  maintainer's decision of 2026-11-18), `tests/test_step2_record_type_contradiction.py`,
  `tests/test_payload_key_collides_with_registered_feature.py`,
  `tests/test_the_2026_09_30_audit_rules_cite_their_invariants.py`,
  `tests/test_quality_assessment_type_name_check.py`,
  `tests/test_globalization_retrieval_strategy.py`, `tests/test_license_env_var_absent.py`,
  `tests/test_loader_concurrency_reads_database_type.py`,
  `tests/test_prescribed_search_queries.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** server 1.46.1 (`get_capabilities`: `"server_version":"1.46.1"`), docs index
  built 2026-11-14 17:44 UTC (`"index_built"` in every `search_docs` reply, 13404 documents),
  2026-11-18. Outcome: the claims mostly still reproduce; ten rationales or quotations did not and
  are corrected; two markers are findings, left untouched (below). Tools called, read-only, each
  marker re-asked individually with its own call and parameters, every `search_docs` call at the
  default result count with all ten hits read, the owning route re-asked where it differs, and
  every call made before any file changed: `get_capabilities`, `mapping_workflow` (start, step 1,
  step 2 with a legacy `embedded_master` payload lacking `embedded_in`, step 2 with
  `record_type='MIXED'`; synthetic labels only, no data), `analyze_record`, `sdk_guide`,
  `generate_scaffold`, `get_sdk_reference`, `search_docs`, `find_examples`, `reporting_guide`,
  `explain_error_code`, and the declared tool schemas of `find_examples`, `generate_scaffold` and
  `download_resource` read from the tool manifest. `submit_feedback` and `download_resource` were
  not called. Quotes that decided a correction:
  - `mapping_workflow` step 2: *"set record_type to the DOMINANT type (e.g. PERSON or ORGANIZATION
    — do NOT send "MIXED": it is not a type, only a literal string here)"*; its `advance_schema`
    `record_type` is `"type":"string"` with *"any other value (e.g. VEHICLE) is accepted"*, no
    enum; sending `MIXED` returns *"record_type 'MIXED' is not one of the usual values ...; any
    value is accepted, so this is advisory only"*; the legacy shape *"is also still accepted for
    backward compatibility"*; without `embedded_in` the reply is
    `"schema_plan[1] (employer): 'embedded_master' requires 'embedded_in'"`.
  - `mapping_workflow`'s tool description: *"The call needs both arguments present; it does NOT
    need the file to exist."* (the quoted *"The call WILL FAIL without both"* is gone).
  - `analyze_record(workspace_dir='data/mapping')` `validation_guidance.valid_shapes`: *"(2)
    feature attributes at the record root — flat, still supported"*;
    `sdk_guide(topic='load', language='python', record_count=100)`: *"the flat/legacy shape
    (feature attributes at the record root ...) is NOT one of these problems — the Entity
    Specification still supports it"*.
  - `download_resource`'s declared schema: `filename`, `filenames`, `inline`, `offset`, `version`,
    `workspace_dir`.
  - `search_docs(query='globalization')`: the "What languages does Senzing support?" section is
    returned, sixth; the Rust SDK's `GLOBAL_ENVIRONMENT` is not.
  - `search_docs(query='NEED_REEVALUATION how entity final state')`: the field appears in the how
    flags page's payloads and in the Java `SzEngine` reference's `howEntity` example result; the
    top hit is a bootcamp repository's script.
  - `sdk_guide(topic='install', platform='macos_arm', language='python')`: compatibility note
    *"(1) Pick a different language — Java and C# are officially supported on macOS and Windows;
    Rust and TypeScript are community-supported on all platforms. (2) Pick a different environment
    — use Docker or WSL2"*, plus a `next_steps` entry for the docker install.
  - `mapping_workflow(action='start')` step 1: *"a `curl` download from this server over HTTP, or
    a local extract command when the server runs over stdio"* (no "stdio/airgap mode").
  owner-checked: `get_sdk_reference(topic='response_schemas', filter='how_entity_by_entity_id')`
  — `HOW_RESULTS.FINAL_STATE.NEED_REEVALUATION` `{"field_type":"integer"}`, no description (the two
  NEED_REEVALUATION absence markers).
  owner-checked: `analyze_record` and `sdk_guide(topic='load')` — both state the root-key
  consequence, so that marker is now a routing negative; `search_docs` with the marker's query
  still returns no section stating it.
  owner-checked: `sdk_guide(topic='install', platform='macos_arm', language='python')` — declines
  the platform, no `install_commands`, `env_vars` or `gotchas` (the macOS PYTHONPATH absence).
  owner-checked: `sdk_guide(topic='install', platform='docker', language='csharp'|'typescript')` —
  *"It must also already contain your language runtime (python3, a JDK, .NET or Node.js)"*, no
  install command (the container toolchain absence).
  owner-checked: the tool manifest's declared schemas — neither `find_examples` nor
  `generate_scaffold` declares `inline`.
- **Summary:** `coverage_reports.py negatives --server 1.46.1` listed 37 due markers this issue
  owns (34 under `source/skills/`, one in `source/scripts/senzing_viz_server.py`, two in
  `specs/DECLINED.md`) and 5 current ones (#35, #36, #37, left alone). Each of the 37 was
  re-asked on its own call. After the change the report lists 2 due, the two findings below, and
  none of the out-of-scope three, which their merged issues had already re-dated. Line numbers
  are at `5aaba2a`.
  - **Holds, re-dated to server 1.46.1, 2026-11-18 (25):** `phase2-data-mapping.md:417`
    (`embedded_in`), `senzing_viz_server.py:2351`, `module-02-sdk-setup/SKILL.md:374`, `:378`,
    `:403`, `:435`, `:523`, `:1108`, `:1554`, `:1754`, `:1777`, `:2323`,
    `module-04-data-collection/SKILL.md:1662`, `phaseA-build-loading.md:429`,
    `phaseB-load-first-source.md:156`, `phase1-query-visualize.md:454` and `:490`,
    `phase2-discover.md:189`, `phase2b-discover.md:380`, `phaseD-validation.md:509`,
    `ground-rules.md:556`, `:1107` and `:1134` (the two the dry run did not re-ask),
    `phase1-verification.md:285`, `specs/DECLINED.md:126`.
  - **Corrected (10):** `specs/DECLINED.md:135` (owner clause quotes the current step-1 stdio
    wording and the SENZ9000 binary line); `module-02-sdk-setup/SKILL.md:1680` (the reply also
    offers Rust and TypeScript) and `:2410` with its prose (the reply also carries a `next_steps`
    pointer to the docker install); `module-02-sdk-setup/SKILL.md:901` (the Dockerfiles that add
    python3 do so on a Senzing runtime image; the owner's sz-napi minimums cite the README, which
    carries both); `module-05-data-quality-mapping/SKILL.md:97` with its prose (the bare call now
    returns the UTF-8 section, behind other Guide sections; the Rust hit is gone) and `:111`
    (it leads with the template files, which are not all of its hits); `phaseD-validation.md:720` and
    `visualization-api-reference.md:516` (the field also appears in the Java reference's
    `howEntity` example; the latter's "the only hits" no longer held); `ground-rules.md:647` with
    its prose (`download_resource` also declares `workspace_dir`);
    `phase2-data-mapping.md:877` (now a routing negative, owner `analyze_record` and
    `sdk_guide(topic='load')`).
  - **The twelve sites under Problem.** `ground-rules.md:629` is the `:647` marker above;
    `phaseD-validation.md:504` belongs to #36 and is current; `visualization-api-reference.md:516`
    and `phase2-data-mapping.md:876` are above; `:1056` and `:1083` are `:1107` and `:1134`;
    `module-02-sdk-setup/SKILL.md:1649` and `:2381` are the `:1680` and `:2410` markers;
    `module-05-data-quality-mapping/SKILL.md:97` is above. `phase2-data-mapping.md:190-191` now
    quotes *"The call needs both arguments present"*, and `:398` *"also still accepted for backward
    compatibility"*, each stamped. The mixed-type note (`:595-602`) is retired under its own
    condition at `:648`: the step-2 prose and its `advance_schema` agree, so the contradiction
    paragraph, the MIXED-warning paragraph and the retirement sentence are gone, and the ⛔
    (INV-280) rule now reads "send the source's dominant type as `record_type`, never `MIXED`",
    cited to the step-2 quote above. The Retype bullet calls it "one of the source's real types"
    where it said "enum-valid", since `record_type` is no longer an enum. The paragraph at
    `:865-873` loses its OBSERVATION-ONLY label and cites `analyze_record` and
    `sdk_guide(topic='load')` for the consequence, keeping its 2026-08-17 first observation. It
    names that route as "`sdk_guide`'s `load` topic": the literal call form in step 11 makes
    `tests/test_build_and_run_statement.py` read the step as one that writes SDK code.
  - **Findings, left untouched with their old version and date (2).**
    1. `module-02-sdk-setup/SKILL.md:239`. `search_docs(query='szBuildVersion.json build version
       file location')` now returns, at ranks 9 and 10, a `senzing-garage` performance-test
       runbook naming `/opt/senzing/er/szBuildVersion.json` for 4.x container images, so "no
       indexed document gives that file's path on any platform" no longer holds as written.
       Correcting it would also change the Linux bullet's "No MCP route states it" provenance
       (INV-149), and whether a `senzing-garage` runbook counts as a source is a judgment: the
       server's own anti-pattern says `senzing-garage` "contains experimental/internal/legacy
       code". Its evidence slot in `tests/test_prescribed_search_queries.py` is left as is too.
    2. `bootcamp-preparation/SKILL.md:295`. `sdk_guide(topic='install', platform=…)` "returns no
       language list at all" holds for `linux_apt`, but the `macos_arm` and `windows` replies'
       gotchas now say *"Supported languages on macOS: Java and C# (official), Rust and
       TypeScript (community)"* (and the same for Windows). Correcting it contradicts the step's
       reasoning that the language set is platform-independent, which decides what the guide
       offers, so it is the maintainer's call.
  - **Tests.** Each test that pinned retired wording now asserts the corrected wording and has a
    negative control; none is deleted. `test_step2_record_type_contradiction.py` pins the retired
    note (its kept and retired sentences, with a mutation for each);
    `test_payload_key_collides_with_registered_feature.py` pins the cited routes and the routing
    owner, and rejects the observation-only label and the old owner;
    `test_the_2026_09_30_audit_rules_cite_their_invariants.py` moves its INV-280 row's phrase with
    the rule and rejects the old phrase; `test_quality_assessment_type_name_check.py` reads the
    new Retype wording, scopes its never-`MIXED` check to the Retype bullets (the rule line now
    says it too) and rejects "enum-valid"; `test_globalization_retrieval_strategy.py` finds the
    trap paragraph by the property it states rather than by a hit's name and rejects both retired
    claims; `test_license_env_var_absent.py` requires the license marker's stamp to postdate the
    lapse rather than pinning 1.39.0, and `test_loader_concurrency_reads_database_type.py` does
    the same for the out-of-sync marker (no older than 1.36.0). In `test_prescribed_search_queries.py`, the evidence slots
    re-measured here carry the new stamp, and the five whose reply moved are rewritten.
  - **Every assistant.** The change is guidance text, HTML-comment markers and one code comment;
    nothing names an assistant and nothing sits in a host marker.
    `python3 -m tools.bootcamp_build check` passes.
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. The tests read text and call no server. Verified on Linux
    only, with Python 3.12.3. The change carries no platform branch (INV-001) and names no
    programming language's own mechanism beyond what the markers quote (INV-002).
  - **Differs from the issue.** The issue counted 26 holds on 2026-11-17; on 2026-11-18, read at
    all ten hits, 25 hold, 10 are corrected and 2 are findings. The issue's line numbers are from
    an older commit. The issue named `test_mcp_call_contracts.py`; it needed no change.
- **Follow-up, drafted and not filed.** (1) `module-05-data-quality-mapping/SKILL.md`'s ⛔ line
  "a bare `search_docs(query="globalization")` does not reach this material" is looser than what
  the server returns (it reaches the UTF-8 section, below other sections); a rule line, so not
  edited here. (2) `phase2-data-mapping.md` rule 1 says `start` requires `data.workspace_dir`;
  the server now accepts `workspace_dir` at the top level or inside `payload`/`data`. The shown
  call still works, and changing the rule changes what the step tells the guide to do. (3) The
  two findings above.
- **Upstream:** not applicable. No server defect was found.
- **Invariants.** Establishes no new invariant, and no invariant's text needs a correction: the
  ⛔ (INV-280) rule keeps its instruction and citation, and INV-336's "the predominant
  post-retype type as `record_type`, never `MIXED`" still matches step 10. The register is not
  edited (INV-365).
- **Commit:** uncommitted

## the-kiro-install-page-and-location-note-contradict-the-kiro-package

- **Implemented:** 2026-11-17 (issue #42)
- **Files changed:** `hosts/kiro/fragments/site-before.html`, `hosts/kiro/host.json`,
  `tests/test_kiro_skills_say_where_they_are.py`, `tests/test_bootcamp_build_site.py`,
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes what one install page says about Python and the order in which one note tells
  the guide to look for the bootcamp's own files. Neither says anything about Senzing or
  about what the Senzing MCP server serves. Module 5's analyzer floor is not touched. No
  absence claim about the server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** The Kiro install page and the Kiro location note each said something the Kiro
  package does not do. Both now agree with it. These are findings 10 and 11 of
  `production-readiness-audit-2026-11-17`.
  - **The page.** The Python item in `hosts/kiro/fragments/site-before.html` is the text the
    issue gives, byte for byte: "Python 3, available as `python3` on the `PATH`", the sentence
    on the graduation recap and the optional hooks, and the Windows sentence the Claude,
    ChatGPT and Gemini pages carry. "3.10 or later" and "Any command name works" are gone.
    The page states no minimum Python version, because none is recorded for the bootcamp's
    own scripts and this change measured none.
  - **The note.** `options.skill_location_note` in `hosts/kiro/host.json` had two sentences
    for a bootcamp missing from the Kiro home, with no order between them, and none for a
    bootcamp found nowhere. They are replaced by one sequence. After "Read the files from
    there" the note says: if the bootcamp is not there, look in these places, in this order,
    and take the first one that holds the bootcamp as the bootcamp's directory.
    1. `powers/installed/senzing-bootcamp/` inside the directory `KIRO_HOME` names
    2. a `senzing-bootcamp` directory anywhere inside `powers/` in the directory `KIRO_HOME`
       names
    3. `powers/installed/senzing-bootcamp/` inside `.kiro` in the user's home directory
    4. a `senzing-bootcamp` directory anywhere inside `powers/` in `.kiro` in the user's home
       directory

    Then: places 1 and 2 apply only when `KIRO_HOME` is set, and when none of the four places
    holds the bootcamp the guide stops and tells the bootcamper that the bootcamp's files were
    not found. The sentence that forbids a search of the rest of the filesystem follows,
    unchanged.
  - **What the note keeps.** Everything before the sequence is unchanged: the bootcamp's
    directory and the skill's directory inside the Kiro home, what the Kiro home is with
    `%USERPROFILE%` named for Windows, and what "this skill directory", `<this-skill-dir>`,
    every `../` path and `${PLUGIN_ROOT}` resolve to. It is still one unwrapped line, stated
    once in each skill, with no `~` in it, and its ⛔ still cites INV-252 on that line.
  - **Decided here, because the issue gives the places and not the words.**
    - The note says "the directory `KIRO_HOME` names" where the issue says "the value of
      `KIRO_HOME`". The place is the same.
    - The guide takes the first place that holds the bootcamp "as the bootcamp's directory",
      so `${PLUGIN_ROOT}` and every `../` path follow the place that was found.
    - The sequence lists all four places although the location stated above it is already
      place 1 when `KIRO_HOME` is set and place 3 when it is not. One list in one order was
      preferred to a shorter list that depends on which case the reader is in.
    - The note has two conditions and each has one instruction: "If the bootcamp is not
      there" opens the sequence, and "If none of the four places holds the bootcamp" gives
      the stop.
  - **Built output.** A build of `6fe4627` and a build of this change were compared with
    `diff -r`. The Claude, Copilot, ChatGPT and Gemini packages are identical, and so are
    the three catalogs, the public pages and those four assistants' install pages. Nineteen
    files differ: the Kiro install page, at its Python item only, and the 18 Kiro `SKILL.md`
    files, each at its note line only.
  - **Tests.** `tests/test_kiro_skills_say_where_they_are.py` goes from 14 tests to 18 and
    `tests/test_bootcamp_build_site.py` from 7 to 9.
    - For every Kiro skill, the first module now asserts that the note states each of the
      four places once and in that order, that the sentence opening the sequence comes before
      them, that the sentence limiting places 1 and 2 comes after them, and that the stop is
      stated once, after the last place and before the ban on searching the filesystem. It
      asserts that the two replaced sentences are gone and that the note's conditions are
      exactly the two above. The assertions for INV-252's note are kept as they were: the
      two directories, the Kiro home, what each reference resolves to, the two sentences on
      searching, no `~`, and one note on one line in each skill.
    - Negative controls run on every pass against the built note: places 2 and 3 exchanged,
      the home directory put before `KIRO_HOME`, the last place taken out, the stop taken
      out, the stop moved before the places, and the stop given twice. Each is reported.
    - The second module gains one test over every assistant `load_hosts()` returns. It reads
      each built install page, requires `<code>python3</code> on the <code>PATH</code>` and
      refuses "Any command name works". It fails when it read no assistant (INV-265). A
      second test holds the Kiro page to the item above, once, and to no "3.10 or later".
    - Negative control run once, on an export of `6fe4627` holding only the two changed test
      files. The site module reports `FAILED (failures=2)`: the all-assistants test fails for
      Kiro alone, and the Kiro test fails. The Kiro module reports `FAILED (failures=55)`:
      the three new assertions fail for each of the 18 skills, and the control test fails.
  - **Not observed.** No run on Kiro was made, so `hosts/kiro/checks.json` and
    `options.skill_location_sources` are unchanged. The tests read the words of the note and
    of the pages. They do not show which place a guide looks in first, that Kiro honors
    `KIRO_HOME`, or that `python3` is on any bootcamper's `PATH`. No recorded run tested
    `KIRO_HOME`. Verified on Linux only, with Python 3.12.3. The change is text and two test
    modules that use the standard library and have no branch on the platform (INV-001).
  - **Compatibility.** An installed Kiro Power keeps the old note until it is updated. The
    published Kiro page changes at the next promotion.
  - **Found and not changed, as out of scope. Each is drafted here and not filed.**
    1. **Not filed.** *The Kiro hooks-setup skill does not say which command starts the
       installer.* `hosts/kiro/files/skills/bootcamp-hooks-setup/SKILL.md` says to run the
       installer "with the Python interpreter the bootcamp uses for its own scripts" and
       writes the command as `<python> …/install_hooks.py`. The package's other commands
       name `python3`, and the page now requires `python3` on the `PATH`. The issue puts
       this skill out of scope. The question for the maintainer is whether the skill should
       name `python3` as the rest of the package does.
    2. **Not filed.** *The note does not say which copy to take when `powers/` holds more
       than one `senzing-bootcamp`.* Places 2 and 4 look anywhere inside `powers/`. The issue
       puts this out of scope, and the note still does not say.
- **Invariants.** The register is not edited here (INV-365). The change rewords one
  hard-rule line, the note's, and it still cites INV-252 on its own line:
  `conformance.py since --since-last-audit` reports it outside the corpus, and the
  cited-or-deferred gate checks it at its whole source line. The change ships two rules the
  register does not hold, each stated in one ⛔ line of a test's docstring. `since` does not
  report those, because `tests/` is not a rule home. The two blocks below cover them
  (INV-309). The first is an amendment and not a new rule because the order and the stop
  belong to the note INV-252 already governs. The issue says INV-252 holds as written and
  puts the register's text out of scope, so that block changes nothing there: it drafts the
  dated note that would bind the order and the stop, for the maintainer to apply or hold.
  Until then only the test holds them. The second is a new rule because no registered
  invariant says what an install page tells a reader about Python.

- **PROPOSED AMENDMENT to INV-252 — applied 2026-11-18 by the maintainer.**
    - ⛔ **If the bootcamp is not there, look in these places, in this order, and take the first one that holds the bootcamp as the bootcamp's directory** — in `hosts/kiro/host.json`
    - ⛔ **If none of the four places holds the bootcamp, stop and tell the bootcamper that the bootcamp's files were not found.** — in `hosts/kiro/host.json`

  INV-252, as amended on 2026-11-16 (issue #11), defines the Kiro home and forbids a search
  of the filesystem. It gives no order of places to look when the bootcamp is not at the
  stated location, and nothing for a bootcamp that is in none of them. The note that shipped
  under it had two sentences for one condition and no order between them. Without the note
  below, a later edit can put two unordered fallbacks back, or take the stop out, and
  contradict no registered rule. Enforced by `tests/test_kiro_skills_say_where_they_are.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-252** — (⚠️ **Dated note, 2026-11-17 (#42): a location note gives one order of places to look and ends in a stop; the Kiro home, the per-platform record and the ban on searching the filesystem above are unchanged.** Where a package's location note says where to look when the bootcamp is not at the location it states, it MUST give the places as one ordered sequence, tell the guide to use the first place that holds the bootcamp, and, after the last place, tell the guide to stop and tell the bootcamper that the bootcamp's files were not found. No condition in the note MAY carry two instructions. On Kiro the order finishes one Kiro home before the next: (1) `powers/installed/senzing-bootcamp/` inside the directory `KIRO_HOME` names; (2) a `senzing-bootcamp` directory anywhere inside `powers/` in the directory `KIRO_HOME` names; (3) `powers/installed/senzing-bootcamp/` inside `.kiro` in the user's home directory; (4) a `senzing-bootcamp` directory anywhere inside `powers/` in `.kiro` in the user's home directory. Places 1 and 2 apply only when `KIRO_HOME` is set. The note does not say which copy to take when `powers/` holds more than one `senzing-bootcamp`. Enforced by `tests/test_kiro_skills_say_where_they_are.py`, which reads the order the note states in every built Kiro skill and **cannot** establish which place a guide looks in first, or whether Kiro honors `KIRO_HOME`: on 2026-11-17 no run recorded in `hosts/kiro/checks.json` tested `KIRO_HOME`.)

- **DEFERRED INVARIANT (resolved INV-433, registered by the maintainer 2026-11-18).** Every assistant's install page states the Python requirement its package relies on. The rule already shipping, quoted:
    - ⛔ **Every assistant's install page states the Python requirement its package relies on: `python3` on the `PATH`.** — in `tests/test_bootcamp_build_site.py`

  Enforced by `tests/test_bootcamp_build_site.py`.

  **Why it is not an existing invariant:** INV-052 says a hook is invoked as `python3`, and
  binds the package. An install page is in no package. INV-428 and INV-429 bind what an
  install page says about a model and an effort. INV-347 gives Module 5's analyzer a floor
  of its own and checks it there. None of them says what a page tells a reader about Python
  before the install, so the Kiro page said "Python 3.10 or later" and "Any command name
  works" and contradicted no registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Every assistant's install page (its "before you start" list, `hosts/<assistant>/fragments/site-before.html`) MUST state the Python requirement the assistant's package relies on, `python3` on the `PATH`, in the words `<code>python3</code> on the <code>PATH</code>`, and MUST NOT say that any command name works. Each package runs the bootcamp's bundled scripts as `python3`, so a `python` or `py` command alone does not meet the requirement, and a page MAY say how to add a `python3` entry where only one of those is installed. Enforced by `tests/test_bootcamp_build_site.py`, which reads the built install page of every assistant `load_hosts()` returns and fails when it read none (INV-265). It reads each page's words and **cannot** establish that `python3` is on a bootcamper's `PATH`. It does not report a page that states a minimum Python version: none is recorded for the bootcamp's own scripts, only the Kiro page is held to not saying "3.10 or later", and Module 5's analyzer floor is INV-347's. (Source: `the-kiro-install-page-and-location-note-contradict-the-kiro-package`, GitHub issue #42, 2026-11-17.)

- **An older entry edited, with the maintainer's yes (2026-11-18).** The applied
  `PROPOSED AMENDMENT to INV-252` block in `the-kiro-package-states-its-installed-path-for-linux-only`
  quoted the note sentence this issue removes, so `tests/test_deferral_quotes_match_their_source.py`
  failed. Its quote is shortened to the leading sentence, `(INV-252) Read the files from there.`,
  which still ships. Nothing else in that entry changed, and the applied note in
  `specs/INVARIANTS.md` is untouched. The unattended run stopped here because a run may not
  edit another entry; the maintainer approved this edit on issue #42's resume.
- **Commit:** uncommitted

## maintainer-documents-and-skills-describe-tools-and-guards-that-are-not-here

- **Implemented:** 2026-11-18 (issue #48)
- **Files changed:** `README.md`, `.claude/CLAUDE.md`, `tests/README.md`,
  `docs/model-selection.md`, `tools/bootcamp_build/render.py` (module docstring),
  `tools/bootcamp_build/model.py` (`Host.fragment_path` docstring),
  `.claude/skills/production-readiness-audit/SKILL.md`,
  `.claude/skills/production-readiness-audit/conformance.py`,
  `.claude/skills/compact-dev-environment/SKILL.md`,
  `.claude/skills/delegate-to-mcp-server/SKILL.md`, `.claude/skills/dry-run/SKILL.md`,
  `.claude/skills/review-invariants/SKILL.md`,
  `.claude/skills/review-invariants/pending_invariants.py` (one comment),
  `.claude/skills/release/SKILL.md`, `tests/test_conformance_scans.py`, `specs/IMPLEMENTED.md`
  (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-18 against the change
  itself: it corrects what maintainer documents, skills, docstrings and help text say about this
  repository's build, tests, ledger and promotion, and adds one output line to two audit scans.
  It states nothing about the Senzing SDK, the Senzing MCP server or any Senzing behavior. No
  MCP tool was called.
- **Summary:** findings 30, 31 and 32 of `production-readiness-audit-2026-11-17`. Every
  statement the issue lists now says what the repository does today, read at `7f41ed1` after
  the earlier merges of this run.
  - **Layout documents.** `README.md` and `.claude/CLAUDE.md` name `host:except` beside
    `host:only`. `README.md` no longer says text outside a marker is copied unchanged: it says
    the build also changes such text and names each case `tools/bootcamp_build/emit.py` makes,
    a command built as a skill (the `name:` line, `../skills/` rewritten to `../`, the
    sibling-skills note), the `skill_location_note` appended to every `SKILL.md`, and, since
    #39, the read-to-the-end note at the top of every package Markdown file over
    `READ_CUT_CHARACTERS` outside the docs directory. The `render.py` docstring agrees with it.
    `check`'s list says names of an assistant are counted against the ceilings in
    `tools/bootcamp_build/neutrality.json` and fail above a ceiling or below it until it is
    lowered, and names the skill frontmatter problems `skill_problems()` reports.
    `tests/README.md` says the build never puts the tests in a package.
    `Host.fragment_path`'s docstring says `hosts/_shared/fragments/` is optional and absent,
    with no code change. `docs/model-selection.md` says every skill under `source/skills/` has a
    row and the five commands have none; no row is added.
  - **Skills.** The five sentences that cited `tests/test_specs_are_frozen.py` or
    `specs/FROZEN-MANIFEST.txt` keep their rule (no new file under `specs/`, INV-307), cite the
    table in `specs/README.md` as the list of files that belong there, and say the frozen
    archive of the spec files is in the repository that file names. None says a test rejects a
    file. The three `propagate.sh` sentences name `python3 -m tools.bootcamp_build promote` and
    the four kinds of path `promote.py`'s docstring lists. `release/SKILL.md` no longer names
    `tests/test_maintainer_tooling_stays_out_of_public.py` or claims a test enforces the rule.
    `compact-dev-environment` keeps its root location for `RENUMBERING.md`, its warning against
    `docs/` now giving today's reason. The `pending_invariants.py` comment says the manifest is
    not here and `frozen_names()` returns an empty set; its code is unchanged. The issue's
    search prints exactly its two lines: `conformance.py:614` and the `FROZEN_MANIFEST =`
    assignment.
  - **The audit tool.** `production-readiness-audit/SKILL.md` and the `--since-last-audit` help
    of `since` and `reverse-check`, now one constant `SINCE_LAST_AUDIT_HELP`, say the range
    starts at the newest audit entry whose `Commit:` names a commit here and otherwise at the
    `Fallback commit` line of `specs/IMPLEMENTED.md`, with a `FALLBACK` line printed. No hash is
    copied (INV-432). `duplication` prints `CORPUS: source (<n> file(s)) — and .md only.` and
    `size` prints a `CORPUS:` line naming `source`'s `.md` files and the `.py` files directly
    under `source/scripts`, on every run (INV-431, INV-308). Both read the same files as before,
    so their recorded figures do not move.
  - **Tests.** `TestDuplicationAndSizeNameTheRootTheyRead` in `tests/test_conformance_scans.py`
    asserts both lines on fixture runs that find nothing (no repeated passage; no Markdown
    file), on a fixture with a bundled script, and on the live repository.
  - **One wording found by a guard.** "the frozen spec archive" read to
    `tests/test_compact_dev_environment_leaves_specs_frozen.py` as an instruction to archive a
    spec, so every site says "the frozen archive of the spec files" instead.
  - **Not changed.** `specs/INVARIANTS.md` (INV-365); any file under `source/`, `hosts/`,
    `site/` or `public/`, so no assistant's package changes. No run on a real assistant was
    made, so nothing is added to any `hosts/<assistant>/checks.json`. Verified on Linux only,
    with Python 3.12.3; the change is prose, docstrings, help text and two `print` lines, and
    the new test uses `tempfile` and `subprocess` with `sys.executable`, which hold on macOS and
    Windows too.
- **Invariants.** The register is not edited here (INV-365). This entry establishes no new
  invariant. The new `CORPUS:` lines meet INV-431, already registered, and the help text states
  INV-432. Six registered invariants name a guard or a tool this repository does not carry, so
  this entry queues six `PROPOSED AMENDMENT` blocks below, each a dated note of facts only. None
  proposes a change to a requirement, and none retires an invariant: that is the maintainer's
  decision in `/review-invariants`.

- **PROPOSED AMENDMENT to INV-304 — applied 2026-11-18 by the maintainer.**
    - ⛔ **This skill is development-repo only and must NOT be propagated to the public plugin repo.** — in `.claude/skills/release/SKILL.md`

  INV-304 governs "the propagate mirror" and names `propagate.sh` and its enforcer
  `tests/test_maintainer_tooling_stays_out_of_public.py`. Neither is in this repository, and
  `tests/test_invariant_enforcer_citations.py` lists the test as not carried. Without a note,
  the register describes a mirror nobody runs, and #48 found a skill still citing the absent
  test as the reason the rule is "enforced rather than remembered".

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-304** — (⚠️ **Dated note, 2026-11-18 (#48): `propagate.sh` is not in this repository;
  no requirement changes.** Since the one-repository migration of 2026-11-14, promotion is
  `python3 -m tools.bootcamp_build promote`, which writes only the paths the docstring of
  `tools/bootcamp_build/promote.py` lists: every assistant's package under `plugins/`, each
  assistant's catalog file, `docs/` from `site/`, and each file under `public/` at the same path
  from the root. The enforcer named above, `tests/test_maintainer_tooling_stays_out_of_public.py`,
  is not carried into this repository.)

- **PROPOSED AMENDMENT to INV-307 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Never write a new file under `specs/`.** — in `.claude/skills/production-readiness-audit/SKILL.md`

  INV-307 requires the frozen set to be pinned in `specs/FROZEN-MANIFEST.txt` and names
  `tests/test_specs_are_frozen.py` as its enforcer. Neither the manifest, the archived spec
  files nor the test is in this repository, and `tests/test_invariant_enforcer_citations.py`
  lists the test as not carried. Five skill sentences cited the test as rejecting a new file
  under `specs/`, which no test here does; #48 corrected them, and without a note the register
  still says the opposite.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-307** — (⚠️ **Dated note, 2026-11-18 (#48): the frozen archive and its manifest are not
  in this repository; no requirement changes.** Since the one-repository migration of
  2026-11-14, `specs/` holds live records only, listed in the table in `specs/README.md`, and
  the frozen archive is the repository and commit that file names. `specs/FROZEN-MANIFEST.txt`
  and the archived spec files are absent here. The enforcer named above,
  `tests/test_specs_are_frozen.py`, is not carried into this repository.)

- **PROPOSED AMENDMENT to INV-350 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Promotion writes exactly those paths and nothing else, and it stops at the working tree: no commit, no branch, no push.** — in `tools/bootcamp_build/promote.py`

  INV-350 governs the files `propagate.sh` publishes and its rewrite pass, and names
  `tests/test_propagate_publishes_the_pages_site.py` as its enforcer. The script, its rewrite
  pass and the test are not in this repository; `tests/test_invariant_enforcer_citations.py`
  lists the test as not carried. Without a note, the register describes a publishing step that
  no longer runs.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-350** — (⚠️ **Dated note, 2026-11-18 (#48): `propagate.sh` and its rewrite pass are not
  in this repository; no requirement changes.** Since the one-repository migration of
  2026-11-14, promotion is `python3 -m tools.bootcamp_build promote`. The enforcer named above,
  `tests/test_propagate_publishes_the_pages_site.py`, is not carried into this repository.)

- **PROPOSED AMENDMENT to INV-351 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Promotion writes exactly those paths and nothing else, and it stops at the working tree: no commit, no branch, no push.** — in `tools/bootcamp_build/promote.py`

  INV-351 requires this repository's marketplace to carry its own name and `propagate.sh` to
  rewrite it, and names `tests/test_propagate_publishes_the_published_marketplace_name.py` as
  its enforcer. This repository has no marketplace catalog of its own, and the script and the
  test are not here; `tests/test_invariant_enforcer_citations.py` lists the test as not
  carried. Without a note, the register describes a rename and a rewrite that no longer exist.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-351** — (⚠️ **Dated note, 2026-11-18 (#48): `propagate.sh` is not in this repository,
  and neither is a marketplace catalog of this repository's own; no requirement changes.**
  Since the one-repository migration of 2026-11-14, promotion is
  `python3 -m tools.bootcamp_build promote`. The enforcer named above,
  `tests/test_propagate_publishes_the_published_marketplace_name.py`, is not carried into this
  repository.)

- **PROPOSED AMENDMENT to INV-360 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Bootcampers install from the public repository, [Senzing/bootcamp].** — in `README.md`

  INV-360 requires this repository's install surfaces to name the development repository and
  relies on `propagate.sh`'s slug rewrite. Nobody installs from this repository, the script is
  not here, and its enforcer, `tests/test_dev_install_surfaces_name_the_dev_repo.py`, is
  present but retired by its own dated note of 2026-11-14. Without a note, the register states
  a requirement its own enforcer has recorded as no longer applying.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-360** — (⚠️ **Dated note, 2026-11-18 (#48): INV-360 no longer applies; this note is
  the review it asks for.** This repository has no install surface that bootcampers install
  from, and `propagate.sh` and its slug rewrite are not in it. Since the one-repository
  migration of 2026-11-14, every install page is generated for the public repository,
  `Senzing/bootcamp`, and `README.md` names that repository. The enforcer named above,
  `tests/test_dev_install_surfaces_name_the_dev_repo.py`, is present and records its own
  retirement in its dated note of 2026-11-14.)

- **PROPOSED AMENDMENT to INV-380 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Every deliverable INV-050's tree annotates as always produced MUST be named on at least one user-facing surface, and a deliverable it annotates as produced only on the Bootcamper's yes MUST be named there as an offer rather than as something they finish with.** — in `tests/test_always_produced_deliverables_are_named.py`

  INV-380 says its enforcer derives the surfaces "from `propagate.sh`'s published roots". The
  script is not in this repository. The enforcer,
  `tests/test_always_produced_deliverables_are_named.py`, is present and was adapted on the
  migration to read the build's published roots instead. Without a note, the register names
  a source of surfaces the guard no longer reads.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-380** — (⚠️ **Dated note, 2026-11-18 (#48): `propagate.sh`'s published roots are not in
  this repository; no requirement changes.** Since the one-repository migration of 2026-11-14,
  the published roots are the build's `public/` and `site/`. The enforcer named above,
  `tests/test_always_produced_deliverables_are_named.py`, is present and was adapted to read
  them.)

- **Commit:** uncommitted

## inv-050-says-config-license-json-is-written-in-module-4-module-2-writes-it-first

- **Implemented:** 2026-11-18 (issue #41)
- **Files changed:** `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-18 against the change
  itself: it adds this entry and nothing else. The entry says which steps of the bootcamp
  write `config/license.json` and quotes the bootcamp's own text. Where its note names the
  `get_license` response, it names what Step 5a already saves; it states nothing about what
  that call returns or how the SDK behaves. No MCP tool was called.
- **Summary:** INV-050's layout tree annotates `config/license.json` "(written in Module 4)",
  and its 2026-07-28 correction says "Module 2 only reads the detected limit". Module 2 Step 5a
  saves the `get_license` response to that file, and Module 4 Step 8a sub-step 7 saves it again
  (`production-readiness-audit-2026-11-17`, finding 9). The shipped behavior is right and the
  invariant's text is stale, so this entry queues the `PROPOSED AMENDMENT to INV-050` block
  below for `/review-invariants`. Nothing else changes.
  - **The block** quotes Step 5a's sentence, "Save the returned JSON to `config/license.json`,
    because later steps read it.", verbatim from `source/skills/module-02-sdk-setup/SKILL.md`
    as it stands after #35 and #40. It carries the issue's dated note with `<date>` set to
    2026-11-18, and the issue's replacement for the `license.json` line of INV-050's tree,
    byte for byte.
  - **Checked.** `python3 .claude/skills/review-invariants/pending_invariants.py check`
    resolves the quote: 42 rule quotes checked, 0 mismatched, 0 unresolved, 0 unparsed (41
    checked before this entry). `list` shows the block as pending, with
    `AMENDS INV-050 — already registered`; the pending count goes from 31 to 32.
  - **No test is added**, as the issue's scope says: the queue's existing checks cover the
    block, and `tests/test_deferral_quotes_match_their_source.py` fails if Step 5a's sentence
    stops shipping verbatim.
  - **Not changed.** `specs/INVARIANTS.md` (INV-365), and no file under `source/`, so no
    assistant's package changes. No run on a real assistant was made, so nothing is added to
    any `hosts/<assistant>/checks.json`. Verified on Linux only, with Python 3.12.3. The change
    is Markdown text in the maintainer's ledger and names no operating system's or programming
    language's mechanism.
- **Invariants.** The register is not edited here (INV-365). This entry establishes no new
  invariant: the rule it concerns is INV-050, already registered, and the block below proposes
  a dated note on it and a corrected comment on one line of its tree. The note cites INV-244
  and INV-295, which Step 5a already applies, and changes neither.

- **PROPOSED AMENDMENT to INV-050 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Save the returned JSON to `config/license.json`, because later steps read it.** — in `source/skills/module-02-sdk-setup/SKILL.md`

  INV-050's tree annotates `config/license.json` "(written in Module 4)", and its 2026-07-28
  correction says license detection moved to Module 4 and "Module 2 only reads the detected
  limit". Module 2 Step 5a now measures the license with no prompt, saves the response to the
  file as a provisional reading, and writes nothing when it cannot measure; Module 4 Step 8a
  sub-step 7 measures again, with the engine configuration in force, and saves the file again.
  Without the note below, the register tells the next editor that Module 2 writes no license
  file, and an edit made to agree with it would remove Step 5a's save, which the step's own
  field-name fallback reads (INV-115). The file and its purpose are unchanged. No test pins
  which module writes the file: `tests/test_invariant_layout_tree.py` (INV-202) checks only
  that the tree's entry is referenced under `source/`, so this block names no enforcer.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-050** — (⚠️ **Dated note, 2026-11-18 (#41): `config/license.json` is first written in Module 2; the
  file and its purpose are unchanged.** SDK setup (Module 2) Step 5a saves the `get_license`
  response to `config/license.json` as a provisional reading (INV-295), and writes nothing
  when it cannot measure (INV-244). Data collection (Module 4) Step 8a sub-step 7 saves it
  again when that step measures, with the engine configuration in force. The 2026-07-28
  correction's "Module 2 only reads the detected limit" no longer holds, and the tree's
  annotation "(written in Module 4)" on the `license.json` line is read as "written in
  Module 2, rewritten in Module 4"; the tree line itself is left as it is. The rules above
  still bind.)

  **Amended at review, 2026-11-18:** the maintainer chose the note alone, so the register stays
  append-only. The draft also asked for the tree line to be rewritten in place; that part was
  struck, and the note above says how to read the annotation instead.

- **Commit:** uncommitted

## module-2-gives-two-install-routes-on-windows-with-python-and-no-step-chooses

- **Implemented:** 2026-11-18 (issue #40)
- **Files changed:** `source/skills/module-02-sdk-setup/SKILL.md`,
  `tests/test_windows_python_route_is_chosen.py` (new),
  `tests/test_rule5_takes_the_distro_criterion_from_the_server.py`, `specs/IMPLEMENTED.md`
  (this entry)
- **MCP re-check:** server 1.46.1, docs index built 2026-11-14 17:44 UTC, 2026-11-18 — n/a (no
  Senzing fact) for the text this change adds, re-confirmed against the diff: it states what
  makes a container or WSL2 present on the Bootcamper's machine (`docker version`,
  `podman version`, `wsl --list --verbose`), the pinned question, and where the route is
  recorded. None of that is a Senzing fact. The two platform tokens the question resolves to,
  `platform='docker'` and `platform='linux_apt'`, are the ones rule 1 already named, and are not
  changed. Rule 1's existing server quotation, which this change keeps and does not re-stamp,
  was re-asked as the lead's plan asked, and still reproduces. Tools: `get_capabilities`,
  `sdk_guide`, `search_docs`, read-only, at the default result count:
  - `get_capabilities()` gives `"server_version":"1.46.1"`. The index build is not in that
    reply; `search_docs` gives it: `"index_built":"2026-11-14 17:44 UTC"`,
    `"documents_indexed":13404`.
  - `sdk_guide(topic='install', platform='windows', language='python')` returns as its only
    `compatibility_notes` entry: "The Senzing Python SDK is ONLY supported on Linux. … (2) Pick
    a different environment — use Docker or WSL2 to run Python inside a Linux container." Its
    `next_steps` names `sdk_guide(topic='install', platform='docker', language='python')`. Rule
    1's quotation, *"use Docker or WSL2 to run Python inside a Linux container"* (server
    1.33.0, 2026-08-21), still matches word for word, so its stamp is left as it is.
  - `search_docs(query='Python SDK Windows WSL2 Linux container')` returns the v4 Windows
    Quickstart as hit 1, and its "Start developing" section as hit 5: "The Python SDK is
    supported on Linux only. To use it, follow the v4 Docker Quickstart" (link markup left out
    here). Nothing in the change rests on this reply; it was asked to see whether the server
    now names one of the two routes as preferred, and the `sdk_guide` reply above, the route
    rule 1 cites, names both.
- **Summary:** On Windows with Python, Module 2 named two Linux environments, a container and
  WSL2, and no step chose between them; the "Agent Behavior" bullet at the end of the file
  said "Do NOT offer alternatives", which read literally forbade the WSL2 route
  (`production-readiness-audit-2026-11-17`, finding 6). Step 2 now resolves one route.
  - **Rule 1 states the procedure, in order.** A `route` already recorded under step 2 in
    `config/bootcamp_progress.json` (`container` or `wsl2`) is taken, with no probe and no
    question (INV-006). Otherwise the guide checks what is present: a container when
    `docker version` or `podman version` answers, the probe Step 7 makes before its PostgreSQL
    question; WSL2 when `wsl --list --verbose` lists a distribution whose VERSION is 2, a WSL 1
    distribution not counting. Exactly one present: the guide takes it and says so in one line
    with the reason, in the "say so if that's wrong" form Step 2 uses for the detected
    platform, and asks nothing. Both or neither: it says what it found and asks the route
    question once. A guide already inside WSL2 detects Linux and reaches rule 5; macOS keeps
    the container route with no probe and no question.
  - **The route question** is pinned verbatim after the routing rules, as the issue gave it:
    "Which Linux environment would you like to run the Senzing SDK in? Reply with a number:",
    options "1. A container" and "2. WSL2", a neutral lead and a numbered list (INV-051,
    INV-056), ending the turn (INV-251). Its `**Handling each answer (INV-284).**` block
    resolves 1 to `platform='docker'` and 2 to `platform='linux_apt'`, records the route, then
    checkpoints step 2 and continues to Step 3. When neither was present, the answer still
    decides the route and Step 3 proceeds as it does today.
  - **The checkpoint** now records rule 1's `route` under step 2, the way Step 1b records its
    outcome under step 1. A resumed session, and the `sdk_repair` detour that re-runs Step 2,
    read it there and neither probe nor ask.
  - **The tail bullet** now reads: install the SDK on the route Step 2's routing rules
    resolve, natively, in a container, or in WSL2 where rule 1 chooses it; offer no route
    those rules do not resolve; the one choice they leave to the Bootcamper is rule 1's route
    question, on Windows with Python.
  - **Kept.** The routing rules keep their ordinals 1 to 5, which
    `bootcamp-preparation/SKILL.md` indexes by number, and both anchors
    `tests/test_language_gate_names_the_cost.py` cuts on. The new presence probes are written
    as prose, as `docker version` is at Step 7, so no new guide-run block is added. The
    language gate in `bootcamp-preparation/SKILL.md` is not edited, and that file's
    `TheProbeIsNotClaimed` boundary, which is about the language gate, still holds.
  - **Tests.** `tests/test_windows_python_route_is_chosen.py`, 8 tests. Five checks, each a
    function returning problems: rule 1 states the procedure's steps in order, and that the
    exactly-one branch asks nothing; the question is pinned verbatim once, in Step 2, with
    exactly its two options and a handling entry for each that resolves the platform and
    records the route, and its handling checkpoints step 2 and continues to Step 3; the
    checkpoint records the route; the "Agent Behavior" section does not say "do not offer
    alternatives" and carries a bullet deferring to the routing rules; and no routing rule
    carries a 👉, rules 1 to 5 stand in order, no rule other than rule 1 leads to the route
    question, and Step 2 holds exactly two 👉 questions. Seven negative controls run on
    in-memory mutants of the shipped file on every pass: rule 1 without its procedure, the
    exactly-one branch asking, a lost handling entry, a reworded question, an unrecorded
    route (in the handling entry and in the checkpoint), the tail bullet as it shipped before
    this change, and a question on rule 4. Prose is matched with whitespace collapsed
    (INV-346).
  - **`tests/test_rule5_takes_the_distro_criterion_from_the_server.py`**:
    `test_step_two_still_asks_exactly_one_question` asserted Step 2 carries exactly one 👉,
    which this issue's own scope changes. It now asserts exactly two, that the second is the
    route question, and that rule 5 carries none, so its rule-5 purpose still holds. A dated
    note in its docstring says why.
  - **Every assistant.** The changed text sits outside every host marker and names no
    assistant; `python3 -m tools.bootcamp_build check` passes.
  - **Not observed.** No run on a real assistant was made, so nothing is added to any
    `hosts/<assistant>/checks.json`. The tests read Markdown: they cannot show that a live
    guide runs the probes or reads `wsl --list --verbose` correctly. Verified on Linux only,
    with Python 3.12.3. The change is Markdown text and standard-library tests (INV-001); it
    binds Python because the server's Linux-only statement is about the Python SDK, and states
    no programming language's own mechanism (INV-002).
  - **Not changed (out of scope, per the issue).** Who installs a missing Docker Desktop or
    WSL2, and how a guide on native Windows runs commands inside WSL2.
- **Invariants.** The register is not edited here (INV-365). The lines this change adds or
  edits under `source/` and `tests/` carry no ⛔ and no bold MUST, NEVER or ALWAYS, and
  `conformance.py since --since-last-audit` reports none from this change. The behavior it
  ships applies invariants already in force to one step: a recorded answer is not asked
  again (INV-006), a detection is preferred to a question (INV-012), the question is pinned
  with a neutral lead and a numbered list (INV-009, INV-051, INV-056), it is the turn's one 👉
  question (INV-251), and each option has a handling entry (INV-284). Which route Module 2
  takes on Windows with Python is a product decision recorded in the issue, guarded by the
  test above, not a standing rule across the bootcamp. Establishes no new invariant.
- **Commit:** uncommitted

## the-senzing-mcp-server-returns-the-bootcamps-own-repositories-as-senzing-examples

- **Implemented:** 2026-11-18 (issue #37)
- **Files changed:** `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/module-06-data-processing/phaseC-multi-source.md`,
  `tests/test_prescribed_search_queries.py`,
  `tests/test_bootcamp_repository_results_are_not_senzing_sources.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** server 1.46.1, docs index built 2026-11-14 17:44 UTC, 2026-11-18 — still
  reproduces, as the issue recorded on 2026-11-17, with one detail different (the first item of
  "Differs from the issue" below). Tools: `get_capabilities`, `find_examples`,
  `generate_scaffold`, `search_docs`, read-only, each at its default result count.
  `submit_feedback` and `download_resource` were not called. Every call was made before any
  file was changed.
  - `get_capabilities()` gives `"server_version":"1.46.1"`. The index build is in the
    `search_docs` reply: `"index_built":"2026-11-14 17:44 UTC"`, `"documents_indexed":13404`.
  - `find_examples(query='multi-source')` returns two examples, `"repo":"senzing/senzing-bootcamp-claude-plugin"`
    and `"repo":"senzing/senzing-bootcamp-kiro-power"`, each `"file_path":"CHANGELOG.md"` and
    each `"provenance":"official"`. With `language='java'` it returns `"examples":[]` and
    `"hint":"No examples found for \"multi-source\". …"`.
  - `find_examples(query='orchestrator load multiple data sources')` returns one example per
    repository, led by `senzing/code-snippets-v4` `java/snippets/configuration/RegisterDataSources.java`,
    with `"remainder":"Returned 34 of 46 examples. …"`. Among them:
    `senzing/senzing-bootcamp-claude-plugin` `CHANGELOG.md`,
    `senzing/senzing-bootcamp-chatgpt-plugin` `plugins/senzing-bootcamp/scripts/generate_recap_video.py`,
    `senzing/senzing-bootcamp-kiro-power` `senzing-bootcamp/skills/bootcamp-enforcement-setup/scripts/install_hooks.py`,
    and `senzing/recipes` `recipes/clair-data-ingestion-starter.md`, whose snippet reads "PPP
    relief loans and Department of Labor violations, with a third folded in later". With
    `language='python'` the bootcamp scripts come back again and the recipe does not; with
    `language='java'` neither does.
  - `generate_scaffold(language='python', workflow='orchestration')` is rejected: "Unknown
    workflow 'orchestration'. Available workflows: initialize, configure, add_records, delete,
    query, redo, stewardship, information, error_handling, full_pipeline. …".
  - `generate_scaffold(language='python', workflow='full_pipeline')` and the same call with
    `language='java'` list `python/loading/add_truthset_loop.py` and
    `java/snippets/loading/LoadTruthSetWithInfoViaLoop.java`. Each file was fetched from its
    hosted `url` and its SHA-256 equals the reply's `hash` (`2d50ac81…` and `c8a00643…`). The
    Python loader reads three files from `INPUT_FILES` in one loop and has
    `except (SzUnrecoverableError, SzError) as err: raise err`; the Java loader has the same
    three files and `throw e; // rethrow since exception is critical`.
  - `search_docs(query='NEED_REEVALUATION how entity final state')` ranks first a hit with
    `"title":"senzing/senzing-bootcamp-chatgpt-plugin: plugins/senzing-bootcamp/scripts/bootcamp_state.py"`
    and `"source_url":"https://github.com/senzing/senzing-bootcamp-chatgpt-plugin/blob/main/…"`.
  Two statements this change ships are absence claims, so (INV-213):
  owner-checked: `search_docs` is the route that returns the hit, and the hit object is all
  it says about one — it returned `title`, `section`, `excerpt`, `source_url`, `category`,
  `version` and `relevance_score`, and no `repo`.
  owner-checked: `find_examples` is the route for indexed example code and `generate_scaffold`
  the route for SDK templates — the first returned no code that loads several sources with
  per-source error isolation, and the second has no orchestration workflow and its nearest
  code rethrows a critical error and ends the run.
- **Summary:** The server's example and documentation corpus indexes the bootcamp's own
  repositories, and no shipped text said such a hit is not Senzing evidence
  (`dry-run-2026-11-17`, finding 5).
  - **The rule.** `ground-rules.md`, in "MCP-first invariant (absolute precedence)", gains one
    bullet after "Tool routing": "A result from a bootcamp repository is not a Senzing source
    (INV-080)." It says an MCP result that names its repository is disregarded when the
    repository's name contains `bootcamp`, compared without regard to case; where the name is
    read (the `repo` field of a `find_examples` hit; the `title` and `source_url` of a
    `search_docs` hit, which has no `repo` field); that a `search_docs` hit whose `source_url`
    is not a repository's address is not touched; that it is a property of the name, so a
    repository added or renamed later is covered; that the rest of the hits are used as before
    when some are disregarded; and that when every hit is, the call counts as having returned
    no Senzing example, the step continues on its existing fallback and nothing is said to the
    bootcamper. It names `find_examples` and `search_docs` as the observed cases, dated server
    1.46.1, docs indexed 2026-11-14 17:44 UTC, 2026-11-18. It is stated there once and pointed
    at from the marker below; no other file restates it (INV-300).
  - **A marker for the rule.** "which has no `repo` field" is a dated statement of what a reply
    lacks, and `tests/test_coverage_reports.py` failed on it until a marker sat beside it. The
    marker, under the rule, names `search_docs(query='NEED_REEVALUATION how entity final state')`
    and is stamped server 1.46.1, 2026-11-18.
  - **The orchestrator marker.** In `phaseC-multi-source.md`, Step 17, the claim is unchanged
    and still holds. The rationale is restated from the calls above: 'multi-source' surfaces
    changelogs of bootcamp repositories, which are not Senzing sources, with a pointer to the
    ground rules' MCP-first section, and no Senzing example code; with `language='java'` it
    returns no example; the orchestrator query surfaces kinds of hits, among them scripts from
    bootcamp repositories, and the `senzing/recipes` recipe as the nearest. The owner clause
    says `find_examples` "returned no such code" where it said "returned none". The stamp is
    server 1.46.1, 2026-11-18. It names no repository whose name holds an assistant's name.
    `coverage_reports.py negatives` parses it and reports no census-shaped or enumerated
    rationale, and `tests/test_mcp_negative_rationale_shape.py` passes.
  - **The evidence slots.** The `("find_examples", "multi-source", None)` and
    `("find_examples", "orchestrator load multiple data sources", None)` records in
    `tests/test_prescribed_search_queries.py` are re-measured with the marker and carry its
    stamp: server 1.46.1, docs index 2026-11-14 17:44 UTC, measured 2026-11-18. They name the
    bootcamp repositories, which `source/` does not.
  - **Every assistant.** The rule and both markers sit outside every host marker and name no
    assistant. `python3 -m tools.bootcamp_build check` passes, and
    `tools/bootcamp_build/neutrality.json` is unchanged.
  - **Tests.** `tests/test_bootcamp_repository_results_are_not_senzing_sources.py`, 9 tests.
    One function, `problems()`, reads every text file under `source/` and reports: the rule's
    label in no file, in a file other than `ground-rules.md`, twice, or outside the MCP-first
    section; each of 14 clauses the rule's bullet must state (the property, the case rule,
    disregarding, any result that names its repository, the `find_examples` field, the
    `search_docs` fields, the missing `repo` field, property not list, added or renamed later,
    the rest used as before, no Senzing example, the existing fallback, nothing said to the
    bootcamper, the dated observation); any of the three repository names, in any letter case,
    in any shipped file; and an orchestrator marker that is missing, does not point at the
    MCP-first section, or carries a stamp other than the two evidence slots'. Negative
    controls run on in-memory copies, one per check, with each clause removed in turn. It reads
    prose collapsed and the marker as one line, with its INV-346 verdict, and imports nothing
    from `source/` (INV-108).
  - **Differs from the issue.**
    - The issue says one of the two `multi-source` hits carries provenance "official". On
      2026-11-18 both do. The rule does not depend on provenance, so nothing else changes.
    - A second marker is added, under the rule, because the rule states what a `search_docs`
      hit lacks; the issue names one marker.
    - The rule cites INV-080 at its line, and a DEFERRED INVARIANT block below drafts the rule
      itself, since INV-080 does not say a bootcamp repository's hit is not a source.
    - The rule says a `search_docs` hit whose `source_url` is not a repository's address is not
      touched. The issue does not say this; without it a Senzing documentation page with
      "bootcamp" in its title could be read as covered.
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. Nothing here shows that a live guide disregards such a
    hit. The test reads Markdown and calls no server. Verified on Linux only, with Python
    3.12.3. The change is Markdown text and a standard-library test with no branch on the
    platform (INV-001), and it names no programming language's own mechanism (INV-002).
  - **Not changed.** The `visualization-api-reference.md` marker and the
    `("search_docs", "NEED_REEVALUATION how entity final state", None)` slot, whose rationale
    names the top hits of the same query and no longer reproduces now that a bootcamp script
    ranks first: that is #38's scope. The `dry-run-2026-11-17` entry, including its upstream
    draft.
- **Upstream, drafted and not sent.** Upstream: not yet sent — needs maintainer approval.
  - The "Indexed bootcamp repositories (finding 5)" draft in `dry-run-2026-11-17` still
    reproduces on 2026-11-18 and is not sent by this run. One detail in it is now out of date:
    it says one of the two `multi-source` results has provenance 'official', and on
    2026-11-18 both do. The corrected text, **not sent — needs maintainer approval**:
    "The example and docs corpus includes Senzing bootcamp plugin repositories (server 1.46.1,
    docs index 2026-11-14). `find_examples(query='multi-source')` returns only two results,
    both CHANGELOG.md files from those repositories, both with provenance 'official'.
    `find_examples(query='orchestrator load multiple data sources')` returns bootcamp helper
    scripts among its results, and `search_docs(query='NEED_REEVALUATION how entity final
    state')` ranks a bootcamp helper script first. These are teaching-plugin housekeeping
    files, not Senzing SDK examples, and a client that treats this server as its source of
    Senzing facts can be handed its own text. Suggest excluding these repositories, or at
    least their changelogs and non-SDK scripts."
- **Follow-up, drafted and not filed.** None. The adjacent stale rationale above is #38's.
- **Invariants.** The register is not edited here (INV-365). The rule this change ships is a
  hard rule with a ⛔; it cites INV-080 at its line, and the block below drafts it, because
  INV-080 makes the MCP tools the source of Senzing facts and does not say which of their
  results is not one. INV-209, INV-213, INV-219, INV-300 and INV-346 are applied and not
  changed. Beyond the one block the change establishes no new invariant.

- **DEFERRED INVARIANT (resolved INV-434, registered by the maintainer 2026-11-18).** An MCP result from a bootcamp repository is not a Senzing source. The rule already shipping, quoted:
    - ⛔ **A result from a bootcamp repository is not a Senzing source (INV-080).** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  Enforced by `tests/test_bootcamp_repository_results_are_not_senzing_sources.py`
  (`TheShippedTextIsClean`, `EachCheckReportsItsCase`).

  **Why it is not an existing invariant:** INV-080 says every Senzing fact comes from the
  Senzing MCP tools and never from training data. It treats whatever those tools return as
  the source, and says nothing about a result that is the bootcamp's own text served back by
  the server. INV-300 governs where the rule is stated, not what it says. INV-213 governs how
  an absence claim names its owner, not which hits count.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — An MCP result that names its repository MUST NOT be used as a Senzing source when that repository's name contains `bootcamp`, compared without regard to case. The guide reads the repository from the `repo` field of a `find_examples` hit, and from the `title` and `source_url` of a `search_docs` hit, which has no `repo` field; a `search_docs` hit whose `source_url` is not a repository's address is not covered. The rule is a property of the name and MUST NOT be stated as a list of repositories or of tools, so a bootcamp repository added or renamed later is covered with no edit. When some hits are disregarded the rest are used as before. When every hit is, the call counts as having returned no Senzing example, the step continues on its existing fallback, and the guide MUST NOT tell the bootcamper about the disregarded hits. The rule is stated once, in `skills/bootcamp-onboarding/ground-rules.md` → "MCP-first invariant (absolute precedence)", and no shipped file names a bootcamp repository whose name holds an assistant's name. Observed on MCP server 1.46.1 (docs index 2026-11-14 17:44 UTC), 2026-11-17 and 2026-11-18: `find_examples(query='multi-source')` returned only two bootcamp repositories' changelogs, and `search_docs(query='NEED_REEVALUATION how entity final state')` ranked a bootcamp script first (`dry-run-2026-11-17`, finding 5). Enforced by `tests/test_bootcamp_repository_results_are_not_senzing_sources.py`, which reads Markdown and calls no server; it **cannot** establish that a live guide disregards such a hit, or which repositories the server indexes. (Source: `the-senzing-mcp-server-returns-the-bootcamps-own-repositories-as-senzing-examples`, GitHub issue #37, 2026-11-18.)

- **Commit:** uncommitted

## the-flags-reference-reply-changed-shape-and-now-points-at-a-topic-the-bootcamp-never-names

- **Implemented:** 2026-11-18 (issue #36)
- **Files changed:** `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/module-06-data-processing/phaseD-validation.md`,
  `source/skills/module-07-query-visualize-discover/phase1-query-visualize.md`,
  `source/skills/module-07-query-visualize-discover/phase2-discover.md`,
  `source/skills/module-07-query-visualize-discover/phase2b-discover.md`,
  `tests/test_flags_lookup_reads_the_reply_that_holds_the_field.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** server 1.46.1, docs index built 2026-11-14 17:44 UTC, 2026-11-18 — server
  now contradicts the plugin, as the issue recorded on 2026-11-17, and in one respect
  differently from what the issue expected (the third item of "Differs from the issue" below).
  Tools: `get_capabilities`, `get_sdk_reference`, `search_docs`, read-only; `search_docs` at the
  default result count. `submit_feedback` and `download_resource` were not called. Every call
  was made before any file was changed, except the two marked "after" below, which were made
  to write a citation as the exact call and changed no decision.
  - `get_capabilities()` gives `"server_version":"1.46.1"`. The index build is not in that
    reply. It is in the `search_docs` reply: `"index_built":"2026-11-14 17:44 UTC"`,
    `"documents_indexed":13404`.
  - **The compact list.** `get_sdk_reference(topic='flags', filter='export_json_entity_report')`
    returns `"method":"export_json_entity_report"`, `"default_flags":"SZ_EXPORT_DEFAULT_FLAGS"`,
    `"detail":"Full definitions and response paths: get_sdk_reference(topic='flag_details',
    filter='export_json_entity_report'), or filter by one flag name."`, and a `data` array of
    strings: group headers such as `# export`, and one line per flag. Among them:
    `SZ_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES (default) — Include only resolved entities that
    contain…`, the same cut-short text for `SZ_EXPORT_INCLUDE_SINGLE_RECORD_ENTITIES`,
    `# fallback:java-sdk-SzFlag-enum` followed by `SZ_EXPORT_ALL_FLAGS — All export flags
    combined — includes all…`, and `SZ_INCLUDE_MATCH_KEY_DETAILS =
    SZ_ENTITY_INCLUDE_ALL_RELATIONS`. `SZ_ENTITY_INCLUDE_RECORD_SUMMARY` appears only inside
    the `SZ_ENTITY_DEFAULT_FLAGS = …` line. The same call with `language='python'` returns the
    same `data` array, and `method_signatures` holding the Python signatures only. The
    top-level `caution` and `method_signatures` are in both replies.
  - **The same shape for other single methods.** `filter='why_records'`,
    `filter='get_entity_by_record_id'`, `filter='how_entity_by_entity_id'`,
    and, with `language='python'`, `filter='find_network_by_entity_id'`,
    `filter='find_path_by_entity_id'`, `filter='how_entity'` and `filter='search_by_attributes'`
    each return the compact list with a `detail` field. The `get_entity_by_record_id` reply
    holds both `SZ_INCLUDE_MATCH_KEY_DETAILS = SZ_ENTITY_INCLUDE_ALL_RELATIONS` and
    `SZ_ENTITY_INCLUDE_RECORD_JSON_DATA = SZ_RECORD_DEFAULT_FLAGS`. The `why_records` reply
    holds `SZ_WHY_RECORDS_DEFAULT_FLAGS = SZ_INCLUDE_FEATURE_SCORES`. The
    `find_network_by_entity_id` reply's `caution` is, word for word, the text
    `phase1-query-visualize.md` quotes.
  - **The row form from `flag_details`.**
    `get_sdk_reference(topic='flag_details', filter='export_json_entity_report')`, asked with
    `language='python'` and without (after), returns each flag as an object, for example
    `"name":"SZ_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES","description":"Include only resolved
    entities that contain more than one record. …","applies_to":["export_json_entity_report",
    "export_csv_entity_report"],"source_file":"docs-flags-4-flags_export.md"`, and
    `SZ_EXPORT_ALL_FLAGS` with `"source_file":"fallback:java-sdk-SzFlag-enum"`. It holds no row
    for `SZ_ENTITY_INCLUDE_RECORD_SUMMARY`; that name is in `SZ_ENTITY_DEFAULT_FLAGS`'s
    `composite_members`.
  - **The row form from a flag name.** `filter='SZ_EXPORT_ALL_FLAGS'` returns that row with the
    same `source_file`. `filter='SZ_INCLUDE_MATCH_KEY_DETAILS'` returns a row with `name`,
    `description`, `applies_to`, `source_file` and `response_paths`, whose description opens
    "The SZ_INCLUDE_MATCH_KEY_DETAILS flag is dependent on using one of the following flags:
    SZ_ENTITY_INCLUDE_ALL_RELATIONS , SZ_ENTITY_INCLUDE_POSSIBLY_SAME_RELATIONS , …".
    `filter='SZ_ENTITY_INCLUDE_RECORD_JSON_DATA'` returns a row whose description is "Member of
    SZ_RECORD_DEFAULT_FLAGS." `filter='SZ_WHY_RECORDS_DEFAULT_FLAGS'` returns "The default
    recommended flags for why_records. Equivalent to: SZ_INCLUDE_FEATURE_SCORES." with
    `"composite_members":["SZ_INCLUDE_FEATURE_SCORES"]`. `filter='SZ_INCLUDE_FEATURE_SCORES'`
    returns `applies_to` naming `search_by_attributes`, `how_entity_by_entity_id`,
    `why_entities`, `why_records`, `why_record_in_entity` and `why_search`.
    `filter='SZ_ENTITY_INCLUDE_RECORD_SUMMARY'` (after) returns "Include the record summary of
    the entity." `filter='SZ_FIND_PATH_INCLUDE_MATCHING_INFO'` and
    `filter='SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO'` return `applies_to` of the two
    `find_path_*` and the two `find_network_*` methods, and each default composite's
    `composite_members` holds its own matching-info flag.
  - **Three filters return the row form directly.** `filter='find_network'` and
    `filter='find_path'`, and `filter='get_entity'` with `language='python'`, return objects
    with `applies_to`, and no `method`, `default_flags` or `detail` key. The issue expected the
    compact list for the first two. What decides the shape was not established: the three
    names each cover a by-entity-ID and a by-record-ID method, and that is an observation about
    three filters, not a rule the server states.
  - **The binding's own flag reference.**
    `search_docs(query='senzing.szengineflags SzEngineFlags SZ_EXPORT_DEFAULT_FLAGS')` returns
    as hit 1 the Python `szengineflags` section, whose excerpt runs from
    `SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES` directly to `SZ_EXPORT_DEFAULT_FLAGS`. The
    owner clause of the corrected marker rests on this call. The second marker in that
    paragraph, stamped 1.37.16, is #38's and is not re-dated here.

  Three statements above are absence claims, so (INV-213):
  owner-checked: `get_sdk_reference(topic='flag_details', filter='export_json_entity_report')`
  is the route the compact list's own `detail` field names for the fields the list lacks — it
  returned every flag of the method as an object with `applies_to` and `source_file`, and
  `composite_members` and `response_paths` on the composites.
  owner-checked: `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')` is
  the route that carries that flag's fields — it returned no `depends_on` and no
  `composite_members`, and its description states the dependency. The field does exist on
  other rows: `filter='SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME'` returns a row with
  `"depends_on"` naming the relations flags.
  owner-checked: `get_sdk_reference(topic='flags', filter='SZ_ENTITY_INCLUDE_RECORD_JSON_DATA')`
  is the route that carries that flag's fields — it returned no `composite_members`, and
  `SZ_RECORD_DEFAULT_FLAGS`, in the same reply, carries
  `"composite_members":["SZ_ENTITY_INCLUDE_RECORD_JSON_DATA"]`.
- **Summary:** A method's flags lookup no longer returns flag entries with fields, and shipped
  steps still read fields from it (`dry-run-2026-11-17`, findings 6 and 7). Each step now makes
  a call whose reply holds what it reads, and shipped text names `flag_details`.
  - **The rule.** `ground-rules.md`, under the "Flags" bullet, gains the passage "Reading a
    flags reply". It describes the two shapes and how to tell them apart, then says: "Choose
    flags from the compact list. Before reading a field or a full description, call the row
    form: by flag name for one flag, or by `topic='flag_details'` for a method." The fallback
    is the next sentence: when the compact list carries no `detail` pointer, or
    `topic='flag_details'` fails, the flag-name row, saying which route produced what is
    presented (INV-125). The passage is in that one file. The four other files point at it
    with `ground-rules.md` → "Reading a flags reply", and none holds a copy.
  - **The sites.** The scope is every method-filter `topic='flags'` call in `source/`. A scan
    that reads across line wraps finds 15, in five files: the 12 the issue counted and three it
    missed (first item of "Differs from the issue").
    - `phaseD-validation.md`: the sentence that said "only its `source_file` … shows the Java
      origin" now says the reply is the compact list, that the Java origin shows only in the
      group header above the flag's line, `# fallback:java-sdk-SzFlag-enum`, and that the
      flag's own row carries the same value as its `source_file`. Its marker is corrected to
      say the same and stamped server 1.46.1, 2026-11-18. "does not narrow that list by
      binding" still holds and is kept.
    - `ground-rules.md`, the entity-as-text "Rank" step: the export's flags are named by the
      compact list, and the step reads the full descriptions from `topic='flag_details'` and
      each entity flag from its own row before choosing. The dated note on `method_signatures`
      in "Parameter shapes" is re-confirmed on 1.46.1.
    - `phase1-query-visualize.md`: the flags paragraph points at the rule; the dependency
      lookup names `get_sdk_reference(topic='flags', filter='SZ_INCLUDE_MATCH_KEY_DETAILS')`
      and its `description`; the `caution` quotation is kept and re-confirmed word for word;
      the `applies_to` of `SZ_INCLUDE_FEATURE_SCORES` is cited to that flag's own row.
    - `phase2-discover.md`: the `get_entity_by_record_id` and `why_records` lookups point at
      the rule; the equivalence of `SZ_WHY_RECORDS_DEFAULT_FLAGS` is cited to that composite's
      own row; the `how_entity_by_entity_id` lookup confirms the two flag names from the
      compact list and the relations dependency from the flag's row.
    - `phase2b-discover.md`: the `find_network` and `find_path` lookups say which shape each
      filter returned; the sentence that reads `applies_to` says it reads the row form; the
      export lookup says its reply is the compact list; and the step that finds the
      relationship flags says they are named inside a composite's line.
  - **The dated note.** Beside the dependency lookup, `phase1-query-visualize.md` says, dated
    server 1.46.1, 2026-11-18, that in the compact list `=` also marks "depends on" and
    "member of", gives the two lines above as returned, and says "a line `A = B` is not proof
    that `A` is a composite".
  - **Three markers.** The corrected one in `phaseD-validation.md`, and two new ones, because
    the rule and the note are dated statements of what a reply lacks: one under the rule and
    one under the note. `coverage_reports.py negatives` parses all three and reports no
    census-shaped or enumerated rationale; `unmarked` reports none.
  - **Every assistant.** The changed passages sit outside every host marker and name no
    assistant. `python3 -m tools.bootcamp_build check` passes, and a build of all five
    packages was read: each holds the rule once, the pointer in four files, and the note.
  - **Differs from the issue.**
    - The issue counts 12 calls. Three more are corrected: the `why_records` call in
      `phase1-query-visualize.md` that read `applies_to`, the `how_entity_by_entity_id` call in
      `phase2-discover.md`, and the dated `find_network_by_entity_id` note in `ground-rules.md`.
      The first two are split across a line break, and the third is not written as a full
      call.
    - The criterion asks for a DEFERRED INVARIANT block for INV-132. INV-132 is in force, so
      the block below is a PROPOSED AMENDMENT, the shape `review-invariants` → "Writing one"
      gives for a change to an invariant in force.
    - The issue says a method filter returns the compact list. Three filters return the row
      form (above). The rule therefore tells the guide to see which shape came back, and does
      not say a method filter always returns the compact list.
    - `flag_details` for the export method has no row for a member entity flag, so the "Rank"
      step names the flag's own row for it as well.
    - Two markers are added beyond the one the issue names.
  - **Tests.** `tests/test_flags_lookup_reads_the_reply_that_holds_the_field.py`, 19 tests. One
    function, `problems()`, reads every Markdown file under `source/` and reports: the rule
    held by no file or by more than one; a rule that does not say to choose from the compact
    list, does not send the reader to the row form by flag name or by `flag_details`, or
    states no fallback with INV-125; a file that makes a method-filter call and does not point
    at the rule; a list item or paragraph that makes such a call, names one of the five fields
    and names no row-form route; a missing or undated `=` note, or one with no dependency
    lookup beside it; and a Module 6 marker whose version, date or origin token differs from
    its paragraph's. The sites are found by scanning (INV-246). The shipped files give none.
    - Negative controls run on every pass, on in-memory copies: a second copy of the rule,
      the rule without `flag_details`, without its INV-125 citation or without its first
      sentence, a site with no pointer, the Module 6 sentence as it shipped until this issue,
      a note without "member of" or without its date, a dependency lookup that names no row,
      and a marker re-dated or naming another origin are each reported; the retired sentence
      with its row named is not.
    - Run once against the five files as they stand on `b077397`: seven problems, among them
      `phaseD-validation.md:487 reads ['source_file'] beside a method-filter topic='flags'
      call and names no row-form route`.
    - It asserts properties and no server wording (INV-219), reads prose through
      `_wrapped_text` (INV-346) and imports nothing from `source/` (INV-108).
    - Two existing guards shaped the wording and are unchanged:
      `tests/test_how_call_requests_the_breakdown_it_promises.py` fails a sentence that names
      `SZ_INCLUDE_MATCH_KEY_DETAILS` and `depends_on` together, so the lookup names the
      description and not the missing field; `tests/test_module07_why_flags.py` wants every
      mention of that flag to carry its relations dependency, so the note says "relations
      flags".
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. Nothing here shows what a live guide does with either
    reply. The test reads Markdown and calls no server: it cannot show which shape a filter
    returns on a later server, or that `flag_details` still exists. A failing
    `topic='flag_details'` call was not produced, so the fallback is stated and not exercised.
    Verified on Linux only, with Python 3.12.3. The change is Markdown text and a
    standard-library test with no branch on the platform (INV-001), and it names no
    programming language's own mechanism (INV-002).
  - **Not changed.** Sites that filter `topic='flags'` by a flag name, and the dated
    statements about `topic='flags'` that name no filter (the INV-179 paragraph in
    `ground-rules.md`, the composite-membership section and the `find_network` coverage note
    in `phase1-query-visualize.md`, the binding-type note in `phase2-discover.md`): their
    replies are the row form, which did not change, and re-dating them is #38. The second
    marker in the `phaseD-validation.md` paragraph (#38). The `/auto-test` probe baseline
    (#50).
  - **Waited for #50.** `tests/test_auto_test_harness.py` checks every literal MCP call in
    `source/` against `.claude/skills/auto-test/baseline/mcp-snapshot.json`. Captured from
    server 1.40.10, that baseline had no `flag_details` in `get_sdk_reference`'s topic set, so
    the two `topic='flag_details'` calls this change ships were reported as BREAKING and the
    full suite was red. #50 refreshed the baseline from 1.46.1 (merged as `f0dd599`), and this
    change was rebased onto it unchanged: the test passes, with neither the baseline nor the
    guard edited here.
- **Upstream, drafted and not sent.** Upstream: not yet sent — needs maintainer approval.
  - The message about the `=` rendering is the "Flags list (finding 7)" draft in
    `dry-run-2026-11-17`. It still reproduces on 2026-11-18 and is not sent by this run.
  - A second message, drafted here, **not sent — needs maintainer approval**:
    "`get_sdk_reference(topic='flags', filter=<method>)` returns two different shapes
    depending on the filter (server 1.46.1). `find_network_by_entity_id`,
    `find_path_by_entity_id` and `get_entity_by_record_id` return the compact list with a
    `detail` field; `find_network`, `find_path` and `get_entity` return full flag objects
    and no `detail` field. The tool description says a method filter returns one line per
    flag. Also, in the compact list for `why_records`, `default_flags` is
    `SZ_WHY_ENTITIES_DEFAULT_FLAGS` and that line carries `(default)`, while
    `SZ_WHY_RECORDS_DEFAULT_FLAGS` does not; and for `get_entity_by_record_id`,
    `default_flags` is `SZ_ENTITY_BRIEF_DEFAULT_FLAGS` while the Python signature in the same
    reply defaults to `SZ_ENTITY_DEFAULT_FLAGS`. A caller cannot tell which default to trust."
- **Follow-up, drafted and not filed.** One issue, **not filed**: "The compact flags list
  marks a default that the binding's signature does not use." For `why_records` and
  `get_entity_by_record_id` the compact list's `default_flags` and `(default)` marks name a
  different composite from the one the Python signature in the same reply defaults to (the
  second upstream draft above). Shipped text tells the guide to corroborate a default with
  `method_signatures` only inside Module 7's composite-membership section; the new "Reading a
  flags reply" passage does not mention `(default)`. Proposed: one sentence there saying the
  binding's default is read from `method_signatures`. Left out of this change because the
  issue's scope is the routing of field reads.
- **Invariants.** The register is not edited here (INV-365). The lines this change adds or
  edits under `source/` carry no ⛔ and no bold MUST or NEVER, and
  `conformance.py since --since-last-audit` reports none from this change. INV-132 says that
  under a method filter "flag entries additionally carry `composite_members`, `depends_on` and
  `response_paths`", which the server no longer returns for most method names, and the block
  below proposes the dated correction. INV-080, INV-125, INV-169, INV-209, INV-213 and INV-219
  are applied and not changed. INV-300 is not engaged: no site says the rule is stated once,
  and the pointers name their file and section. Beyond the one block the change establishes
  no new invariant.

- **DEFERRED INVARIANT (resolved INV-435, registered by the maintainer 2026-11-18).** How the guide reads a flags reply. Split at review from the INV-132 amendment below, whose draft carried these MUSTs inside a dated note; the maintainer made them their own invariant. The rules already shipping, quoted:
    - ⛔ **Choose flags from the compact list. Before reading a field or a full description, call the row form: by flag name for one flag, or by `topic='flag_details'` for a method.** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **When the compact list carries no `detail` pointer, or `topic='flag_details'` fails, fall back to the flag-name row, `get_sdk_reference(topic='flags', filter='<flag name>')`, and say which route produced what you present** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **a line `A = B` is not proof that `A` is a composite** — in `source/skills/module-07-query-visualize-discover/phase1-query-visualize.md`

  Enforced by `tests/test_flags_lookup_reads_the_reply_that_holds_the_field.py`.

  **Why it is not an existing invariant:** INV-132 governs reading a tool's parameter shape from
  the server; it says nothing about which of two reply shapes holds a flag's fields, or how the
  guide must tell them apart.

  **INV-435** — Before reading a reply to `get_sdk_reference(topic='flags', …)`, the guide MUST tell which shape it has: the compact list (lines under group headers) or the row form (one entry per flag with its fields). It MUST choose flags from the compact list, and MUST call the row form before reading a flag's field or its full description: by flag name for one flag, or `topic='flag_details'` for a method. Where the compact list carries no `detail` pointer, or `topic='flag_details'` fails, it MUST fall back to the flag-name row and say which route produced what it presents (INV-125). In the compact list `=` also marks "depends on" and "member of", so a line `A = B` MUST NOT be read as proof that `A` is a composite. The rule is stated once, in `skills/bootcamp-onboarding/ground-rules.md` → "Reading a flags reply", and every shipped file that makes a method-filter `topic='flags'` call MUST hold it or point at it. Enforced by `tests/test_flags_lookup_reads_the_reply_that_holds_the_field.py`, which reads Markdown and calls no server; it **cannot** establish that a live guide reads the shape first. (Source: `the-flags-reference-reply-changed-shape-and-now-points-at-a-topic-the-bootcamp-never-names`, GitHub issue #36, 2026-11-18.)

- **PROPOSED AMENDMENT to INV-132 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Choose flags from the compact list. Before reading a field or a full description, call the row form: by flag name for one flag, or by `topic='flag_details'` for a method.** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **When the compact list carries no `detail` pointer, or `topic='flag_details'` fails, fall back to the flag-name row, `get_sdk_reference(topic='flags', filter='<flag name>')`, and say which route produced what you present** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **a line `A = B` is not proof that `A` is a composite** — in `source/skills/module-07-query-visualize-discover/phase1-query-visualize.md`

  INV-132, as corrected on 2026-07-30, says a `flags` result already in hand answers the
  parameter shape and that "flag entries additionally carry `composite_members`,
  `depends_on` and `response_paths`, which is what a flag family selects". The first half
  still holds: `method_signatures` comes back with both shapes. The second half is false for
  the compact list, which is what most method filters now return. Left as it is, the
  registered wording tells a guide, and the next editor, that those fields are in a reply
  that does not hold them, which is the failure the 2026-07-30 correction itself names
  (telling the guide that data is where it is not). The shipped text and
  `tests/test_flags_lookup_reads_the_reply_that_holds_the_field.py` already say otherwise, so
  without the note below the register and its shipped rule disagree.
  Enforced by `tests/test_flags_lookup_reads_the_reply_that_holds_the_field.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-132** — (⚠️ **Dated note, 2026-11-18 (#36): the clause on flag entries holds for the row form only; the parameter-shape rule above is unchanged.** On MCP server 1.46.1 (docs index 2026-11-14 17:44 UTC), `get_sdk_reference(topic='flags', filter='<method>')` returned, for several methods, a compact list: lines of text under group headers, with a `detail` field naming `topic='flag_details'`, and none of `composite_members`, `depends_on`, `response_paths`, `applies_to` or `source_file`. Those fields are in the row form, which a flag-name filter returns for one flag and `topic='flag_details'` returns for every flag of a method. So "flag entries additionally carry `composite_members`, `depends_on` and `response_paths`" holds for the row form only. The `method_signatures` block came back with both shapes, so a `flags` result in hand still answers the parameter shape. How the guide reads a flags reply is INV-435. Which filters return which shape is an observation on that server, recorded with its date, and not a rule (INV-169).)

  **Amended at review, 2026-11-18:** the maintainer split this draft. Its MUSTs on reading a
  flags reply became INV-435 (the block above), and this note keeps only the factual
  correction.

- **Commit:** uncommitted

## re-read-the-mcp-servers-changed-prose-and-refresh-the-probe-baseline

- **Implemented:** 2026-11-18 (issue #50)
- **Files changed:** `.claude/skills/auto-test/baseline/mcp-snapshot.json`,
  `tests/test_mcp_call_contracts.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** server 1.46.1, docs index built 2026-11-14 17:44 UTC, 2026-11-18 — server
  now contradicts the plugin, at one place no open issue covers (C1 below). Tools: the probe
  `.claude/skills/auto-test/mcp_probe.py` (`check`, `snapshot`, `update`; read-only calls only,
  `submit_feedback` and `download_resource` blocked in code by `NEVER_CALL`), then
  `get_capabilities()`, `search_docs(query='one mapping_workflow over all related source files or tables together joins relationships')`
  at the default result count, and
  `sdk_guide(topic='configure', platform='linux_apt', language='python')`. `get_capabilities`
  gives `"server_version":"1.46.1"`; the index build is in the `search_docs` reply's
  `metadata`: `"index_built":"2026-11-14 17:44 UTC"`, `"documents_indexed":13404`. The server
  is the version the issue was written against, and the probe reported the same eight changed
  texts the issue names, so the change is what the issue asks for.
- **Summary:** The `/auto-test` probe baseline was captured from server 1.40.10. It is
  refreshed from 1.46.1, after every changed server text was re-read against shipped text and
  each contradiction recorded below, and the static contract in
  `tests/test_mcp_call_contracts.py` is re-verified and re-dated. No file under `source/` or
  `hosts/` changes.
  - **Probe summary line before the refresh** (`mcp_probe.py check`, 2026-11-18, exit 0):
    `14 INFO, 10 WATCH`. The WATCH findings: `content` (`get_capabilities`), `contract-stale`
    (`CONTRACT_VERIFIED_ON is 2026-08-12 (98 days old, limit 90)`), six `description`
    (`find_examples`, `get_sdk_reference`, `mapping_workflow`, `reporting_guide`, `sdk_guide`,
    `search_docs`), `instructions`, and `silent-accept` on `search_docs.category`. No BREAKING,
    no `static-contract-wrong`, no `static-contract-drift`, no conformance violation.
  - **Probe summary line after the refresh** (`mcp_probe.py update`, exit 0, "baseline
    written: .claude/skills/auto-test/baseline/mcp-snapshot.json (13 tools)", then `check`,
    exit 0): `9 INFO, 1 WATCH`. The one WATCH finding is `silent-accept` on
    `search_docs.category`, which the issue leaves in place. No `instructions`, `description`,
    `content` or `contract-stale` finding remains. The refreshed baseline lists `flag_details`
    in `get_sdk_reference`'s declared `topic` enum and in its probed accepted values.
  - **The eight texts re-read**, each against the old baseline's copy, before `update`
    overwrote it:
    - Server `instructions`: the `## NETWORK ACCESS` section moved below the others, unchanged
      in wording; two routing lines were added ("Database/warehouse tables (e.g. Snowflake) →
      export a sample of each table to CSV, then ONE mapping_workflow over the related tables",
      and a Databricks line naming `mapping_workflow` with `environment="databricks"`).
    - `find_examples`: "51 indexed Senzing GitHub repositories" became "53".
    - `get_sdk_reference`: the `flags` topic with a method filter now returns "one line per
      applicable flag … under group headers", and a new topic, "'flag_details' (the full
      definitions and response paths for a method filter)".
    - `mapping_workflow`, `reporting_guide`, `sdk_guide`: each gained an optional
      `environment` ("one of snowflake, aws_lambda, azure_functions, kafka, spark,
      databricks"), whose response "then opens with `environment_note`"; for
      `mapping_workflow`, "dotted DB.SCHEMA.TABLE source labels … infer
      environment=snowflake".
    - `search_docs`: "~2175 chunks" became "~13.5k chunks", and "A result from a Senzing
      whitepaper is one section, dated by `as_of` (last reviewed): act on it, then follow its
      `next`".
    - `get_capabilities` response: the version, "461 codes" to "462", "51 GitHub repositories"
      to "53", the tool entries above, and two `suggested_workflows` steps: C1 below, and the
      "Deploy Senzing" step, now "for production, install the senzingsdk-runtime package on
      your own hardened, CVE-patched base (as the official senzing/ Dockerfiles do);
      senzing/senzingsdk-runtime as a base image is for development and evaluation".
  - **Contradictions with shipped text, for the maintainer to file (not filed):**
    - **C1, no open issue covers it.** `get_capabilities` → `suggested_workflows` →
      "Analyze Data with Senzing (End-to-End)", step 1: "Phase 1 — Map ALL data sources: ONE
      mapping_workflow (steps 1-4) over all the related source files or tables together, so
      joins and relationships between them are seen (produces mapped JSONL). Use a separate
      workflow only for genuinely independent sources." On 1.40.10 the same step read
      "mapping_workflow steps 1-4 for EACH source file". The server `instructions` add the
      same for tables: "ONE mapping_workflow over the related tables". Shipped text runs one
      workflow per source with no exception for related sources:
      `source/skills/module-05-data-quality-mapping/phase2-data-mapping.md:234` ("This module
      runs one workflow **per source**"), `:460` ("## Workflow (per data source)"), `:473-478`
      ("**Per-source mapping requirement:** Each data source **must** complete its own full
      `mapping_workflow` run … Every source gets its own independent `mapping_workflow`
      execution") and `:41` ("a full `mapping_workflow` run, as Step 8's per-source
      requirement demands"). This is the contradiction the issue named, confirmed; the issue
      quoted it at `:233`, which is now `:234`.
    - **C2, no open issue covers it.**
      `source/skills/bootcamp-onboarding/ground-rules.md:655-661` gives as "the live
      illustration" that "`search_docs`' declared description sizes the corpus in chunks, while
      every `search_docs` response carries `metadata.documents_indexed`, a different figure."
      On 1.46.1 the description says "~13.5k chunks" and the reply above carries
      `"documents_indexed":13404`: the two figures now agree to the description's rounding, so
      the passage's illustration no longer shows a disagreement. The rule above it (INV-280)
      is not affected.
    - **Covered by open issue #36.** The `get_sdk_reference` change: the `flags` reply's new
      shape and the `flag_details` topic, which no shipped text names yet.
  - **Read and found consistent with shipped text:** the moved `NETWORK ACCESS` section (no
    shipped text quotes the server `instructions`); the new `environment` parameter, which the
    bootcamp never passes — and
    `sdk_guide(topic='configure', platform='linux_apt', language='python')` still returns the
    `environment` response block with `default_paths` and `engine_config` that
    `source/skills/module-02-sdk-setup/SKILL.md:2275-2281` relies on; the `as_of` and `next`
    fields of a whitepaper result (no file under `source/` or `hosts/` names `as_of`, `next` or
    a whitepaper); the "Deploy Senzing" step, which matches Module 2's container route, a plain
    `debian:bookworm-slim` container with the `linux_apt` packages installed in it
    (`module-02-sdk-setup/SKILL.md:788-791`); and the error-code and repository counts, which
    no file under `source/` or `hosts/` states.
  - **`CONFABULATIONS`.** The live `llm_instructions.common_confabulations` is identical to the
    1.40.10 baseline's, item for item, so `mcp_probe.py` is not edited.
  - **The static contract, re-verified 2026-11-18.** `mcp_probe.py check` reported no
    `static-contract-wrong`, `static-contract-drift` or BREAKING finding. Against the live
    schemas: the 13 live tool names equal `MCP_TOOLS`; every `REQUIRED_PARAMS` entry is in its
    tool's `required` array, and `mapping_workflow`'s two are in its description ("REQUIRED on
    action='start': `file_paths` AND `workspace_dir`"); the four tools classed as conditional
    or requiring nothing declare no required parameter; the `mapping_workflow` `action` enum
    is `start`, `advance`, `back`, `status`, `reset` (plus null); `get_capabilities` reports
    `tool_count` 13. `CONTRACT_VERIFIED_ON` is now `2026-11-18` and `MCP_SERVER_VERSION`
    `1.46.1`, and the comment above them says what was checked. The `MCP_TOOLS` comment's
    tool-count date moves with them, because the count was read again today.
  - **Spelling waiver.** The baseline still holds the server's word the waiver in
    `tests/test_us_english_spelling.py` names, and that test passes, so the waiver stays.
  - **Tests.** No test is added: the change is a re-verified constant and a machine-written
    baseline. `tests/test_mcp_call_contracts.py` and the auto-test tests pass on the refreshed
    baseline, and so do `python3 -m tools.bootcamp_build check` and the full suite.
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. No package's content changes. Verified on Linux only,
    with Python 3.12.3; the change is data and a dated constant, with no branch on the
    platform (INV-001) and no programming language's own mechanism (INV-002).
- **Invariants.** The register is not edited here (INV-365). INV-080 is applied, not changed.
  The change adds no ⛔ line and no bold MUST or NEVER, and ships no new rule: it establishes
  no new invariant.
- **Commit:** uncommitted

## two-module-2-claims-about-the-senzing-mcp-server-no-longer-hold

- **Implemented:** 2026-11-18 (issue #35)
- **Files changed:** `source/skills/module-02-sdk-setup/SKILL.md`,
  `tests/test_record_limit_route_names_no_ranking.py` (renamed from
  `test_record_limit_negative_is_rescoped.py`), `tests/test_prescribed_search_queries.py`,
  `tests/test_sdk_update_offer.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** server 1.46.1, docs index built 2026-11-14 17:44 UTC, 2026-11-18 — server
  now contradicts the plugin, on both claims, as the issue recorded on 2026-11-17. Tools:
  `get_capabilities`, `search_docs`, `sdk_guide`, read-only. Every `search_docs` call was made
  at the default result count, with no `max_results` and no `category`. The server version
  and the index build are the ones the issue was refined against, and each reply matches what
  the issue records, so the change is what the issue asks for. The calls, re-asked before any
  file was changed:
  - `get_capabilities()` gives `"server_version":"1.46.1"`. The index build is not in that
    reply. It is in each `search_docs` reply: `"index_built":"2026-11-14 17:44 UTC"`,
    `"documents_indexed":13404`.
  - **Record limit.**
    `search_docs(query='evaluation license record limit how many records without a license')`
    returns as hit 1 the FAQ "What is the 500 record limit and how do I work around SENZ9000":
    "Without a license, Senzing operates in evaluation mode limited to 500 Distinct Source
    Records (DSRs)." The EULA sections "B. Senzing Production License", "A. Senzing
    Non-Production License" and "End User License Agreement" are hits 6, 7 and 8. So the
    shipped sentence, "its top-ranked hits are EULA grant-of-license prose that states no
    figure, and the figure sits in a lower-ranked FAQ", was false, and so was its marker.
  - **The route Step 5 keeps.**
    `sdk_guide(topic='load', language='python', platform='linux_apt', record_count=1000)`
    returns as the first `compatibility_notes` entry: "LICENSE REQUIRED: You have 1000 records,
    which exceeds the default Senzing license limit of 500 Distinct Source Records." The route
    is unchanged. What the passage now says of `search_docs` is the tool's own description as
    the server gives it: "Full-text BM25 search across all indexed Senzing documentation …
    Returns ranked results with excerpts."
  - **Scoop.** `search_docs(query='scoop-senzingsdk update scoop update senzingsdk')` returns as
    hit 1 the `senzing/scoop-senzingsdk` README, whole. It opens with the heading
    "scoop-senzingsdk" and the line "Scoop bucket for installing the Senzing SDK on Windows."
    (link markup left out here), and carries "### Update" with `scoop update senzingsdk`. Hits
    2 to 7 are its CHANGELOG and its `docs/` pages.
  - **Homebrew, the relay's own query.**
    `search_docs(query='homebrew-senzingsdk preview release unsupported tap install cask')`
    returns three sections titled `senzing/homebrew-senzingsdk`: "Install" (hit 1), "Synopsis"
    (hit 7: "A Homebrew tap to publish the Senzing SDK for macOS.", link markup left out here)
    and "Upgrade" (hit 10). All three were read. The other hits are the tap's
    `docs/` pages, its CHANGELOG and the macOS quickstart. The record this query had named a
    section "homebrew-senzingsdk" as its top hit; no section of that name came back.
  - **Homebrew, the update route.**
    `search_docs(query='homebrew-senzingsdk upgrade cask brew upgrade senzingsdk')` returns as
    hit 1 the FAQ "What are the exact steps to migrate from V3 to V4?" and as hit 2
    `senzing/homebrew-senzingsdk` section "Upgrade": `brew update`, then
    `brew upgrade --cask senzingsdk`. The README's "Install" and "Uninstall" sections are hits
    7 and 9. The record's band, `ON TARGET BELOW AN ADJACENT TOP HIT`, still holds.
  - **The notice's own words.**
    `search_docs(query='Preview Release Unsupported provided as-is with no warranty and is not supported')`
    returns EULA warranty sections, two support FAQs and other pages, and no document from
    `senzing/homebrew-senzingsdk` or `senzing/scoop-senzingsdk`.

  That neither README carries the notice is an absence claim, so (INV-213):
  owner-checked: `search_docs` is the route that carries both READMEs, and the route the relay
  itself named — it returned the Scoop README whole and the Homebrew README's Install,
  Synopsis, Upgrade and Uninstall sections, and none of them holds the words "preview",
  "unsupported" or "warranty". `sdk_guide(topic='install', platform='macos_arm')` and
  `sdk_guide(topic='install', platform='windows')` were asked too: their `install_commands`
  call them "the official Senzing Homebrew tap" and "the official Senzing Scoop bucket", and
  where those replies say "unsupported" it is of the Python SDK off Linux and of
  `senzing-garage` repositories, not of the tap or the bucket.
  The limit of that check: the Homebrew README is served in sections, and only the sections
  those calls returned were read. The file was not read whole. No shipped text now says the
  notice is absent, and no marker says so, as the issue decides.
- **Summary:** Module 2 said two things about the Senzing MCP server that the server does not
  return (`dry-run-2026-11-17`, findings 2 and 3). Both are corrected to the calls above, and
  neither passage now depends on which `search_docs` hit ranks where.
  - **Step 5, the record limit.** The fallback still fills `{record limit}` from
    `sdk_guide(topic='load', …, record_count=1000)`. Its reason now reads: "`sdk_guide` states
    the figure in a fixed field, `compatibility_notes`, while `search_docs` results are
    ranked." The sentences saying which hits rank where and that the top hit has no figure
    are removed, with the `MCP-NEGATIVE` marker for the record-limit query. The passage keeps
    "Never substitute a hardcoded or remembered figure" with its INV-080 citation, and
    carries no figure and no date. The ⛔ line above it is not edited.
  - **Step 2, the preview relay.** Removed for both platforms: the two parentheticals in the
    platform list, which now read "(Homebrew cask)" and "(Scoop)"; the ⚠️ paragraph, with its
    prescribed query and its pointer to "The update command"; and the clauses in routing
    rules 3 and 4. Rule 3 still resolves to `platform='macos_arm'` and rule 4 to
    `platform='windows'`. Nothing replaces the relay. Step 1b's statement of the update route
    is not edited.
  - **`VERIFIED_QUERIES`.** Two records are removed, because no shipped file prescribes their
    query now: the record-limit query and the Homebrew preview query. The two update-route
    records are re-measured and stamped server 1.46.1, docs index 2026-11-14 17:44 UTC,
    2026-11-18. Neither describes the notice, and the Scoop record's `sections` is `("Update",)`.
    The Homebrew record keeps its band.
  - **What a bootcamper is told changes.** On macOS Apple Silicon and on Windows with Scoop,
    the guide no longer says the install route is an unsupported preview release.
  - **Every assistant.** The changed passages sit outside every host marker and name no
    assistant. `python3 -m tools.bootcamp_build check` passes, and a build of all five
    packages was read: each carries the corrected Step 5 sentence, and none carries the
    relay or either removed query.
  - **Differs from the issue's wording, not from what it asks.** The record-limit test file is
    renamed, which the issue allows. The class `StepTwoRelaysThePreviewStatus` is renamed
    `StepTwoStatesNoPreviewClaim`, because it now asserts the opposite. One `search_docs`
    call beyond the three the issue names was made, of the notice's own words, at the default
    result count.
  - **Tests.**
    - `tests/test_record_limit_route_names_no_ranking.py`, 16 tests where the file it replaces
      had 13. One function, `problems()`, reads the Step 5 passage and reports a rank claim,
      an absence claim about `search_docs`, a marker for a `search_docs` query, the retired
      query, a `search_docs` sentence that does not say "ranked", and a passage that no longer
      names `search_docs` at all. The shipped passage must give none. The file also holds the
      fill route, the fixed-field reason, no figure, no date and no "active license" claim,
      that no Markdown file under `source/` names the retired query, and that
      `VERIFIED_QUERIES` has no record for it.
    - Its negative controls run on every pass: the passage as it shipped until this issue is
      reported for its rank claim, its absence claim and its marker; the passage as it read
      before it was first rescoped, in 2026-09, is reported for its absence claim; the
      corrected passage with only a marker put back, with a rank claim in a second sentence,
      or with the `search_docs` half deleted is reported for that alone; and the corrected
      passage is clean.
    - `tests/test_sdk_update_offer.py`: `StepTwoStatesNoPreviewClaim`, 8 tests where the class
      it replaces had 2. `preview_claims()` reports the word "preview" anywhere in Step 2,
      comments included, and any sentence that names the tap, the bucket or its package
      manager and gives it a support status. Step 2 must give none; the module must not hold
      the retired query or the notice's title; Step 2 must not point at "The update command";
      Step 1b must still state both update routes; and the platform list and rules 3 and 4
      must still name both native routes. Negative controls on every pass: each of the five
      retired pieces is reported, three rewordings without the word "preview" are reported,
      and Step 2's own corrected lines are not.
    - `tests/test_prescribed_search_queries.py` gains no test. Its
      `test_the_allowlist_has_no_dead_entries` is what required the two removals.
    - Negative control run once, in a throwaway clone of `0d1b82f` holding only the two
      rewritten test files: each gives `FAILED (failures=3)`.
    - Prose is matched with whitespace collapsed (INV-346). The marker check reads lines and
      says why at the read.
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. Nothing here shows what a live guide says at Step 2 or
    Step 5. The tests read Markdown and call no server: they cannot show what either README
    says on a later index. Verified on Linux only, with Python 3.12.3. The change is Markdown
    text and standard-library tests with no branch on the platform (INV-001), and it names no
    programming language's own mechanism (INV-002).
  - **Not changed.** The other dated markers and quotations in the same file, the Step 1b
    marker stamped server 1.37.14 among them (#38). How the Windows-with-Python route is
    chosen (#40). The `/auto-test` probe baseline (#50). `specs/mcp-coverage.jsonl`, whose
    2026-10-15 and 2026-10-19 rows record the preview claim as it then stood: it is a dated
    record written by its own command.
- **Invariants.** The register is not edited here (INV-365). INV-080, INV-194, INV-213, INV-219
  and INV-291 are not changed. The lines this change adds or edits under `source/` carry no ⛔
  and no bold MUST or NEVER, and `conformance.py since --since-last-audit` reports none from
  this change. The
  change ships one hard-rule line, in the docstring of
  `tests/test_record_limit_route_names_no_ranking.py`, and the block below covers it (INV-309).
  The Step 2 guard is not drafted as an invariant: it holds the text to what the server
  returned on the dates above, and the issue itself says the relay returns if a README
  carries the notice again, so it is INV-080 applied to one fact and not a standing rule about
  previews. Beyond the one block the change establishes no new invariant.

- **DEFERRED INVARIANT (resolved INV-436, registered by the maintainer 2026-11-18).** Module 2 Step 5's record-limit fallback says of `search_docs` only that its results are ranked. The rule already shipping, quoted:
    - ⛔ **Step 5's record-limit fallback says of `search_docs` only that its results are ranked: it never says which hit ranks where, never says that a query lacks the figure, and carries no `MCP-NEGATIVE` marker for a record-limit query.** — in `tests/test_record_limit_route_names_no_ranking.py`
    - `source/skills/module-02-sdk-setup/SKILL.md` — ⛔ Step 5's fallback gives as its reason for naming `sdk_guide` that it states the figure in a fixed field, `compatibility_notes`, while `search_docs` results are ranked, and says nothing else of `search_docs`

  Enforced by `tests/test_record_limit_route_names_no_ranking.py`.

  **Why it is not an existing invariant:** INV-080 says where a Senzing fact comes from, and
  the sentence it would have caught here was sourced: it was measured, dated and carried a
  marker, and an index rebuild made it false. INV-194 scopes a negative finding to the tool
  and parameters asked, which the retired marker did. INV-291 has an inline route record a
  rank band and a read-past note, and so permits a statement of which hit ranks where at a
  route the guide runs; this passage runs no `search_docs` route, so no band applies to it.
  INV-219 binds how a test reads such a claim, not whether shipped text makes one. So the
  ranking sentence could be written back, with a fresh date, and contradict no registered
  wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Module 2 Step 5's fallback, which fills `{record limit}` from `sdk_guide(topic='load', …, record_count=<above the default limit>)`, MUST give as its reason for naming that tool that `sdk_guide` states the figure in a fixed field, `compatibility_notes`, and MUST say of `search_docs` only that its results are ranked. The passage MUST NOT say which `search_docs` hit ranks where, MUST NOT say that a `search_docs` query lacks the figure, and MUST NOT carry an `MCP-NEGATIVE` marker for a record-limit `search_docs` query; no shipped file prescribes such a query and `VERIFIED_QUERIES` records none. Observed: the passage's statement about `search_docs` was made false twice by a rebuild of the docs index while the route it justified kept working. It first said the query returned no figure, and the index built 2026-09-24 carried an FAQ that states it. It then said the top-ranked hits state no figure and the FAQ ranks lower, and by 2026-11-17 (server 1.46.1, docs index 2026-11-14 17:44 UTC) the FAQ was the top hit. A reason that names a fixed field holds whichever hit comes first; a reason that describes a ranking is true of one build of the index. This binds one passage. It does not bind a route the guide runs, whose record carries a rank band and a read-past note under INV-291. (Relates to INV-080, INV-194 and INV-291.) Enforced by `tests/test_record_limit_route_names_no_ranking.py`. (Source: `two-module-2-claims-about-the-senzing-mcp-server-no-longer-hold`, 2026-11-18.)

- **Commit:** uncommitted

## the-packager-omits-symlinked-directories-unnamed-skips-utf-16-text-and-shares-the-feedback-file

- **Implemented:** 2026-11-18 (issue #46)
- **Files changed:** `source/scripts/package_bootcamp.py`,
  `source/skills/bootcamp-onboarding/packaging.md`, `source/commands/package-bootcamp.md`,
  `tests/test_package_bootcamp.py`, `tests/test_open_me_first_matches_the_manifest.py`,
  `tests/test_packaging_consent_gate_ships.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-18 against the change itself:
  it changes which of the bootcamper's own files the packager walks, scans and carries, and
  what the bootcamp's own text says about that. The three secret classes, the Senzing license
  payload among them, are read from `secret_patterns.py`, which does not change. That Windows
  PowerShell 5.1 writes UTF-16 from a `>` redirect is a statement about PowerShell, taken
  from the issue, and was not checked on a Windows machine here. Nothing says anything about
  Senzing or about what the Senzing MCP server serves. No absence claim about the server is
  made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** Four gaps between what `package_bootcamp.py` does and what its manifest and the
  consent question say are closed (`dry-run-2026-11-17`, finding 12, and a fourth gap found
  when the issue was refined). The file was read on `main` at `4486c25`, after #25, #28, #30,
  #31 and #45 changed it, and the new tests fail on that commit (see **Tests**).
  - **Symlinked directories.** `collect()` does not enter a symlinked directory, wherever it
    points, and lists it in `excluded` as `<path>/` with the reason "a symlinked directory;
    not followed, so nothing under it is packaged". Before, a link inside a walked tree was in
    neither the archive nor `excluded`, and a candidate root that was itself a link was walked,
    because `os.walk` follows the directory it starts on. A candidate root is now checked
    before the walk, and so is each directory above it inside the project: with `data` a link,
    `data/exports` is not entered and `data/` is named. A rule that matches the link's own
    path is reported first, as `excluded by rule: <rule>`, as before. The reason does not name
    the link's target. A root that is a link is not reported on the dry run's `absent:` line,
    which lists only roots that are not in the project.
  - **Windows directory junctions.** A junction is treated as a symlinked directory. It is
    read from the reparse tag `os.lstat` reports (`IO_REPARSE_TAG_MOUNT_POINT`), because
    `os.path.islink` does not report one and `os.path.isjunction` needs Python 3.12. No
    junction was created and nothing ran on Windows: one test gives the check a stand-in
    `lstat` result.
  - **Symlinked files.** A link that resolves inside the project is also checked against the
    exclusion rules by its resolved project-relative path. A match excludes it with the reason
    `excluded by rule: <rule> (the rule matches the path this link resolves to)`. So
    `docs/x.csv -> ../data/raw/customers.csv` is left out on both profiles, and a link named
    `notes.txt` that resolves to a `.db` file is left out of `share`. A link to a path no rule
    matches is packaged under the link's path, and a link that resolves outside the project
    keeps the reason `resolves outside the project root; not packaged`, both as before.
  - **UTF-16 text.** `_scan()` decodes each block as UTF-8, UTF-16 little-endian and UTF-16
    big-endian (`SCAN_ENCODINGS`) and applies the same patterns to each, so a secret is found
    in either byte order, with or without a byte-order mark. The decoders are incremental and
    each encoding carries its own tail, so a secret that straddles a scan-block boundary is
    found. The reason is unchanged: `excluded: content matched a secret pattern (<class>)`.
    No other encoding is read. `secret_patterns.py` and `write-gate.py` do not change, as the
    issue decides, so the write gate still reads UTF-8 only.
    The scan costs more, because each block is now decoded and searched three times.
    Measured once on the machine that did this work, on a 100 MiB file: 1.24 s before and
    2.09 s after for random bytes, and 0.33 s before and 0.59 s after for JSON lines.
  - **The feedback file and the in-progress recap.** `docs/feedback` and `docs/progress` are
    new `share`-only rules, so they match at any depth and appear in
    `exclusion_rules_applied.share_only`. `transfer` carries both directories.
  - **`OPEN_ME_FIRST.md`.** On `share`, the "What is NOT here, and why" list gains a bullet
    naming `docs/feedback/` and `docs/progress/`. On `transfer`, a sentence of its own after
    the profile paragraph names `docs/feedback/SENZING_BOOTCAMP_FEEDBACK.md` and
    `docs/progress/recap_checkpoint.md`, each only when the manifest's `included` list carries
    it. The profile paragraph and the "To resume" paragraph are byte for byte what they were,
    and a package with neither file reads as before.
  - **The consent question.** Option 2 reads as the issue gives it: "the above plus your
    database backup, saved bootcamp feedback, in-progress recap, config and mappings, …". The
    two new items sit on its first lines. Its last two physical lines are unchanged, and so
    is `tests/test_quoted_sizes_say_what_they_missed.py`, whose controls anchor on them.
    Options 1 and 3 are unchanged.
  - **Step 4 and the command.** The guarantee list in `packaging.md` Step 4 names the two
    paths as dropped by `share` and carried by `transfer`, and says that a symlinked directory
    is never followed and is named, that a symlinked file is checked by the path it resolves
    to, and that the content scan reads UTF-16 text. The profile summary in
    `source/commands/package-bootcamp.md` names the two paths as dropped by `share` and
    carried by `transfer`. No line carrying a ⛔ was edited.
  - **Compatibility.** No command-line option changes. `PACKAGE_MANIFEST.json` keeps
    `"schema": 1` and its keys.
  - **Not changed.** Other content under `docs/` that `share` carries. `SECRET_PATTERN` and
    the write gate's secret check. Step 5 of `packaging.md`. The `absent:` report.
  - **Every assistant.** Every changed passage sits outside every host marker and names no
    assistant, so all five packages get the same text. `python3 -m tools.bootcamp_build check`
    passes.
  - **Tests.** 51 new tests in three existing files.
    - `tests/test_package_bootcamp.py` gains four classes, 32 tests. Eleven read symlinked
      directories: a link that resolves inside the project and one that resolves outside it,
      on both profiles; a candidate root that is a link, inside and outside; a root below a
      linked directory; a rule matching the link's own path; the written archive and its
      manifest; the reason's wording and that the manifest names no target; the control
      below; a real directory and a linked file, which are not linked directories; and the
      junction stand-in. Seven read symlinked files, the first of them from the members of a
      written `share` archive. Seven read UTF-16: four forms of each of the three secret
      classes, a secret straddling a block boundary in each form, an odd block length, the
      written archive, and clean UTF-16 text that still travels. Six read the two new rules,
      on written `share` and `transfer` archives, and one more reads the consent question
      against the rules.
    - `tests/test_open_me_first_matches_the_manifest.py` gains three classes, 10 tests: both
      files named, one, the other and neither; a partial package; a file on disk that the
      secret scan excludes and that is therefore not named; and the `share` list.
    - `tests/test_packaging_consent_gate_ships.py` gains three classes, 9 tests: option 2
      word for word, its last two physical lines, options 1 and 3, the Step 4 list and the
      command's summary.
    - A test that needs a symlink skips, with its reason, where the platform cannot create
      one. None skipped on the machine that ran them.
    - Every secret-shaped string the new cases use is put together when the test runs, from a
      pattern's fixed prefix and characters drawn from a seeded generator. None is written
      in a file whole.
    - Negative controls that run on every pass (INV-265): with the link check switched off,
      a link inside a walked tree is in neither list and a linked root is walked; with the
      scan reading UTF-8 only, all twelve UTF-16 fixtures are packaged; a link's own path
      matches no rule; and the text a complete package carries fails each `OPEN_ME_FIRST.md`
      case.
    - Negative control run once, in a throwaway clone of `4486c25` holding only the three
      test files: `tests/test_package_bootcamp.py` gives `FAILED (failures=42, errors=13)`,
      `tests/test_open_me_first_matches_the_manifest.py` gives
      `FAILED (failures=6, errors=1)` and `tests/test_packaging_consent_gate_ships.py` gives
      `FAILED (failures=8, errors=1)`. That run was made before the odd-block-length test
      was added.
    - Thirteen small changes to the script were each tried once in that clone, with the
      whole change applied, and each turns at least one of the three files red: a walked link not named, a linked root
      followed, no resolved-path check, UTF-8 only, no big-endian read, no carried tail,
      either rule dropped, the `transfer` sentence dropped, the `share` bullet dropped, the
      sentence built from something other than `included`, the junction tag ignored, and a
      decoder that is not incremental.
    - Prose is matched with whitespace collapsed (INV-346).
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. Nothing here shows what a live guide asks or says.
    Verified on Linux only, with Python 3.12.3: no run on macOS or on Windows happened, no
    Windows junction was created, and no file written by Windows PowerShell 5.1 was read. The
    script uses the standard library only and has no branch on the platform (INV-001), and
    nothing in the change is specific to a programming language (INV-002).
  - **Drafted, not filed.** One finding outside this issue's scope, for the maintainer to
    file or drop. It was seen on `4486c25` and is unchanged by this work.
    - *Title:* The packager stops with a traceback on a symlink loop.
    - *Body:* `collect()` in `source/scripts/package_bootcamp.py` calls `Path.resolve()` on
      each member and catches `OSError`. On Python 3.12.3, a link that loops (`docs/a -> b`,
      `docs/b -> a`) makes `resolve()` raise `RuntimeError: Symlink loop from …`, which is not
      caught, so `--dry-run` and the write both end in a traceback and no archive is written.
      Expected: the link is listed in `excluded` with a reason and the run goes on, as it does
      for an unreadable member. Seen by running the script on a scratch directory holding one
      file and the two links.
- **Invariants.** The register is not edited here (INV-365). INV-109, INV-135 and INV-410 are
  not changed. The change ships three hard-rule lines, all in the docstring of
  `tests/test_package_bootcamp.py`. `since` does not report them, because `tests/` is not a
  rule home. The lines this change adds or edits under `source/` carry no ⛔ and no bold MUST
  or NEVER. The three blocks below cover the three rules (INV-309). Beyond them the change
  establishes no new invariant.

- **DEFERRED INVARIANT (resolved INV-437, registered by the maintainer 2026-11-18).** The packager never follows a link into a path it would leave out, and names what it did not enter. The rule already shipping, quoted:
    - ⛔ **The packager never enters a symlinked directory and always names it, and it checks a symlinked file by the path it resolves to.** — in `tests/test_package_bootcamp.py`
    - `source/scripts/package_bootcamp.py` — ⛔ `collect()` checks each candidate root and each directory the walk lists, names a linked one in `excluded`, and checks a member's resolved path against the exclusion rules
    - `source/skills/bootcamp-onboarding/packaging.md` — ⛔ Step 4's "Symlinks resolved, then compared" bullet says a symlinked directory is never followed and is named, and a symlinked file is checked by the path it resolves to

  Enforced by `tests/test_package_bootcamp.py` (`ASymlinkedDirectoryIsNeverEnteredAndIsNamed`,
  `ASymlinkedFileIsCheckedByThePathItResolvesTo`).

  **Why it is not an existing invariant:** INV-410 says that `share` carries none of the
  loader inputs wherever they sit, that an exclusion rule matches its segments at any depth,
  and that each excluded path is named with its rule. It reads a path's own segments, and a
  link's own path matches no rule, so it did not stop `docs/x.csv` from carrying a file under
  `data/raw/`. It also binds the loader inputs on `share`, not every rule on both profiles,
  and says nothing about a directory the walk does not enter. INV-200 governs where the
  bootcamp writes; the packager's check for a link that leaves the project borrows its
  resolve-then-compare and is not stated by it. The packaging feature's own invariant, Draft
  1 of `the-bootcamp-cannot-leave-the-machine-it-was-built-on`, names symlink resolution and
  has been held since 2026-08-27. The maintainer may fold this wording into Draft 1 when
  registering it; that is a different act and is not drafted here.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — `package_bootcamp.py` MUST NOT enter a symlinked directory, whether it resolves inside or outside the project, and whether it is found during the walk, is a candidate root itself or is a directory above a candidate root inside the project. A Windows directory junction counts as a symlinked directory. Each one MUST be listed in `PACKAGE_MANIFEST.json`'s `excluded` list as `<path>/`: with the rule, when an exclusion rule matches the link's own path, and otherwise with a reason saying it is a symlinked directory that was not followed. That reason MUST NOT name the link's target, because the manifest travels with the archive and a target can hold a user name or a path outside the project. A symlinked file that resolves inside the project MUST be checked against the profile's exclusion rules by its resolved project-relative path as well as by its own path; a match on either MUST exclude it, and the reason MUST name the rule. A link that resolves to a path no rule matches is packaged under the link's path, and a link that resolves outside the project is excluded and named as resolving outside the project root. Observed (`dry-run-2026-11-17`, finding 12, and the refinement of issue #46): a symlinked directory was in neither the archive nor `excluded`, and on `share` a link under `docs/` to a file under `data/raw/` was packaged under the link's name. Enforced by `tests/test_package_bootcamp.py`, which builds the links in fixture projects and skips, with its reason, where the platform cannot create one; it was run on Linux only, creates no junction (the junction case is a stand-in `lstat` result), and **cannot** establish what a live packaging run on a Bootcamper's project excludes. (Source: `the-packager-omits-symlinked-directories-unnamed-skips-utf-16-text-and-shares-the-feedback-file`, GitHub issue #46, 2026-11-18.)

- **DEFERRED INVARIANT (resolved INV-438, registered by the maintainer 2026-11-18).** The packager's secret scan reads UTF-16 text as well as UTF-8. The rule already shipping, quoted:
    - ⛔ **The packager's secret scan reads every member as UTF-16 text as well as UTF-8.** — in `tests/test_package_bootcamp.py`
    - `source/scripts/package_bootcamp.py` — ⛔ `_scan()` decodes each block in every encoding in `SCAN_ENCODINGS` and applies the secret patterns to each
    - `source/skills/bootcamp-onboarding/packaging.md` — ⛔ Step 4's "Content-scanned" bullet says the scan reads each member as UTF-8 and as UTF-16 text, in either byte order, with or without a byte-order mark

  Enforced by `tests/test_package_bootcamp.py` (`Utf16TextIsScannedForSecrets`).

  **Why it is not an existing invariant:** INV-109 names the three secret classes the write
  gate must detect. It binds `write-gate.py`, and it says nothing about the packager or about
  the encoding a file is read in. `tests/test_secret_patterns_are_shared.py` holds the two
  pattern strings equal and says itself that equal patterns do not establish equal
  application. Draft 1 of `the-bootcamp-cannot-leave-the-machine-it-was-built-on`, held since
  2026-08-27, covers a byte-level scan with no file-type allowlist and names no encoding. So
  the scan could go back to reading UTF-8 only and contradict no registered wording. The
  maintainer may fold this into Draft 1 instead.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — `package_bootcamp.py`'s content scan MUST apply the secret patterns to every member read as UTF-8 text and as UTF-16 text, little-endian and big-endian, with or without a byte-order mark, and MUST find a pattern that straddles a scan-block boundary in each of them. A member that matches in any of those readings MUST be excluded and named in `PACKAGE_MANIFEST.json` with the secret's class, and the manifest MUST NOT echo the matched text. No other encoding is read. This binds the packager only: the write gate's secret check (INV-109) is not changed by it. Observed (`dry-run-2026-11-17`, finding 12): a UTF-16 file holding a synthetic secret-shaped id was packaged, because the scan decoded it as UTF-8; Windows PowerShell 5.1 writes UTF-16 from a `>` redirect. Enforced by `tests/test_package_bootcamp.py`, which writes each of the three secret classes in the four UTF-16 forms from strings put together at run time; it was run on Linux only, reads no file that PowerShell wrote, and **cannot** establish that a secret in some other encoding is found. (Source: `the-packager-omits-symlinked-directories-unnamed-skips-utf-16-text-and-shares-the-feedback-file`, GitHub issue #46, 2026-11-18.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The saved bootcamp feedback and the in-progress recap travel on `transfer` only, and each profile's text says so. The rule already shipping, quoted:
    - ⛔ **The saved bootcamp feedback and the in-progress recap travel on `transfer` only, and each profile's text says so.** — in `tests/test_package_bootcamp.py`
    - `source/scripts/package_bootcamp.py` — ⛔ `SHARE_EXCLUDE` holds `docs/feedback` and `docs/progress`, and `open_me_first()` names the two files on `transfer` from the manifest's `included` list and lists both directories on `share` among what is not there
    - `source/skills/bootcamp-onboarding/packaging.md` — ⛔ option 2 of the pinned question names the saved bootcamp feedback and the in-progress recap and option 1 does not, and Step 4's "Never packaged on `share`" bullet names both paths and says `transfer` carries them
    - `source/commands/package-bootcamp.md` — ⛔ the profile summary says both paths are dropped by `share` and carried by `transfer`

  Enforced by `tests/test_package_bootcamp.py` (`TheWorkingNotesTravelOnTransferOnly`),
  `tests/test_open_me_first_matches_the_manifest.py` and
  `tests/test_packaging_consent_gate_ships.py`.

  **Why it is not an existing invariant:** INV-410 binds the loader inputs on `share` and how
  a rule matches, not the feedback file or the recap checkpoint. INV-015 says where feedback
  is captured, and nothing about whether it travels in a package. INV-388 binds the size an
  option quotes, and INV-051 and INV-056 the form and pinning of the question, not which
  files an option names. The deferred rule that `OPEN_ME_FIRST.md` says only what the
  manifest includes (issue #321, held 2026-10-02) covers how the `transfer` sentence is
  built, and does not say which profile carries these two files. So `share` could carry the
  bootcamper's own feedback text again, or option 2 could stop naming it, and contradict no
  registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — The packaged `share` profile MUST carry nothing under `docs/feedback/` or `docs/progress/`, wherever in the project tree they sit: the saved bootcamp feedback and the in-progress recap are the Bootcamper's working notes, in their own words, and not results. Each MUST be an exclusion rule of that profile, named in `PACKAGE_MANIFEST.json`'s `excluded` list where it applied and listed in `exclusion_rules_applied.share_only`, and `OPEN_ME_FIRST.md` on `share` MUST list both among what is not there. The `transfer` profile MUST carry both, and its `OPEN_ME_FIRST.md` MUST name `docs/feedback/SENZING_BOOTCAMP_FEEDBACK.md` and `docs/progress/recap_checkpoint.md` each only when the manifest's `included` list carries it. The pinned consent question in `packaging.md` MUST name the saved bootcamp feedback and the in-progress recap in the option that produces `transfer` and MUST NOT name them in the option that produces `share`, and `packaging.md` Step 4 and `source/commands/package-bootcamp.md` MUST say which profile carries them. A project with neither file packages without error. Observed (`dry-run-2026-11-17`, finding 12): `share` carried `docs/feedback/SENZING_BOOTCAMP_FEEDBACK.md` and `docs/progress/recap_checkpoint.md`, and neither the consent question nor `OPEN_ME_FIRST.md` named them. Enforced by `tests/test_package_bootcamp.py`, `tests/test_open_me_first_matches_the_manifest.py` and `tests/test_packaging_consent_gate_ships.py`, which read archives built from fixtures and the shipped wording; they **cannot** establish what a live guide asks, and they say nothing about other content under `docs/` that `share` carries. (Source: `the-packager-omits-symlinked-directories-unnamed-skips-utf-16-text-and-shares-the-feedback-file`, GitHub issue #46, 2026-11-18.)

  **HELD 2026-11-18:** held with the other packaging blocks,
  `the-bootcamp-cannot-leave-the-machine-it-was-built-on` (Draft 1) and
  `open-me-first-says-only-what-the-manifest-includes`, because it pins `OPEN_ME_FIRST.md`
  content in the same feature. Revisit after `dry-run` phase 3 has exercised packaging.

- **Commit:** uncommitted

## restated-rules-and-lists-in-shipped-text-have-drifted-from-their-source

- **Implemented:** 2026-11-17 (issue #45)
- **Files changed:** `source/skills/module-01-business-problem/phase2-document-confirm.md`,
  `source/skills/module-02-sdk-setup/SKILL.md`,
  `source/skills/module-03-system-verification/phase2-report-close.md`,
  `source/skills/module-03b-truthset-visualization/phase2-close.md`,
  `source/skills/module-04-data-collection/SKILL.md`,
  `source/skills/module-05-data-quality-mapping/phase2-data-mapping.md`,
  `source/skills/bootcamp-onboarding/ground-rules.md`, `source/skills/graduation/SKILL.md`,
  `source/hooks/fallbacks/checkpoint-tick.md`, `source/scripts/package_bootcamp.py`,
  `tests/test_gate_options_have_handling_steps.py`,
  `tests/test_generated_scenario_marker_drop_is_exempt.py`,
  `tests/test_restatements_say_what_their_source_says.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it corrects seven places where the bootcamp's own text restates the bootcamp's own text, a
  register entry or a test file. The order in which Module 4 recommends CORD, the free-data
  catalog and generated data is the bootcamp's own recommendation, already stated in the file,
  and the offer's description of the catalog is unchanged. `docs/mapping/{source_name}_mapper.md`
  is a file the bootcamp defines. None of that says anything about Senzing or about what the
  Senzing MCP server serves. No absence claim about the server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** Seven restatements in shipped text now say what their source says. These are
  findings 15, 20, 21, 28 and 29 of `production-readiness-audit-2026-11-17`, and the two parts
  of finding 23 that #32 did not take. Each was read on `main` at `59025e1` first: none had
  been corrected by an earlier merge, and the new tests fail on that commit (see **Tests**).
  - **Module closes (finding 20).** The closes of Discover the Business Problem and SDK setup
    listed "update progress, append the recap section, present the end-of-module summary" and
    left out Step 0. Both now use the form Data collection, Data processing and Query,
    Visualize and Discover already use: its Step 0 checks, update progress, append the recap
    section, present the summary. The close of Data Quality, Mapping, and Transformation named
    Step 0, then the summary, then the recap, and no progress update. It now gives Step 0,
    progress, the recap section (INV-085), the summary (INV-032) and the completion line
    (INV-079), in that order. The closes of System verification and Truth Set visualization
    number the steps 1 to 4; each now says "Run Module Completion's Step 0 checks first, then:"
    before item 1. The numbered items are unchanged.
  - **Module 4's data hierarchy (finding 21).** The secondary offer, made when CORD is
    declined, gave "Free raw data" and "Synthesized test data" as two equal options. It is
    still one quote with both entries and no question. Its lead now says "I recommend free raw
    data next. If nothing in that collection fits, I can generate test data instead", the
    first entry opens "Recommended." and the second opens "The fallback, when nothing in that
    collection fits." The "Synthesized test data" entry under **Handling each answer** and
    the hierarchy under **Agent behavior** already gave that order and are unchanged. Both
    entry names are unchanged, so the handling entries keyed on them still match. The scope of
    "last resort" is unchanged.
  - **Two citations (finding 15).** The sentence above the stage table states two subjects,
    one row per stage (INV-140) and one level per row (INV-141), and cited INV-140 alone. It
    now cites both. The list of retired nudge rules named INV-141, which is in force: the
    register lists it in its group's main list, and its 2026-11-16 amendment keeps "exactly
    one effort level" per row. INV-141 is removed from that list. The other five ids are in
    the register's "Fully superseded" list for the group.
  - **The marker's readers (finding 23).** Graduation's Step 5b listed the readers of the
    generated-scenario marker by step number and left out Module 6 Phase C step 13. It now
    names them by module and phase: Module 4, Module 6 Phase C and Module 6 Phase D. The
    docstring of `tests/test_generated_scenario_marker_drop_is_exempt.py` repeated the list
    and is brought to the same form. The marker string is unchanged.
  - **The checkpoint fallback (finding 23).** `source/hooks/fallbacks/checkpoint-tick.md` said
    the checkpoint is refreshed "as `module-completion.md` describes". The rule is the
    "In-progress recap checkpoint" rule in `ground-rules.md`, and the fallback now points
    there, in the form `failed-run-net.md` uses for "Worked steers". The rule itself is
    unchanged.
  - **The packager's comment (finding 28).** The comment above `DATABASE_BACKUP_ROOT` named
    `tests/test_package_bootcamp.py` as the test that pins the constant to the tuple. That
    file does not read the constant; `tests/test_quoted_sizes_say_what_they_missed.py` does,
    and the comment now names it. No code changes.
  - **Module 5's per-source documents (finding 29).** Step 18 wrote
    `docs/mapping/mapping_[name].md` and `docs/mapping/{source_name}_mapper.md` for each
    source, and only `_mapper.md` is read. Step 18 no longer writes the first. The structure
    it gives for `_mapper.md` gains a `## How to run` section, between `## Quality Notes` and
    `## Record Type Check`, naming the transformation program (the shared one when it is
    shared) and the command that runs it on this source. That was the only content the
    dropped document had that `_mapper.md` lacked. The lead sentence now says `_mapper.md` is
    the source's one mapping document. The transformation lineage document and the
    `## Record Type Check` section are unchanged.
  - **Not changed.** The reader list of `bootcamp_complete()`, which #32 settled. The text of
    `specs/INVARIANTS.md`. The closes of Entity Resolution Concepts and Bootcamp preparation.
    The "In-progress recap checkpoint" rule. The other ids in the retired list, and whether
    that list is complete. A `docs/mapping/mapping_[name].md` already in a project from an
    earlier run: no step deletes, migrates or reads it.
  - **Every assistant.** Every changed passage sits outside every host marker and names no
    assistant, so all five packages get the same text. `python3 -m tools.bootcamp_build check`
    passes.
  - **Tests.** `tests/test_restatements_say_what_their_source_says.py` is new, with 35 tests
    in five classes, and `tests/test_gate_options_have_handling_steps.py` gains
    `Module4StatesOneDataHierarchy`, with 5 tests.
    - Ten read the module closes. The order of the steps is read from the opening of
      `module-completion.md` and checked against that file's `## Step N:` headings. A close
      is found by scanning `source/skills/` for the phrase "standard **Module Completion**
      process" (INV-246), and every module directory but Entity Resolution Concepts' must
      have one that lists the steps. Each close must name Step 0 first and keep the order.
    - Six read the two citations. The retired list is compared with the "Fully superseded"
      lists read from the index of `specs/INVARIANTS.md`, and the register's own entries for
      INV-140 and INV-141 must state the two subjects and be in force.
    - Eight read the marker's readers. A reader is any file under `source/skills/` that
      contains the marker's text and is neither Module 1's writer nor `graduation/SKILL.md`.
      Its name in the list is read from its path, and a marker that wraps across a line is
      still found. The marker test's docstring must repeat graduation's list.
    - Four read the fallback's pointer and the packager's comment: the pointer names a rule
      that `ground-rules.md` opens by that name, and the comment names a test file that
      exists and reads the constant.
    - Seven read Module 5: no file under `source/` names a `docs/mapping/mapping_…`
      document, step 18 names one mapping document beside the lineage, and the structure has
      `## How to run` and `## Record Type Check`.
    - Five read Module 4: the offer's order and the word each entry carries, no 👉 in the
      offer, "last resort" in the handling entry, and the three steps of the hierarchy under
      **Agent behavior** in order.
    - Negative controls run on every pass (INV-265): each close as it shipped, the order
      changed in `module-completion.md` (every close then fails), INV-141 put back in the
      retired list, either citation dropped, a reader left out of the list, a new reader not
      listed, the old pointer, a comment naming a test that does not read the constant, the
      dropped document put back, the structure without its section, the offer as it shipped,
      its entries swapped and a question added to it.
    - Negative control run once, in a throwaway clone of `59025e1` holding only the two test
      files: 21 of the 35 new tests fail (`FAILED (failures=21, errors=2)`), and 3 of the 5
      Module 4 tests fail (`FAILED (failures=3)`).
    - Prose is matched with whitespace collapsed (INV-346). Two reads are by line on purpose
      and say why: the register's index, and the headings inside the fenced structure.
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. Nothing here shows that a live guide runs Step 0 at a
    close, recommends free raw data before generated data, or writes a `## How to run`
    section. Verified on Linux only, with Python 3.12.3. The change is Markdown, one Python
    comment and tests that use `pathlib` and read UTF-8, with no branch on the platform and
    nothing specific to a programming language (INV-001).
- **Invariants.** The register is not edited here (INV-365). INV-140 and INV-141 are
  unchanged: this change corrects two citations of them, not their text. The change ships
  three hard-rule lines, two in the docstring of
  `tests/test_restatements_say_what_their_source_says.py` and one in the docstring of
  `tests/test_gate_options_have_handling_steps.py`. `since` does not report them, because
  `tests/` is not a rule home. The lines this change adds or edits under `source/` carry no ⛔
  and no bold MUST or NEVER. The three blocks below cover the three rules that govern what the
  guide does or says: the order of a module close, Module 4's data hierarchy and Module 5's
  one mapping document (INV-309). The other four corrections establish no new invariant. Each
  is a reference, not a rule: a citation and a list of retired ids that restate the register,
  a list of the marker's readers, a pointer at a ground rule and a comment naming a test.
  What each restates is owned by the place it names, and the new tests hold each one to that
  place under INV-003.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** A module close that lists Module Completion's steps lists them in its order, Step 0 first. The rule already shipping, quoted:
    - ⛔ **A module close that lists the steps of Module Completion names its Step 0 first, then progress, recap and summary, in the order `module-completion.md` fixes.** — in `tests/test_restatements_say_what_their_source_says.py`
    - `source/skills/module-01-business-problem/phase2-document-confirm.md` — ⛔ the close lists Module Completion's Step 0 checks, the progress update, the recap section and the summary, in that order
    - `source/skills/module-02-sdk-setup/SKILL.md` — ⛔ the close lists Module Completion's Step 0 checks, the progress update, the recap section and the summary, in that order
    - `source/skills/module-03-system-verification/phase2-report-close.md` — ⛔ the close says to run Module Completion's Step 0 checks first, before its numbered item 1
    - `source/skills/module-03b-truthset-visualization/phase2-close.md` — ⛔ the close says to run Module Completion's Step 0 checks first, before its numbered item 1
    - `source/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — ⛔ the close lists Step 0's checks, the progress update, the recap section, the summary and the completion line, in that order

  Enforced by `tests/test_restatements_say_what_their_source_says.py`.

  **Why it is not an existing invariant:** INV-032 requires the end-of-module summary, INV-085
  the name-based recap section and INV-413 the fields Step 1 writes, and INV-413's dated note
  says Step 0 runs before Step 1's write. Each binds `module-completion.md` or one step of
  it. None says that a module close which restates the steps names all of them, or names them
  in that order. INV-300 binds a site that claims a rule is stated once, and a close claims
  nothing of the kind. So a close could again leave out Step 0, or put the summary before the
  recap, and contradict no registered wording. The maintainer may prefer a dated note on
  INV-413; that is a different act and is not drafted here.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — A module close that lists the steps of Module Completion MUST name its Step 0 checks first, then updating progress, appending the module's recap section and presenting the end-of-module summary, in the order the opening of `module-completion.md` fixes. A close that names two or more of those steps MUST name all four. A close MAY instead point at the process and list no step. On 2026-11-17 eight closes list the steps: Discover the Business Problem, SDK setup, System verification, Truth Set visualization, Data collection, Data Quality, Mapping, and Transformation, Data processing, and Query, Visualize and Discover. Entity Resolution Concepts runs the process step by step and departs from it on purpose, and is not bound by this. Observed (`production-readiness-audit-2026-11-17`, finding 20): two closes listed the steps without Step 0, one put the summary before the recap, and two numbered the steps 1 to 4 and left Step 0 out, while Step 0's filings run in every module. ⚠️ Limits: the enforcer reads `source/`, finds a close by the phrase "standard **Module Completion** process", reads it up to the module's transition question and takes the first mention of each step. It reads the order from the opening of `module-completion.md`. It **cannot** establish that a live guide runs Step 0 at a module close. Enforced by `tests/test_restatements_say_what_their_source_says.py`. (Source: `restated-rules-and-lists-in-shipped-text-have-drifted-from-their-source`, GitHub issue #45, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Module 4 states one data hierarchy, and its three statements of it agree. The rule already shipping, quoted:
    - ⛔ **Module 4 states one data hierarchy: CORD first, then free raw data, then synthesized test data.** — in `tests/test_gate_options_have_handling_steps.py`
    - `source/skills/module-04-data-collection/SKILL.md` — ⛔ the secondary offer gives "Free raw data" first as the recommended choice and "Synthesized test data" second as the fallback, in one quote with no question

  Enforced by `tests/test_gate_options_have_handling_steps.py`.

  **Why it is not an existing invariant:** INV-284 requires a handling step for every option
  a pinned gate offers, and its enforcer already reads this offer's two entries. It does not
  say in what order the bootcamp recommends data. INV-197 requires a recommended resource's
  known limits to be stated wherever it is recommended. It does not rank one resource against
  another. The hierarchy itself is stated under **Agent behavior** and cites no invariant. So
  the offer could again give generated data beside the catalog as an equal choice, and
  contradict no registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — For a Bootcamper who has no data, has no bootcamp-generated scenario and did not choose option 5 of the provision question, Data collection MUST state one data hierarchy: CORD first, then free raw data from the free-data catalog, then synthesized test data. Its three statements of that order MUST agree. The secondary offer, made when CORD is declined, MUST give "Free raw data" first as the recommended choice and "Synthesized test data" second as the fallback when nothing in the catalog fits, as one offer in one turn with no 👉. The "Synthesized test data" entry under **Handling each answer** calls it the last resort. The hierarchy under **Agent behavior** lists the three in that order. The offer's two entry names MUST stay as they are, since the handling entries are keyed on them (INV-284). "Last resort" is not a judgment on `provenance: synthesized` from the Business Case Offer, nor on option 5 of the provision question. Observed (`production-readiness-audit-2026-11-17`, finding 21): the offer gave synthesized data beside free raw data with no order, while two other passages of the same file called it a last resort. ⚠️ Limits: the enforcer reads the three passages of `source/skills/module-04-data-collection/SKILL.md` and asserts what they state. It **cannot** establish what a live guide recommends. Enforced by `tests/test_gate_options_have_handling_steps.py`. (Source: `restated-rules-and-lists-in-shipped-text-have-drifted-from-their-source`, GitHub issue #45, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Module 5 writes one per-source mapping document, and how to run the transformation is in it. The rule already shipping, quoted:
    - ⛔ **Module 5 writes one per-source mapping document, `docs/mapping/{source_name}_mapper.md`, and its structure has a `## How to run` section.** — in `tests/test_restatements_say_what_their_source_says.py`
    - `source/skills/module-05-data-quality-mapping/phase2-data-mapping.md` — ⛔ step 18 names no mapping document but `_mapper.md` beside the transformation lineage, and the structure it gives has a `## How to run` section

  Enforced by `tests/test_restatements_say_what_their_source_says.py`.

  **Why it is not an existing invariant:** INV-177 requires source-qualified names for
  per-source artifacts and names the `{source_name}_` form of `_mapper.md` as the one to
  use. It does not say there is one mapping document per source. INV-335 and INV-336 govern
  the `## Record Type Check` section of `_mapper.md` and when Phase 2 reads it. They do not
  say what else the file holds. INV-042 and INV-043 require the transformation code and its
  output, not a record of how to run it. So a second per-source document could be written
  again, or `## How to run` dropped, and contradict no registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Data Quality, Mapping, and Transformation MUST write one per-source mapping document, `docs/mapping/{source_name}_mapper.md`, and no file under `source/` may name a `docs/mapping/mapping_…` document. The structure step 18 gives for `_mapper.md` MUST have a `## How to run` section that names the transformation program, the shared program when one serves several sources, and the command that runs it on that source. The file stays per-source when the program is shared. The `## Record Type Check` section Phase 1 writes is kept as written (INV-335). `docs/mapping/transformation_lineage_[name].md` is a separate document and is not bound by this. A `docs/mapping/mapping_[name].md` left in a project by an earlier run is left alone: nothing deletes, migrates or reads it. Observed (`production-readiness-audit-2026-11-17`, finding 29): step 18 wrote two overlapping per-source documents, and only `_mapper.md` was read. ⚠️ Limits: the enforcer reads `source/` and the fenced structure in step 18. It **cannot** establish that a live guide writes the section, or what it writes there. Enforced by `tests/test_restatements_say_what_their_source_says.py`. (Source: `restated-rules-and-lists-in-shipped-text-have-drifted-from-their-source`, GitHub issue #45, 2026-11-17.)

- **Commit:** uncommitted

## selected-modules-is-kept-in-two-files-and-the-text-disagrees-on-which-is-read

- **Implemented:** 2026-11-17 (issue #44)
- **Files changed:** `source/skills/bootcamp-preparation/SKILL.md`,
  `source/skills/bootcamp-onboarding/module-completion.md`,
  `source/skills/module-00-entity-resolution-concepts/SKILL.md`,
  `source/skills/module-03-system-verification/phase2-report-close.md`,
  `source/skills/module-03b-truthset-visualization/phase2-close.md`,
  `.claude/skills/dry-run/scaffold_project.py`,
  `tests/test_selected_modules_is_kept_in_one_file.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes which of the bootcamp's own two state files holds the module selection, and what
  five steps say about that. None of that says anything about Senzing or about what the
  Senzing MCP server serves. No absence claim about the server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** The module selection, `selected_modules`, is now kept in one file,
  `config/bootcamp_preferences.yaml`. This is finding 14 of
  `production-readiness-audit-2026-11-17`.
  - **Bootcamp preparation.** Step 6 wrote the list twice: in its consolidated preferences
    write, and again into `config/bootcamp_progress.json`, where it said module completion and
    the journey map read it. The second write now sets `current_module` to the first content
    module and nothing else. Its paragraph says the selection is kept in the preferences file,
    which the consolidated write has already written and which module completion and the
    journey map read. The consolidated write, Step 0's rule for a saved selection and the line
    telling the Bootcamper to edit the preferences file are unchanged.
  - **The four readers.** Four steps set `current_module` to the next module in
    `selected_modules` inside a write to the progress file, and named no file for the list.
    Each now names `config/bootcamp_preferences.yaml` as the file it is read from: module
    completion's Step 1 and the closes of Entity Resolution Concepts, System verification and
    Truth Set visualization. Module completion's bullet keeps "next module in
    `selected_modules`" and "unconditionally", which
    `tests/test_module_completion_step1_lists_every_write.py` requires.
  - **The dry-run scaffold.** `PROGRESS` no longer holds a `selected_modules` key, so no mode
    writes one to the progress file. `PREFERENCES`, the mid-bootcamp fixture, gains the same
    eleven tokens in the same order. `SEEDED_PREFERENCES` is unchanged.
  - **Not changed.** The other mentions of `selected_modules` that name no file. A
    `selected_modules` key already in the progress file of a bootcamp in progress: nothing
    reads it and nothing removes it. What happens when the selection is edited so that
    `current_module` is no longer in the list. No hook, shipped script or bootcamper-facing
    text changes, and no script read the key.
  - **Every assistant.** The five passages sit outside every host marker, so every package
    gets the same text. `python3 -m tools.bootcamp_build check` passes.
  - **Tests.** `tests/test_selected_modules_is_kept_in_one_file.py` is new, with 23 tests.
    - Eight read Bootcamp preparation's Step 6. Its one write to the progress file sets
      `current_module`, points at the first content module and does not name the list, and
      its preferences write carries the list.
    - Eight read the readers. Each of the four recorded files, and any file under `source/`
      with such a step, names the preferences file beside the list in the same sentence. No
      item under `source/` names the list beside the progress file without that.
    - Seven build the scaffold in all three modes. No progress file carries the key, the mid
      preferences file carries the list in the order of Bootcamp preparation's own Core list
      (INV-246), and that list holds the module the progress fixture is on.
    - Negative controls run on every pass (INV-265): the paragraph as it shipped, the list put
      back into the progress write, a write with no `current_module`, each of the four sites
      with the progress file, another file or no file named, a site reworded so it is no
      longer found, a file named in another sentence or for another key, and a progress file
      holding the key.
    - Negative control run once, in a throwaway clone of `227b0ca` holding only the new test
      file: 11 of the 23 tests fail (`FAILED (failures=23)`).
    - Text is matched one list item or paragraph at a time with whitespace collapsed
      (INV-346).
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. Nothing here shows that a live guide reads the list from
    the preferences file. Verified on Linux only, with Python 3.12.3. The change is Markdown,
    one Python fixture and a test that uses `pathlib` and reads UTF-8, with no branch on the
    platform and nothing specific to a programming language (INV-001).
- **Invariants.** The register is not edited here (INV-365). INV-076 is unchanged: it does not
  say where the list is stored. The change ships two hard-rule lines, both in the docstring of
  `tests/test_selected_modules_is_kept_in_one_file.py`. `since` does not report them, because
  `tests/` is not a rule home. The lines this change adds under `source/` carry no ⛔ and no
  bold MUST or NEVER. The block below covers the rule (INV-309). It is one block because it has
  one subject: which file holds the module selection.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The module selection is kept in one file, and a step that reads it names that file. The rule already shipping, quoted:
    - ⛔ **`selected_modules` is kept in one file, `config/bootcamp_preferences.yaml`, and nothing writes it to `config/bootcamp_progress.json`.** — in `tests/test_selected_modules_is_kept_in_one_file.py`
    - ⛔ **A step that sets `current_module` to the next module in `selected_modules` names `config/bootcamp_preferences.yaml` as the file the list is read from.** — in `tests/test_selected_modules_is_kept_in_one_file.py`
    - `source/skills/bootcamp-preparation/SKILL.md` — ⛔ Step 6's write to the progress file sets `current_module` to the first content module and no other key, and says the selection is kept in the preferences file
    - `source/skills/bootcamp-onboarding/module-completion.md` — ⛔ Step 1's `current_module` bullet says to read the list from the preferences file
    - `source/skills/module-00-entity-resolution-concepts/SKILL.md` — ⛔ Step 2's progress write names the preferences file as where the list is read from
    - `source/skills/module-03-system-verification/phase2-report-close.md` — ⛔ the close's progress update names the preferences file as where the list is read from
    - `source/skills/module-03b-truthset-visualization/phase2-close.md` — ⛔ the close's progress update names the preferences file as where the list is read from

  Enforced by `tests/test_selected_modules_is_kept_in_one_file.py`.

  **Why it is not an existing invariant:** INV-076 says the Bootcamper chooses a path and
  which modules run. It does not say where the list is stored. INV-058 batches the
  administrative writes and asks for one consolidated preference write; it does not say which
  file holds which key, and the second copy was written under it. INV-133 says a preference
  saved in the preferences file is honored; it does not forbid a second copy elsewhere.
  INV-413 says module completion's Step 1 sets `current_module` to the next module in
  `selected_modules`; it does not say which file the list is read from. INV-029's dated note
  gives the journey map one row per `selected_modules` entry and names no file. So the
  progress copy could be written again, or a step could again read the list with no file
  named, and contradict no registered wording. The maintainer may prefer a dated note on
  INV-076 or INV-413; that is a different act and is not drafted here.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — The module selection, `selected_modules`, MUST be kept in one file, `config/bootcamp_preferences.yaml`. Bootcamp preparation writes it there in its consolidated preference write (INV-058), and the bootcamp MUST NOT write it to `config/bootcamp_progress.json`: Bootcamp preparation's write to the progress file sets `current_module` to the first content module and does not name the list. A step that sets `current_module` to the next module in `selected_modules` MUST name `config/bootcamp_preferences.yaml` as the file the list is read from. On 2026-11-17 four steps do so: module completion's Step 1 and the closes of Entity Resolution Concepts, System verification and Truth Set visualization. The dry-run scaffold MUST NOT write a `selected_modules` key to the progress file in any mode, and its mid-bootcamp preferences MUST carry the ordered list. A `selected_modules` key already in the progress file of a bootcamp begun before this rule is left in place and is never read. ⚠️ Limits: the enforcer reads `source/` and the scaffold, and takes the list and the preferences file to be tied when they are neighboring backticked names in one sentence. It **cannot** establish that a live guide reads the list from the preferences file. It does not check a mention of `selected_modules` that names no file and sets no `current_module`, and it does not say what happens when the selection is edited so that `current_module` is no longer in the list. Enforced by `tests/test_selected_modules_is_kept_in_one_file.py`. (Source: `selected-modules-is-kept-in-two-files-and-the-text-disagrees-on-which-is-read`, GitHub issue #44, 2026-11-17.)

- **Commit:** uncommitted

## install-pages-and-interface-lists-are-uneven-across-assistants

- **Implemented:** 2026-11-17 (issue #43)
- **Files changed:** `hosts/copilot/fragments/site-install.html`,
  `hosts/chatgpt/fragments/site-install.html`, `hosts/copilot/fragments/site-tips.html`,
  `hosts/chatgpt/fragments/site-tips.html`, `hosts/gemini/fragments/site-tips.html`,
  `hosts/kiro/fragments/site-tips.html`, `hosts/copilot/host.json`,
  `tests/test_install_pages_cover_what_the_package_names.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes what four install pages say about an assistant's interfaces and about updating
  and uninstalling the bootcamp's package, and one name in a sentence about hooks. None of
  that says anything about Senzing or about what the Senzing MCP server serves. No absence
  claim about the server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** Each assistant's install page now names every interface its package names, and
  every page has one tip about updating and uninstalling. These are findings 13, 25 and 27 of
  `production-readiness-audit-2026-11-17`.
  - **Interfaces without steps.** The GitHub Copilot package names VS Code and the ChatGPT
    package names the Codex CLI, and neither page mentioned it. Each page now has one
    paragraph below its steps, with the id `vs-code` or `codex-cli`. It says the assistant also
    runs there, that the bootcamp has not been run there, and that the page has no verified
    install steps for it. Neither says the bootcamp supports the interface. The GitHub Copilot
    page's first paragraph, which says "Choose one path", also says the page has no steps for
    VS Code and links to that paragraph.
  - **Update and uninstall tips.** All five `site-tips.html` fragments now have one tip with
    the id `update-uninstall`, headed "Update or uninstall".
    - Kiro and ChatGPT gain it. It says the page has no verified steps to update or uninstall,
      and where to look, by the name the page's install steps already use: Kiro's **Powers**
      panel, and the **Plugins** panel of the Codex desktop app.
    - Gemini's heading was "Update". Its two update commands and the sentence above them are
      unchanged. One sentence is added below them: those steps update the plugin, and the page
      has no verified steps to uninstall it.
    - Claude's tip is unchanged. Copilot's changes by the app's name only.
  - **The Copilot name.** "the Copilot app" is now "the GitHub Copilot app" in `hooks.note` of
    `hosts/copilot/host.json` and in the Copilot tip. The package's own naming table
    (`hosts/copilot/fragments/interface-naming.md`) requires that name.
  - **What a build changes.** Compared by building `6fe4627` and this change into two
    directories: the install pages for GitHub Copilot, ChatGPT, Gemini and Kiro differ, and so
    does one file in one package, `skills/bootcamp-onboarding/host-rules.md` in the GitHub
    Copilot package, by the one sentence. Nothing else differs. The Claude page, the Claude
    package and the other three packages are the same byte for byte, and no file under
    `hosts/claude/` is changed.
  - **No naming table is changed**, and no step is written from an assistant vendor's
    documentation.
  - **Tests.** `tests/test_install_pages_cover_what_the_package_names.py` is new, with 15
    tests. It takes the assistants from the build's own list (INV-246) and builds the install
    pages from the current files.
    - Five tests read each assistant's naming table and look for every name in its "Say"
      column, without the leading article, in the visible text of that assistant's built page.
      Text in the page's head, in a script and in a tag's attributes is not visible text. They
      fail when a table yields no name, and they hold the names the five tables give today.
    - Three tests hold the two paragraphs: each names its interface, says the bootcamp has not
      been run there, says the page has no verified install steps, and does not use the word
      "support".
    - Three tests read all five tips fragments: one tip with the id, the heading "Update or
      uninstall", and both "update" and "uninstall" in the tip's text below the heading. They
      also require the id exactly once on each built page.
    - Four tests hold the Copilot name: no file under `hosts/copilot/`, no file in the built
      GitHub Copilot package and not the built GitHub Copilot page has "Copilot app" without
      "GitHub " in front of it. They fail when no file names the app at all.
    - Negative controls run on every pass (INV-265): each name taken off its real page is
      reported missing; a name present only in the head, a script or an attribute is reported
      missing; a tip that is missing, has another heading or speaks of only one of the two is
      reported, on fixtures and on each real fragment; the two sentences this change corrects
      are reported, and the full name is not, also when it wraps over two lines.
    - Negative control run once, in a throwaway clone of `6fe4627` holding only the new test
      file: 9 of the 15 tests fail (`FAILED (failures=21)`).
    - Text is matched with whitespace collapsed (INV-346).
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. The pages now say what they do not cover; nothing here
    shows that a step they do give works. Gemini's update steps have no recorded run, as the
    issue records, and the page's generated preview note already says its steps follow the
    documentation. Verified on Linux only, with Python 3.12.3. The change is HTML, one JSON
    string and a test that uses `pathlib` and reads UTF-8, with no branch on the platform
    (INV-001).
  - **Found and not changed, as out of scope.** Two drafts for the maintainer, neither filed.
    1. **Not filed.** *The Claude install page says the bootcamp supports two interfaces no
       recorded run covers.* `hosts/claude/fragments/site-install.html` says of the Claude web
       app and the Claude IDE extensions: "The bootcamp supports those." Both records in
       `hosts/claude/checks.json` name Claude Code 2.1.325, started with `--plugin-dir`. The
       issue's goal is that a page claims nothing no recorded run backs, and its scope leaves
       Claude's page out. The question for the maintainer is whether that sentence should
       become the statement the other two pages now make.
    2. **Not filed.** *The update and uninstall commands on the Claude and GitHub Copilot
       pages have no recorded run.* No record in either assistant's `checks.json` mentions an
       update, an uninstall or the removal of a marketplace. The tips give the commands
       without a qualifier, while the Kiro and ChatGPT tips now say they have no verified
       steps. The question is whether those commands should be run and recorded, or the tips
       should say they follow the documentation.
- **Invariants.** The register is not edited here (INV-365). The change ships four hard-rule
  lines, all in the docstring of `tests/test_install_pages_cover_what_the_package_names.py`.
  `since` does not report them, because `tests/` is not a rule home. The three blocks below
  cover them (INV-309). They are three blocks because they have three subjects: which
  interfaces a page names, the update and uninstall tip, and one assistant's name for its
  desktop application. The lines this change adds under `hosts/` carry no ⛔ and no bold MUST
  or NEVER.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** An install page names every interface its package names, and says so where it has no steps for one. The rule already shipping, quoted:
    - ⛔ **An install page names every interface its assistant's package names.** — in `tests/test_install_pages_cover_what_the_package_names.py`
    - ⛔ **An install page that has no steps for an interface says the bootcamp has not been run there and that the page has no verified install steps for it.** — in `tests/test_install_pages_cover_what_the_package_names.py`

  Enforced by `tests/test_install_pages_cover_what_the_package_names.py`.

  **Why it is not an existing invariant:** INV-158 says which names the bootcamp uses for
  Claude's interfaces and that the install documents cover the two primary ones. It says
  nothing of another assistant, and nothing of an interface a package names and its page
  leaves out. INV-003 says the bootcamp is consistent, coherent and complete, and names no
  site. INV-428 and INV-429 say what an install page may say about a model and an effort.
  None of them says that a page and its package's naming table name the same interfaces, so
  a table could again gain an interface the page never mentions and contradict no registered
  wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Each assistant's built install page MUST name, in text a reader sees, every interface in the "Say" column of that assistant's naming table (`hosts/<assistant>/fragments/interface-naming.md`), by the name the table gives without its leading article. Where the page gives no install steps for an interface it names, it MUST say that the bootcamp has not been run in that interface and that the page has no verified install steps for it, and MUST NOT say the bootcamp supports it. An interface is added to a table and to its page in the same change; the page moves to the table, and an interface is not taken out of a table to make a page pass. On 2026-11-17 two interfaces have no steps: VS Code on the GitHub Copilot page and the Codex CLI on the ChatGPT page. ⚠️ Limits: the enforcer finds a name on the page and holds the statement for those two interfaces by name. It **cannot** tell steps from a disclaimer for any other interface, and it cannot establish that steps a page gives were ever followed: only a record in `hosts/<assistant>/checks.json` shows that. The Claude page's statement about the Claude web app and the Claude IDE extensions predates this rule and is not held to its second sentence. Enforced by `tests/test_install_pages_cover_what_the_package_names.py`, which builds every assistant's page and reads the tables as they are. (Source: `install-pages-and-interface-lists-are-uneven-across-assistants`, GitHub issue #43, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Every install page has one tip about updating and uninstalling, under one id. The rule already shipping, quoted:
    - ⛔ **Every install page has one tip with the id `update-uninstall`, headed "Update or uninstall", whose text speaks of both updating and uninstalling.** — in `tests/test_install_pages_cover_what_the_package_names.py`

  Enforced by `tests/test_install_pages_cover_what_the_package_names.py`.

  **Why it is not an existing invariant:** INV-158 requires install documents for Claude and
  says nothing of updating or uninstalling. INV-003 names no site. INV-428 and INV-429 govern
  the model and the effort on an install page. None of them says that a page tells a
  bootcamper how to update or remove what it told them to install, so a new assistant's page
  could again say nothing and contradict no registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Each assistant's tips fragment (`hosts/<assistant>/fragments/site-tips.html`) MUST hold exactly one tip with the id `update-uninstall`, headed "Update or uninstall", and the tip's text below the heading MUST speak of both updating and uninstalling. For each of the two the tip gives the steps, or says the page has no verified steps for it and names where in the assistant to look, by a name the page's install steps already use. A tip MUST NOT give steps written from an assistant vendor's documentation as though they had been followed. The id is the same on every page and MUST NOT change, because other text links to `#update-uninstall`. ⚠️ Limits: the enforcer finds the tip, its heading and the two words. It **cannot** establish that steps a tip gives work or were ever run; on 2026-11-17 no record in any `hosts/<assistant>/checks.json` covers an update or an uninstall. Enforced by `tests/test_install_pages_cover_what_the_package_names.py`, which reads all five fragments and requires the id exactly once on each built page. (Source: `install-pages-and-interface-lists-are-uneven-across-assistants`, GitHub issue #43, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Text for GitHub Copilot uses the name its own naming table gives the desktop application. The rule already shipping, quoted:
    - ⛔ **Text written for GitHub Copilot calls its desktop application "the GitHub Copilot app".** — in `tests/test_install_pages_cover_what_the_package_names.py`

  Enforced by `tests/test_install_pages_cover_what_the_package_names.py`.

  **Why it is not an existing invariant:** INV-158 fixes the names of Claude's four
  interfaces and retires one Claude name. It names no other assistant's interface. The
  naming table in `hosts/copilot/fragments/interface-naming.md` states the name and ships in
  the package, but no registered wording holds the package's own text to it, and two
  sentences under `hosts/copilot/` used the short name. The maintainer may prefer a dated
  note on INV-158 that extends it to each assistant's table; that is a different act and is
  not drafted here.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Text written for GitHub Copilot MUST call its desktop application "the GitHub Copilot app", the name its naming table (`hosts/copilot/fragments/interface-naming.md`) gives, and MUST NOT shorten it to "the Copilot app". This holds in every file under `hosts/copilot/`, in the built GitHub Copilot package and on its built install page. "The Copilot CLI" is the table's own name for the terminal interface and is not affected. ⚠️ Limits: the enforcer reports the words "Copilot app" with no "GitHub " in front of them, on text with whitespace collapsed. It does not check any other name in the table, and it reads no other assistant's text. Enforced by `tests/test_install_pages_cover_what_the_package_names.py`. (Source: `install-pages-and-interface-lists-are-uneven-across-assistants`, GitHub issue #43, 2026-11-17.)

- **Commit:** uncommitted

## hook-matchers-the-kiro-hooks-disclosure-and-a-catalog-category-each-take-one-source

- **Implemented:** 2026-11-17 (issue #34)
- **Files changed:** `tools/bootcamp_build/emit.py`,
  `hosts/kiro/files/skills/bootcamp-onboarding/scripts/install_hooks.py`,
  `hosts/kiro/files/skills/bootcamp-hooks-setup/SKILL.md`,
  `tests/test_bootcamp_build_emit.py`, `tests/test_bootcamp_build_hosts.py`,
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes which of an assistant's tool names a hook is limited to, what one skill tells the
  bootcamper about five hook files, and where a catalog entry takes its category. None of
  that says anything about Senzing or about what the Senzing MCP server serves. No absence
  claim about the server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** Three things in host configuration had two sources each, and the two disagreed.
  Each now has one. These are findings 17, 18 and 26 of
  `production-readiness-audit-2026-11-17`.
  - **Matchers.** On an assistant whose hooks go through the hook adapter and are limited to
    named tools, a matcher now holds every name `options.adapter.tool_categories` maps to a
    category the hook covers, in the map's order. Two places build one and both changed.
    `adapter_tool_names()` in `tools/bootcamp_build/emit.py` builds it for a package that
    carries a hook file (ChatGPT). `matcher()` in the Kiro installer builds it when the hooks
    are installed, from the copy of the map the build already writes into
    `bootcamp_host.json`. Neither reads `hooks.tools` any more.
  - **A patch tool.** A name the map calls `patch` joins the matcher of every hook that covers
    `write` or `edit`, because the adapter turns a patch into write and edit calls. A hook
    that covers only `shell` does not get it.
  - **The four matchers, read from a build of this change.** They are the ones the issue
    lists.

    - ChatGPT `PreToolUse`: `apply_patch|Write|Edit|Bash|shell`. It was `Write|Edit|Bash`.
    - ChatGPT `PostToolUse`: `Bash|shell`. It was `Bash`.
    - Kiro `PreToolUse`: `fs_write|write|str_replace|fs_append|execute_bash|shell`. It was
      `fs_write|str_replace|fs_append|execute_bash`.
    - Kiro `PostToolUse`: `execute_bash|shell`. It was `execute_bash`.

    The Kiro matchers are what the built installer prints for `plan` in a scratch workspace.
  - **What stays as it was.** `hooks.tools` stays in every profile and `host_tools` stays in
    `bootcamp_host.json`, as the issue decides. An assistant with no adapter (Claude) still
    builds its matcher from `hooks.tools`. An assistant whose profile sets `"matchers": false`
    (Copilot, Gemini) still has none. No name was removed from an adapter map.
  - **A value the profile cannot supply.** When a hook covers a category the adapter map gives
    no tool, the build stops with a `BuildError` that names the assistant and
    `options.adapter.tool_categories`. The Kiro package carries no hook file, so its matchers
    are first built at install time, when nothing can stop a build. `_emit_host_file()`
    therefore makes the same check while it writes `bootcamp_host.json`. A `codex` catalog
    whose profile has no category stops the build the same way, naming
    `options.manifest.interface.category`. Neither case exists today.
  - **The Kiro disclosure.** "What to tell the bootcamper" in
    `hosts/kiro/files/skills/bootcamp-hooks-setup/SKILL.md` had two summary bullets that
    covered three of the five hooks. It now has one bullet for each hook file the installer
    writes. Each begins with the file name as the installer prints it, then says when the
    hook runs and what it does. "Say this much, and no more", the bullet on what is written
    into `.kiro/hooks/` and the bullet that every hook does nothing outside a bootcamp project
    are unchanged.
  - **What each bullet was written from.** The scripts each hook runs, as the built
    `bootcamp_host.json` lists them, and each script's own code. The session-start bullet
    names both files that hook writes and its container report. The prompt-submit bullet
    covers all four of its scripts. The post-tool-use bullet names the file it writes,
    `config/steer_observations.json`. The stop bullet says the hook changes nothing on Kiro.
    That was run, not only read: in a scratch bootcamp project, the built `stop-nudge.py`
    printed its block for a turn that ended without a question, and the built adapter, given
    the same payload for `stop`, printed nothing and exited 0.
  - **The category.** `write_catalogs()` takes the `codex` catalog's category from
    `options.manifest.interface.category`, the key the manifest already takes it from. No
    category literal is left in `emit.py`. The built `.agents/plugins/marketplace.json` now
    says "Developer Tools", as the built `.codex-plugin/plugin.json` does. It said
    "Productivity".
  - **Three assistants' packages are unchanged.** A build of `d987dc9` and a build of this
    change were compared with `diff -r`. The Claude, Copilot and Gemini packages are
    identical, and so are the two other catalogs, the site and the public pages. Four files
    differ: the ChatGPT hook file, the ChatGPT catalog, and in the Kiro package the
    disclosure and the installer.
  - **Tests.** `tests/test_bootcamp_build_hosts.py` goes from 14 tests to 18, and
    `tests/test_bootcamp_build_emit.py` from 24 to 32.
    - Four tests read the real profiles and the five built packages. One takes each matcher
      from the built ChatGPT hook file and from the files the built Kiro installer writes into
      a scratch workspace, and requires exactly the names the assistant's adapter map gives
      the hook's categories. It takes the assistants from the profiles (INV-246), and fails
      when it read none of them or when a package has neither a hook file nor an installer
      (INV-265). One runs the installer and requires one bullet in the disclosure for each
      file it wrote, each file name as the installer printed it, and no bullet for a file it
      did not write. One compares the built catalog's category and the built manifest's with
      the profile key.
    - Negative controls run on every pass. The matcher check reports a matcher with any one
      mapped name taken out, a name the map does not give, and a name given twice. The
      disclosure check reports a bullet taken away, a hook file added, and a bullet for a file
      that is not written.
    - Eight tests build a miniature repository. An adapter map whose names differ from
      `hooks.tools` shows which of the two a matcher was built from. A patch tool is matched
      for a write or an edit and not for a shell command alone. An assistant with no adapter
      keeps its `hooks.tools` names, and one with no matchers keeps none. A category the map
      cannot name stops the build, for a package with a hook file and for one without. A
      catalog takes whatever category the profile gives, and a profile with none stops the
      build.
    - Negative control run once, on an export of `d987dc9` holding only the two changed test
      files: 9 of the 12 new tests fail (`FAILED (failures=15)`). The three that pass hold
      before and after the change: the matcher check's own control, an assistant with no
      adapter keeps its `hooks.tools` names, and an assistant with no matchers keeps none.
    - The disclosure check matches the file name that opens a bullet. It does not read whether
      a bullet's description is complete or true. That stays a reviewer's call.
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. The change makes each profile agree with itself. It does
    not show that `apply_patch`, `shell`, `write` or any other name in an adapter map is a
    tool name the assistant really sends, and those names stay recorded as not checked.
    Whether Codex accepts "Developer Tools" as a catalog category was not checked either; the
    manifest already ships that value. Verified on Linux only, with Python 3.12.3. The new
    code is standard library only and has no branch on the platform (INV-001).
  - **Compatibility.** A Kiro workspace with hooks already installed keeps the old matchers
    until `install` runs again, which overwrites the files. On ChatGPT the write gate and the
    failed-run check now also run for `apply_patch` and `shell`.
  - **Found and not changed, as out of scope. Each is drafted here and not filed.**
    1. **Not filed.** *The Kiro installer writes a stop hook whose result the adapter always
       discards.* On Kiro the adapter's result dialect is `text`, in which a stop cannot be
       held and no context is written for a stop. `stop-nudge.py` only ever asks for a hold.
       So `senzing-bootcamp-stop.json` runs two Python processes at the end of every turn and
       can change nothing, as the run above shows. The profile already lists `stop` as
       advisory. The question for the maintainer is whether the installer should write that
       file at all. The disclosure now says what it does.
    2. **Not filed.** *A failing check in `tests/test_bootcamp_build_hosts.py` is reported
       with generator errors beside it.* The file's `each()` helper yields inside
       `self.subTest`. When an assertion in the loop body fails, the generator is closed at
       that `yield` and the runner also prints `RuntimeError: generator ignored GeneratorExit`
       and `AttributeError` lines. Seen while running the new tests on `d987dc9`. The four new
       tests open `subTest` in the test body and report only their own failure; the eleven
       older loops still use the helper.
- **Invariants.** The register is not edited here (INV-365). The change ships two hard-rule
  lines, both in the docstring of `tests/test_bootcamp_build_hosts.py`. `since` does not
  report them, because `tests/` is not a rule home. The two blocks below cover them (INV-309).
  They are two blocks because they have two subjects: which tools a hook runs for, and what a
  bootcamper is told before agreeing to an install. No rule is drafted for the catalog
  category: it is one value read from one profile key, held by a test. The lines this change
  adds under `hosts/` and `tools/bootcamp_build/` carry no ⛔ and no bold MUST or NEVER.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** A hook's matcher is derived from the adapter's own map of the assistant's tools. The rule already shipping, quoted:
    - ⛔ **On an assistant whose hooks go through the hook adapter, a hook's matcher names exactly the tools the adapter's map gives the categories the hook covers.** — in `tests/test_bootcamp_build_hosts.py`

  Enforced by `tests/test_bootcamp_build_hosts.py`.

  **Why it is not an existing invariant:** INV-003 says the bootcamp is consistent, coherent
  and complete, and names no site. INV-200 and INV-109 say what the write gate blocks, and
  not for which of an assistant's tools the gate is run. INV-052 says how a hook is invoked.
  INV-300 is about a rule that shipped guidance says is owned by one place. None of them says
  that a matcher and the adapter's map name the same tools, so a matcher could again leave out
  a tool the adapter would gate and contradict no registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — On an assistant whose hooks go through the hook adapter (`options.adapter` in `hosts/<assistant>/host.json`) and are limited to named tools (`hooks.matchers` is not `false`), each hook's matcher MUST name exactly the tools `options.adapter.tool_categories` maps to a category the hook covers, and no other name. A tool the map calls `patch` MUST be in the matcher of every hook that covers `write` or `edit`, because the adapter turns a patch into write and edit calls. Both places that build a matcher MUST derive it from that map and not from `hooks.tools`: the build, for a package that carries a hook file, and the package's hook installer, for a package that carries an installer instead, reading the copy of the map the build writes into `bootcamp_host.json`. When a hook covers a category for which the map gives no tool, the build MUST fail with an error that names the assistant and the key, for both kinds of package. An assistant with no adapter builds its matcher from `hooks.tools`, and an assistant whose profile sets `"matchers": false` has none; this rule changes neither. ⚠️ Limits: the rule makes a profile agree with itself. It does not establish that a name in the map is a tool name the assistant really sends; on 2026-11-17 no recorded run had checked that for any assistant. Enforced by `tests/test_bootcamp_build_hosts.py`, which reads the real profiles, the built hook file and the files the built installer writes, and by `tests/test_bootcamp_build_emit.py` on a miniature repository. (Source: `hook-matchers-the-kiro-hooks-disclosure-and-a-catalog-category-each-take-one-source`, GitHub issue #34, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** A package that installs its hooks tells the bootcamper about every hook file before asking. The rule already shipping, quoted:
    - ⛔ **A package that installs its hooks tells the bootcamper about every hook file it writes, in one bullet for each.** — in `tests/test_bootcamp_build_hosts.py`

  Enforced by `tests/test_bootcamp_build_hosts.py`.

  **Why it is not an existing invariant:** INV-211 says a consent disclosure is placed before
  its 👉 question, and not what the disclosure has to cover. INV-200 says where the bootcamp
  writes files, and not what a bootcamper is told before hook files are written into their
  project. INV-003 names no site. None of them says that the disclosure covers every hook the
  install adds, so it could again describe three of five and contradict no registered wording.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Where an assistant's package installs the bootcamp's hooks into the bootcamper's project (on 2026-11-17 only the Kiro package, through `install_hooks.py`), the skill that asks for consent MUST tell the bootcamper about every hook file the installer writes, before it asks. Its "What to tell the bootcamper" list MUST hold exactly one bullet for each hook file the installer writes and no bullet for a file it does not write. Each bullet MUST begin with the hook file's name as the installer prints it, and then say in plain words when the hook runs and everything it does, including the files it writes and a hook whose result the assistant cannot act on. A change that adds, removes or renames a hook file, or changes what a hook's scripts do, MUST change the list in the same change. ⚠️ Limits: the enforcer matches the file name that opens each bullet; whether a bullet's description is complete and true is a reviewer's call. Enforced by `tests/test_bootcamp_build_hosts.py`, which runs the built installer in a scratch workspace and compares the files it writes with the bullets. (Source: `hook-matchers-the-kiro-hooks-disclosure-and-a-catalog-category-each-take-one-source`, GitHub issue #34, 2026-11-17.)

- **Commit:** uncommitted

## inv-427-is-written-for-every-file-the-guide-reads-and-ships-at-one-site

- **Implemented:** 2026-11-17 (issue #39)
- **Files changed:** `tools/bootcamp_build/emit.py`, `tools/bootcamp_build/validate.py`,
  `tests/test_ground_rules_are_read_to_the_end.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it adds one instruction about reading a file to its end to the built copy of each long
  Markdown file, and a number of characters that decides which files are long. Neither says
  anything about Senzing or about what the Senzing MCP server serves. No absence claim about
  the server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** The build now puts one read-to-the-end instruction at the top of every Markdown
  file over 30,000 characters, in every assistant's package. This is finding 5 of
  `production-readiness-audit-2026-11-17`. Until now the instruction shipped at one site, the
  onboarding step that names the ground rules.
  - **The instruction.** `READ_TO_THE_END_NOTE` in `tools/bootcamp_build/emit.py` is the one
    text. It says to read the file to its last line, that a read that reports it was cut short
    or truncated has not read it, to continue from where it stopped in as many reads as it
    takes, and to do so before acting on anything the file says. It cites INV-427 on its ⛔
    line and names no assistant. It is the same three lines in every package and every file.
  - **The cut.** `READ_CUT_CHARACTERS = 30_000`, in the same file, is the one definition. The
    build reads it and the test imports it. A file of 30,000 characters or fewer gets no
    instruction.
  - **What is measured.** `_add_read_to_the_end_notes()` runs last in `build_host()`, after the
    step that appends a skill's location and the step that writes `host-rules.md`. So the size
    is the file's size in characters as the package ships it, before the instruction is added,
    and each package is judged on its own files.
  - **Where it goes.** After the frontmatter where the file has one, otherwise first in the
    file. The instruction and one blank line go in front of the first line that is not blank,
    and nothing else in the file changes. A `SKILL.md` over the cut still starts with its
    frontmatter, and `tools.bootcamp_build check` still reports 0 skill frontmatter problems.
  - **The docs directory.** The build leaves every file under the package's docs directory
    alone. It reads the directory from the assistant's own layout: `docs/` in four packages
    and `skills/bootcamp-onboarding/docs/` in the Kiro package. The example recap there is
    52,069 characters and carries no instruction.
  - **Counted on 2026-11-17, at `834a961` plus this change.** Each of the five packages holds
    19 Markdown files over the cut. 18 carry the instruction: the ground rules, 13 phase and
    reference files, and four `SKILL.md` files (`bootcamp-preparation`, `graduation`,
    `module-02-sdk-setup`, `module-04-data-collection`). The 19th is the example recap. That is
    90 files in all.
  - **The issue's sizes are from an older commit.** It gives
    `skills/bootcamp-preparation/SKILL.md` as 30,708 characters in the Claude package and
    31,746 in the Kiro package, and `module-06-data-processing/phaseC-multi-source.md` as
    29,621. They are 30,659, 31,697 and 29,444 today. Each is on the same side of the cut as
    the issue says, so `phaseC-multi-source.md` gets no instruction.
  - **`source/` is unchanged.** No file under `source/` or `hosts/` carries the instruction, and
    a test holds that. The onboarding step keeps its own sentence and "before the first
    reply". The eleven "Follow … throughout" lines are not reworded.
  - **One regular expression moved.** `FRONTMATTER_RE` moves from `validate.py` to `emit.py`,
    and `validate.py` imports it. `validate.py` already imports from `emit.py`, so defining it
    in `emit.py` keeps one copy and no import cycle.
  - **Tests.** `tests/test_ground_rules_are_read_to_the_end.py` goes from 3 tests to 30. Its
    three existing tests are unchanged and pass.
    - Nine tests read all five built packages, taking the assistants from the build's own list
      (INV-246). They find every Markdown file over the cut outside the docs directory and
      require the instruction as its first body text. They fail when a package yields no file
      over the cut, and they require the ground rules and at least one `SKILL.md` among the
      files found (INV-265). They also hold that the text is the same in every file, that each
      file carries it once, that a file at or under the cut carries none, and that no file in
      the docs directory carries it.
    - Four tests read the instruction itself: it says every part, it fails with any part
      removed, it names no assistant by id, name, product or any profile's foreign term, and
      no file under `source/` or `hosts/` carries it.
    - Six tests build a miniature repository: one character over the cut gets the instruction
      and the cut itself does not; a file with frontmatter gets it after the frontmatter; one
      source file is over the cut in one package and exactly at it in the other; a file that
      grows gets it and one that shrinks loses it; the docs directory is left alone under
      either layout; a long script is left alone.
    - Eight negative controls run on every pass. The check reports a long file without the
      instruction, a real ground-rules file with the instruction taken out (in each package),
      a skill with frontmatter and no instruction, an instruction placed below the heading,
      and an instruction with a part missing. It reports nothing for a file at the cut or in
      the docs directory, and a second check reports an instruction on a file under the cut.
    - Negative control run once, in a throwaway clone of `834a961` holding this change with
      the one call to `_add_read_to_the_end_notes()` removed: 10 of the 30 tests fail
      (`FAILED (failures=197)`).
    - The instruction is compared with the build's text, line wraps included, because the
      build writes it. What it says is checked with whitespace collapsed (INV-346).
  - **Not observed.** No run on a real assistant was made, so no record is added to any
    `hosts/<assistant>/checks.json`. The test shows that each package carries the instruction.
    It does not show that an assistant reads on when told to. Verified on Linux only, with
    Python 3.12.3. The new build code is standard library only, measures decoded text and has
    no branch on the platform (INV-001). A checkout that converts line endings to CRLF would
    count each carriage return; the build already needs LF there, because it requires a
    command to start with `---` and a line feed.
  - **Found and not changed, as out of scope.** Two cases the issue does not decide, neither of
    which occurs today. The build would add the instruction to a Markdown file over the cut
    under a `vendor/` directory, which it otherwise copies byte for byte; no package holds
    one. And a command over the cut, built as a skill, would gain two lines that
    `test_a_command_turned_into_a_skill_keeps_its_instructions` in
    `tests/test_bootcamp_build_hosts.py` does not expect; the largest command is 2,352 bytes.
- **Invariants.** Establishes no new invariant (INV-309), and proposes a change to one in
  force. The register is not edited here (INV-365). The change adds one hard-rule line, the
  instruction's ⛔ line in `tools/bootcamp_build/emit.py`, and it cites INV-427 on that line:
  `conformance.py since --since-last-audit` reports it outside the corpus, cited. INV-427 as
  registered says "before its first reply" and its enforcer checked one step, so the block
  below drafts the dated note the issue asks for. Until the maintainer applies it, the
  register's wording is narrower than what the packages carry.

- **PROPOSED AMENDMENT to INV-427 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **(INV-427) Read this file to its last line.** — in `tools/bootcamp_build/emit.py`

  INV-427's first clause covers every file the bootcamp tells the guide to read before acting.
  Its last clause says "before its first reply", and its enforcer checked only the onboarding
  step that names the ground rules. So the rule can be read as binding the first turn alone,
  while each package holds 17 more files of instructions over the size at which the observed
  read was cut. Since #39 the build states the rule at the top of each of them, and
  `tests/test_ground_rules_are_read_to_the_end.py`, the enforcer the invariant names, checks
  every built package. Without the note below the register says less than its enforcer holds:
  a later change could take the instruction off a phase file, or raise the cut, and
  contradict no registered wording.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-427** — (⚠️ **Dated note, 2026-11-17 (#39): the rule covers every long file of instructions in every assistant's package, and the build states it at the top of each; the rule above is unchanged.** The rule is not about the ground rules alone, nor about the first turn alone. Every Markdown file of instructions over the cut, in every assistant's package, MUST carry the read-to-the-end instruction as its first body text: after the frontmatter where the file has one, otherwise first in the file. The cut is 30,000 characters, the size at which the read observed above was cut. It is measured on the file as built for that package, before the instruction is added, and a file of 30,000 characters or fewer carries none. The build adds the instruction: `READ_TO_THE_END_NOTE` in `tools/bootcamp_build/emit.py` is its one text and `READ_CUT_CHARACTERS` there is the one definition of the cut. No file under `source/` carries it by hand, so a file that grows past the cut gets it at the next build. The instruction MUST be the same text in every package and every file, MUST name no assistant, and MUST say all of: read the file to its last line; a read that reports it was cut short or truncated has not read the file; continue from where it stopped, in as many reads as it takes; do so before acting on anything the file says. Where the rule above says "before its first reply", read, for a file the guide reads after the first turn: before acting on anything the file says. The onboarding step that names the ground rules keeps "before the first reply", which is right for the first turn. A file under the package's docs directory is not a file of instructions and carries none: the example recap there is a model of the bootcamper's own recap and ships as a pair with a PDF. Observed (`production-readiness-audit-2026-11-17`, finding 5): the instruction shipped at one site while each package held 17 other files of instructions over the cut, four of them `SKILL.md` files that are loaded with no hand-over sentence. Enforced by `tests/test_ground_rules_are_read_to_the_end.py`, which reads the cut from the build and reads every built package; it **cannot** establish that a live turn obeys the instruction, and no run on a real assistant was made for #39.)

- **Commit:** uncommitted

## shared-text-names-one-assistants-files-ids-and-mechanisms-in-other-packages

- **Implemented:** 2026-11-17 (issue #30)
- **Files changed:** `hosts/claude/host.json`, `hosts/copilot/host.json`,
  `hosts/kiro/host.json`, `hosts/chatgpt/host.json`, `hosts/gemini/host.json`,
  `source/skills/bootcamp-onboarding/onboarding-flow.md`,
  `source/skills/bootcamp-onboarding/feedback.md`, `source/skills/graduation/SKILL.md`,
  `source/skills/module-03b-truthset-visualization/visualization-api-reference.md`,
  `source/scripts/failed_run.py`, `source/scripts/feedback-capture.py`,
  `source/scripts/package_bootcamp.py`, `tools/bootcamp_build/validate.py`,
  `tools/bootcamp_build/emit.py`, `README.md`,
  `tests/test_shared_text_holds_in_every_package.py` (new),
  `tests/test_bootcamp_build_emit.py`, `tests/test_scripts_report_the_built_version.py`,
  `tests/test_viz_server_process_handle.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes which of the package's own files a message names, the wording of four passages
  about the package and the guide, one host value, and the letter case the build's check
  matches. The MCP failure message keeps the address `https://mcp.senzing.com/mcp` as it was,
  and a test now compares it with the address the package's own MCP file registers, which is
  a fact about the package and not about what the server serves. No absence claim about the
  Senzing MCP server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** Six passages that were true in one assistant's package and shipped in all five
  now hold in each, and `tools.bootcamp_build check` reports another assistant's name in any
  letter case. These are findings 7, 8, 12, 16, 19 and 24 of
  `production-readiness-audit-2026-11-17`. #26, #27, #28, #29 and #31 merged first and touched
  nearby text. Each of the six was read at `2442646` before it was changed, and **none was
  already corrected**: all six still read as the issue quotes them.
  - **1. The MCP file.** The MCP failure message in `onboarding-flow.md` said the server
    "ships with this plugin's .mcp.json" in every package. The Copilot and Kiro packages ship
    `mcp.json` and the Gemini package `mcp_config.json`. Every `hosts/*/host.json` now carries
    `mcp_file`, and the message takes the name from it. The build still writes each file under
    the name its emitter holds; a test reads each built package and holds the two together.
  - **2 and 4. The package noun.** The same line takes its noun from the existing
    `package_noun` value: "this Power's" in the Kiro package, "this plugin's" in the other
    four. The build adds one sentence to `host-rules.md` for an assistant whose noun is not
    "plugin", which today is Kiro alone: `In the bootcamp's files, "plugin" means this Power.`
    It is written by `host_rules()` in `tools/bootcamp_build/emit.py` from the noun, so it
    follows the profile and no host is named in the code. A sweep found the message was the
    only text shown word for word that said "plugin": on 2026-11-17 the Kiro package holds 44
    `text` display blocks and 132 pinned 👉 questions, and none says it now.
  - **3. The skill's directory.** `onboarding-flow.md` said "The harness supplies that
    directory at invocation". It now says "That directory is the one this skill's files are
    read from", which holds whoever supplies it. The rest is kept: the skill's own directory,
    two levels up, the plugin whose files are running, and INV-185's fallback.
  - **4. The model example.** The `Model / effort` line of the feedback entry gave
    `"claude-opus-5-5[1m] / high"`. It now gives `"<model ID> / high"`, the same in all five
    packages.
  - **5. The graduation layout.** `graduation/SKILL.md` said the generator is "two levels up
    under `scripts/`". It now says the generator is in `{{host.scripts_relative}}/`, counted
    from `skills/graduation/`: `../../scripts/` in four packages and
    `../bootcamp-onboarding/scripts/` in the Kiro package. The stamps beside it (#27) are not
    touched.
  - **6. The handle that is not a pid.** The warning in `visualization-api-reference.md` named
    "the host's own background-task mechanism" and "the guide's own background-task feature".
    It now reads "A handle that names a task rather than a process is not a pid", for a server
    "started by something other than the shell forms in the table above". It still says to
    record no pid from it and to take the pid from the launch confirmation's port lookup.
    INV-223's 2026-11-10 note states the old sentence, so the first block below proposes a
    dated note.
  - **The check.** `_term_pattern` in `tools/bootcamp_build/validate.py` compiles with
    `re.IGNORECASE`, which both `lint_source` and `residue` use. `README.md` says so in one
    sentence. `tools/bootcamp_build/neutrality.json` is unchanged: source 0, each non-Claude
    package 1, and that one is still `CLAUDE_PROJECT_DIR` in the hook adapter. Measured at
    `2442646` with the match made case-insensitive and nothing else changed: 4 lines in
    `source/` and 5 in each non-Claude package, the ones the issue lists.
  - **Differs from the issue's expectation: #31 did not remove the manifest directory.** The
    issue says that if #31 merges first and the two script lines no longer spell Claude's
    manifest directory, only the comment in `failed_run.py` is left. #31 merged first and kept
    both lookups as they were, by its own decision, so all three lines are fixed here. The
    comment in `failed_run.py` names the transcript lint without its path. In
    `feedback-capture.py` and `package_bootcamp.py` the manifest path is now
    `{{host.manifest_path}}`, which the build fills in from the profile, so no package spells
    another assistant's directory. Each of the two lines carries a comment that cites
    `onboarding-flow.md`: INV-252's guard sweeps the Claude package for the manifest's path,
    which is now written whole there, and wants the rule cited where the path is written.
  - **What that changes in the two scripts.** Only the lookup that runs when
    `bootcamp_host.json` gives no version. In the Claude package nothing changes: the hook
    reads `../.claude-plugin/plugin.json`, and the packager `../plugin.json` and then that
    path. In the other packages the Claude path is replaced by the package's own: the hook
    reads `../plugin.json` in the Copilot, Gemini and Kiro packages and
    `../.codex-plugin/plugin.json` in the ChatGPT package, and the packager reads
    `../plugin.json` and then the same path. In the Kiro package that lookup still finds
    nothing, as before, because its scripts sit two directories deeper than its manifest.
    This supersedes the "Unchanged, as the issue decides" bullet of #31's entry for the
    non-Claude packages. The copy of each script in `source/` holds the unfilled token and
    reports its unresolved value when run from there, which it already did: `source/` has no
    manifest beside it.
  - **Tests.** `tests/test_shared_text_holds_in_every_package.py` is new and holds 41 tests.
    It builds every assistant's package, taking the assistants from the build's own list
    (INV-246), and reads what each ships: the message against the one file at the package's
    root that registers an MCP server, found by reading the files; the noun; the `host-rules.md`
    sentence in the Kiro package and in no other; the skill-directory passage, identical in
    all five, and the manifest two levels up from a skill; the model example; the graduation
    path against the directory that holds `generate_recap_pdf.py`; the warning; and the real
    tree against the recorded ceilings. `tests/test_bootcamp_build_emit.py` gains 8 tests that
    plant a lowercase name in a miniature repository, in a package and in the source, and run
    `check` itself on it. `tests/test_scripts_report_the_built_version.py` goes from 24 to 30
    tests: its fallback cases now run copies from every built package and not from `source/`,
    it compares each built `plugin_version()` with the source's with only the manifest path
    filled in, and it checks that no copy reads a manifest at another assistant's path.
    `tests/test_viz_server_process_handle.py` pins the new wording, and its mutation test
    still fails when "is not a pid" is inverted. Text is read with whitespace collapsed
    (INV-346).
    Negative controls, run in a throwaway clone at `2442646` with only the four test files
    copied in: 17 of the 41 new tests fail (`FAILED (failures=52, errors=5)`), 6 of the 8 new
    build tests fail (`FAILED (failures=12)`), 5 of the 30 fail in the built-version module
    (`FAILED (failures=90)`), and the pinned warning fails (`FAILED (failures=1)`).
  - **Not observed.** No real assistant showed the failure message, read `host-rules.md` or
    acted on the warning, so no record is added to any `hosts/<assistant>/checks.json`.
    Whether GitHub Copilot, Kiro, ChatGPT or Gemini has a background-task feature was not
    looked into, as the issue decides. Verified on Linux only, with Python 3.12.3. The two
    scripts join the manifest path with `os.path.join` and `pathlib`, with no branch on the
    platform; on Windows the joined path mixes separators, which Windows accepts, and no run
    there happened (INV-001).
  - **Found and not fixed, as out of scope.** The docstrings of both `plugin_version()`
    functions say the manifest is "above this file's directory", which is not where the Kiro
    package keeps it. `graduation/SKILL.md` still says the generator "ships with this plugin"
    in guide-facing prose, which the issue leaves as it is. In
    `tests/test_plugin_manifest_reads_resolve_inside_the_plugin.py`, three failure messages
    call `path.relative_to(REPO_ROOT)` on a path inside the built package, so a real finding
    there surfaces as a `ValueError` and not as the message. It was met while the two script
    lines had no comment, and is left alone.
- **Invariants.** The register is not edited here (INV-365). The change adds no hard-rule line
  under `source/`, `hosts/` or `tools/bootcamp_build/`, and `since` reports none. It rewords
  one sentence that INV-223's 2026-11-10 note states, and the first block below proposes the
  dated note. It ships two rules the register does not hold, each stated in one line of a
  test's docstring, which the second and third blocks cover (INV-309). No registered
  invariant quotes the skill-directory passage, the model example, the graduation passage or
  the MCP failure message: INV-252 and INV-185 give the resolution order and do not say who
  supplies a skill's directory.

- **PROPOSED AMENDMENT to INV-223 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **A handle that names a task rather than a process is not a pid.** — in `source/skills/module-03b-truthset-visualization/visualization-api-reference.md`

  INV-223's 2026-11-10 note says "A handle from the host's own background-task mechanism is
  not a pid." A background-task mechanism is a feature of one assistant, and the contract that
  carries the sentence ships to five. Since #30 the contract names no feature, and
  `tests/test_viz_server_process_handle.py`, the enforcer the note names, pins the new
  wording. Without the note below the register still states the old sentence, so the registry
  and its enforcer disagree, and the next editor writes one assistant's feature back into
  shared text.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-223** — (⚠️ **Dated note, 2026-11-17 (#30): the handle warning names no assistant's feature; the rule above and the rest of the 2026-11-10 note are unchanged.** Where the 2026-11-10 note says "A handle from the host's own background-task mechanism is not a pid", read: a handle that names a task rather than a process is not a pid. When the server is started by something other than the shell forms the contract's handle table gives, the id it returns names a task, not a process: the guide MUST record no pid from it and MUST take the pid from the launch confirmation's port lookup, and where that lookup names no single listener the checkpoint keeps no pid and teardown's missing-pid fallback applies. The warning MUST be the same text in every assistant's package and MUST name no assistant and no assistant's feature, because a background-task mechanism is a feature of one assistant and the contract ships to all of them. Enforced by `tests/test_viz_server_process_handle.py`, and in every built package by `tests/test_shared_text_holds_in_every_package.py`. Whether any assistant other than Claude has such a feature was not looked into when this note was drafted.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** The build's check for another assistant's name ignores letter case. The rule already shipping, quoted:
    - ⛔ **The build's check for another assistant's name matches it in any letter case, in `source/` and in every built package.** — in `tests/test_bootcamp_build_emit.py`

  Enforced by `tests/test_bootcamp_build_emit.py`.

  **Why it is not an existing invariant:** No registered invariant states the check at all.
  INV-430 says which source files may ship to some assistants and not others. INV-431 says
  which directories the maintainer tools read for rule text. INV-158 and INV-114 are about
  what the bootcamp tells the Bootcamper to do in an interface and which models it names.
  None of them says that shared text names no assistant, or in which letter case a name
  counts. The model ID in the feedback entry sat in all five packages because the match was
  case-sensitive.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — `python3 -m tools.bootcamp_build check` MUST report every term an assistant's profile lists in `foreign_terms` whatever its letter case, both in `source/` outside a host block for the assistants that term belongs to and in each built package. A model ID, a directory name, an environment variable and a comment are text like any other: a script gets no exemption, and the fix for a reported line is to remove the name or take it from a host value, never to split the string. The ceilings in `tools/bootcamp_build/neutrality.json` MUST only come down; when this rule was drafted they were 0 for `source/` and for the Claude package and 1 for each other package, the one being `CLAUDE_PROJECT_DIR` in the hook adapter. Observed (`production-readiness-audit-2026-11-17`, finding 12): the feedback entry's `Model / effort` example gave a Claude model ID in all five packages, and two bundled scripts and one comment spelled the Claude package's directories, and the check passed because it matched the capitalized name only. Enforced by `tests/test_bootcamp_build_emit.py`, which plants a lowercase name in a miniature repository and runs the check on it, and by `tests/test_shared_text_holds_in_every_package.py`, which holds the real tree to the recorded ceilings; neither can find a name put together at run time. (Source: `shared-text-names-one-assistants-files-ids-and-mechanisms-in-other-packages`, GitHub issue #30, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Text shown to the bootcamper word for word names the package by the assistant's own noun. The rule already shipping, quoted:
    - ⛔ **Text a package shows the bootcamper word for word names the package by its assistant's own noun.** — in `tests/test_shared_text_holds_in_every_package.py`

  Enforced by `tests/test_shared_text_holds_in_every_package.py`.

  **Why it is not an existing invariant:** INV-158 is about directing the Bootcamper to act in
  their interface. INV-252 and INV-185 are about where a bundled file is read from. INV-247 is
  about which questions the guide may ask. None of them says what a package calls itself to
  the bootcamper. `package_noun` was read by the certificate alone, so the Kiro package told
  its bootcamper about "this plugin's" file while Kiro calls the package a Power.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — Text a skill file tells the guide to show the Bootcamper word for word, a fenced `text` display block or a pinned 👉 question, MUST name the package by the assistant's own noun, taken from `package_noun` in `hosts/<assistant>/host.json`: "Power" in the Kiro package and "plugin" in the others when this rule was drafted. Where an assistant's noun is not "plugin", its `host-rules.md`, which the guide reads at the start of every session, MUST say once that "plugin" in the bootcamp's files means that noun, and no other package carries the sentence. This binds displayed text only: guide-facing prose, the identifiers `PLUGIN_ROOT` and `plugin.json`, the `plugin` routing value in a feedback entry and the `**Plugin version:**` label keep the word. Observed (`production-readiness-audit-2026-11-17`, finding 16): the MCP failure message said "this plugin's" in the Kiro package. Enforced by `tests/test_shared_text_holds_in_every_package.py`, which reads every `text` display block and every pinned 👉 question of each built package whose noun is not "plugin"; it **cannot** establish what a guide on a real assistant shows, and it does not read text a script prints. (Source: `shared-text-names-one-assistants-files-ids-and-mechanisms-in-other-packages`, GitHub issue #30, 2026-11-17.)

- **Commit:** uncommitted

## slash-commands-are-named-to-bootcampers-on-four-assistants-that-ship-no-command

- **Implemented:** 2026-11-17 (issue #28)
- **Files changed:** `hosts/claude/host.json`, `hosts/copilot/host.json`,
  `hosts/kiro/host.json`, `hosts/chatgpt/host.json`, `hosts/gemini/host.json`,
  `source/commands/graduate.md`, `source/commands/start-bootcamp.md`,
  `source/scripts/session-start.py`, `source/scripts/feedback-capture.py`,
  `source/scripts/package_bootcamp.py`, `source/skills/bootcamp-onboarding/SKILL.md`,
  `source/skills/bootcamp-onboarding/feedback.md`,
  `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/bootcamp-onboarding/notes.md`,
  `source/skills/bootcamp-onboarding/packaging.md`, `source/skills/graduation/SKILL.md`,
  `source/skills/module-07-query-visualize-discover/phase2-discover.md`,
  `source/skills/module-07-query-visualize-discover/phase2b-discover.md`,
  `tests/_invocations.py` (new),
  `tests/test_each_package_names_an_operation_in_its_own_form.py` (new),
  `tests/test_graduation_ending_surfaces.py`,
  `tests/test_a_finished_bootcamp_is_never_resumed.py`,
  `tests/test_generated_data_supports_its_success_criteria.py`,
  `tests/test_coherence_sweep_523.py`, `tests/test_resume_requires_a_recorded_module.py`,
  `tests/test_bootcamp_build_hosts.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes how the bootcamp's own text names the bootcamp's own five operations, replaces
  one value in each assistant's profile with six, and adds tests that read that text and
  those profiles. It asserts nothing about Senzing. No absence claim about the Senzing MCP
  server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** Each package now names a bootcamp operation in the form its own assistant is
  given. This is finding 3 of `production-readiness-audit-2026-11-17`, confirmed by execution
  in `dry-run-2026-11-17`. Before the change the shared text named `/start-bootcamp`,
  `/bootcamp-feedback`, `/bootcamp-note`, `/graduate` and `/package-bootcamp` on every
  assistant. Only the Claude package ships those as commands. The GitHub Copilot, Kiro,
  ChatGPT and Gemini packages carry the same operations as skills, and their install pages
  tell the bootcamper to ask in plain English. Measured with the pattern the new test uses,
  each of those four packages held 28 lines with a slash form before the change and holds
  none after it. The Claude package holds 29 before and after.
  - **The approach.** Two implementations were raced from `a8b1e5c` and judged against a
    rubric written first. The one applied here uses two mechanisms the build already has: a
    host value for an inline mention, and a `host:only claude` / `host:except claude` block
    where the sentence itself must differ. The other used host values only, with one verb
    value, and left sentences such as `Reached by the "Back up the bootcamp" command.` in
    the four packages. No file under `tools/` changes.
  - **Applying it to `41f0f96`.** #47, #33, #32, #31, #26, #29 and #27 merged after the patch
    was cut. A three-way apply left four files in conflict, each where #29 had reworded a
    hook statement: `feedback.md`, `notes.md`, `packaging.md` and `graduation/SKILL.md`. Those
    four were taken as they are on `main` and the patch's edits were made again on the
    current wording by a script whose every anchor must match exactly once. Three blocks
    differ from the raced patch for that reason: the `feedback.md` block and the first
    `notes.md` block carry #29's "`feedback-capture.py` where a hook runs it on this
    assistant" in both halves, and the `notes.md` block spans two lines so the sentence stays
    whole. `packaging.md` keeps #29's text below its block. The other 22 files applied as
    raced.
  - **The host values.** `command_prefix` is removed from all five `host.json` files; nothing
    read it. In its place each profile declares six values under `vars`:

    | Value | Claude | GitHub Copilot, Kiro, ChatGPT, Gemini |
    |---|---|---|
    | `invoke_start_bootcamp` | `/start-bootcamp` | `"Start the bootcamp"` |
    | `invoke_bootcamp_feedback` | `/bootcamp-feedback` | `"Bootcamp feedback"` |
    | `invoke_bootcamp_note` | `/bootcamp-note` | `"Make a note"` |
    | `invoke_graduate` | `/graduate` | `"Graduate"` |
    | `invoke_package_bootcamp` | `/package-bootcamp` | `"Back up the bootcamp"` |
    | `invoke_package_bootcamp_in_string` | `/package-bootcamp` | `'Back up the bootcamp'` |

    The first five are named after the files in `source/commands/`, so a test derives the
    names. The sixth is not in the issue's table. It exists because the message
    `session-start.py` prints sits inside a double-quoted Python string whose bytes must not
    change in the Claude package, and a double-quoted request placed there leaves a script
    that does not parse. A test holds the sixth equal to the fifth with `"` written as `'`.
  - **The source.** 35 tokens in 13 files. Nine block pairs in eight files, each pair with
    the same number of lines in both halves: the closing line of graduation, the
    finished-bootcamp reply, the Module 7 line the bootcamper is shown, the quote of the
    closing line in `commands/graduate.md`, and five sentences to the guide in `packaging.md`,
    `notes.md` (two), `feedback.md` and `ground-rules.md`. Inside a block the operation still
    comes from the host value, so each phrase has one home.
  - **What the four packages now say.** They render these lines identically; quoted from the
    built GitHub Copilot package.
    - Closing line of graduation: `Say "Back up the bootcamp" anytime to bundle your bootcamp
      results into one zip you can archive, move to another machine, or share with others.`
    - Finished-bootcamp reply: `> Your Senzing bootcamp is complete. Say "Back up the
      bootcamp" anytime to bundle your bootcamp results into one zip you can archive, move to
      another machine, or share with others.`
    - `session-start.py` on a finished project, run from the built package: `… say the
      bootcamp is complete, name 'Back up the bootcamp', and end on the one open question it
      pins, asking what they would like to explore.` The output is ASCII-only in all five
      packages.
    - Module 7: `You can report it by saying "Bootcamp feedback"."`
    - An inline mention is the request in code format, for example ``and suggest
      `"Bootcamp feedback"`.``
  - **The Claude package is unchanged, all of it.** Every package was built from `41f0f96`
    before the first edit and again from the final tree, with
    `python3 -m tools.bootcamp_build build --out <dir>`. `diff -r` of the two `plugins/claude`
    trees prints nothing, and a SHA-256 list of its 92 files is the same before and after; 45
    of them are `.md` and 26 are `.py`. The built `site/`, `public/` and the three catalogs
    are identical too. The 52 files that differ are 13 in each of the other four packages.
  - **Tests.** `tests/test_each_package_names_an_operation_in_its_own_form.py` is new and
    holds 31 tests in six classes; `tests/_invocations.py` is the helper it and the converted
    tests share. It builds every package and the site.
    - `NoRequestPackageNamesASlashCommand` reads every file of every package that ships no
      commands, with no exceptions list, a file that is not UTF-8 included. The names come
      from `source/commands/`, and the pattern is the one
      `tests/test_documented_commands_match_the_shipped_set.py` holds, so a name inside a path
      is not a match. Controls: the same scan finds all five in the Claude package, planted
      forms are found, path shapes are not, and a sixth name is covered.
    - `EveryAssistantDeclaresEachOperation` holds Claude's values to the slash commands and
      each other assistant's value to the phrase in the "Say" column of its own built install
      page, in the row for the same operation. Words are compared and the style of the
      quotation marks is not. It also holds that no profile declares `command_prefix`.
    - `TheClosingLineIsPinnedInBothForms` pins both forms of the closing line, the finished
      reply and the quote in the graduate operation, and that no package carries the other
      form.
    - `TheFinishedMessageIsAscii` runs each package's own built `session-start.py` on a
      finished project.
    - `AChangedSentenceReadsWhole` pins the Module 7 line in both forms and fails where a
      request is called a "command".
    - `TheSetsAreNotEmpty` fails when the commands, the assistants or the install-page rows
      come back empty (INV-265).
    - Negative control run once, in a throwaway clone of `41f0f96` holding only the two new
      files: 22 of the 31 tests fail (`FAILED (failures=54, errors=47)`).
  - **Six existing tests changed, and no case was retired.** Each pinned a slash form by
    reading `source/`, where the form is now a token or sits beside its other form in a
    block. Each now reads every built package and holds the form that package uses: the
    slash form on the Claude package and the request form on each of the other four. No test
    method was removed from any of the six; ten were added.
    `tests/test_graduation_ending_surfaces.py` (18 to 20 test methods),
    `tests/test_a_finished_bootcamp_is_never_resumed.py` (25 to 30, which now runs each
    package's built scripts), `tests/test_generated_data_supports_its_success_criteria.py`
    (35 to 36), `tests/test_coherence_sweep_523.py` (29 to 30) and
    `tests/test_resume_requires_a_recorded_module.py` (29 to 30).
    `tests/test_bootcamp_build_hosts.py` keeps its 14: its check that a command turned into a
    skill keeps its instructions now renders the command for the host before counting lines,
    because a command can hold a host block.
  - **Left as it is.** "Offer the command" in `packaging.md` stays shared: the issue puts the
    word "command" with no slash form out of scope. `source/hooks/README.md` still names the
    slash commands and ships in the Claude package only. The install pages and each
    `site.commands_note` are read by the new test and not changed. A later change of form for
    one assistant is values-only at the 19 token sites outside blocks, and moves that
    assistant across the nine block pairs; `test_one_assistant_ships_commands_and_the_others_do_not`
    fails first and says so.
  - **Two rendered sentences nest straight quotes.** `"… You can report it by saying
    "Bootcamp feedback"."` and `verbatim: "Say "Back up the bootcamp" anytime …"`. The
    closing line is pinned with straight double quotes, and both sites quote a line to say.
  - **Not observed.** No real assistant read the changed text. Whether saying a request, or
    typing `/name` or `$name`, reaches the operation on GitHub Copilot, Kiro, ChatGPT or
    Gemini is still unverified, as the issue scopes it, and no record is added to any
    `hosts/<assistant>/checks.json`. Verified on Linux only, with Python 3.12.3. The change is
    text and host values: no script logic, path or encoding changes, the printed message
    stays ASCII, and the tests are stdlib `unittest` reading files as UTF-8 (INV-001).
- **Invariants.** Establishes no new invariant (INV-309), and proposes a change to one in
  force. The register is not edited here (INV-365). The change adds no hard-rule line and
  changes the wording of none. INV-057's 2026-11-10 note pins the closing line in the slash
  form with no assistant named, and the block below proposes the dated note that gives it per
  assistant. INV-102's 2026-11-10 note calls that line "its one `/package-bootcamp` line";
  the issue has the INV-057 note cover it, and it does. **One sentence of the drafted note
  goes beyond the issue, as an assumption:** INV-227, INV-239, INV-254 and INV-392 also name
  an operation by its slash command, and the note says the same reading applies to them. It
  is one block and not five so the maintainer rules once; the sentence can be struck, or
  made four notes, at review. INV-388 names the command only as where a defect was observed
  and is left alone. Until the maintainer applies the note, only the tests hold the request
  form. The docstring of `tests/test_each_package_names_an_operation_in_its_own_form.py`
  describes the amendment as drafted for `/review-invariants`; INV-386 wants it reworded when
  the note is registered.

- **PROPOSED AMENDMENT to INV-057 — applied 2026-11-18 by the maintainer.**
    - ⛔ **Render the terminal banner, verbatim, exactly once, then the one `{{host.invoke_package_bootcamp}}` line below it, verbatim.** — in `source/skills/graduation/SKILL.md`

  INV-057's 2026-11-10 note pins the closing line as "Run `/package-bootcamp` anytime to
  bundle your bootcamp results…" on every assistant. Only the Claude package ships that slash
  command. The other four packages carry the operation as a skill, and their install pages
  tell the bootcamper to ask for it in plain English. Since #28 each package shows the line
  in its own assistant's form, taken from that assistant's `invoke_package_bootcamp` host
  value, and `tests/test_graduation_ending_surfaces.py`, the enforcer the 2026-11-10 note
  names, pins both forms. Without the note below the register still reads as requiring the
  slash form everywhere, so the registry and its enforcer disagree, and the next editor
  writes the slash form back into shared text: a command nobody has run on those assistants,
  in the last line their bootcampers see.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-057** — (⚠️ **Dated note, 2026-11-17 (#28): the closing line names the packaging operation in the assistant's own form.** In a package that ships the slash command, which today is the Claude package alone, the line reads, verbatim, "Run `/package-bootcamp` anytime to bundle your bootcamp results into one zip you can archive, move to another machine, or share with others." In every other package it reads, verbatim, "Say "Back up the bootcamp" anytime to bundle your bootcamp results into one zip you can archive, move to another machine, or share with others.", which names the request that assistant's install page gives. Each assistant's form is its `invoke_package_bootcamp` value in `hosts/<assistant>/host.json`. The finished-bootcamp reply in `bootcamp-onboarding/SKILL.md` step 2 uses the same sentence in the same form. Where INV-102's 2026-11-10 note says "its one `/package-bootcamp` line", read the line in the assistant's own form. The rest of the 2026-11-10 note is unchanged: the line is shown exactly once, together with the banner, as a plain line outside its fence, on the normal path and after the production build's Abort alike, under every verbosity preset; it is a statement with no 👉 and no question, names no archive path, and nothing follows it (INV-251). Enforced by `tests/test_graduation_ending_surfaces.py` and `tests/test_each_package_names_an_operation_in_its_own_form.py`, which build every assistant's package. Neither establishes that saying the request reaches the operation on a real assistant; no such run was recorded when this note was drafted.)

- **Commit:** uncommitted

## every-package-states-one-assistants-shell-as-the-guides-shell

- **Implemented:** 2026-11-17 (issue #27)
- **Files changed:** `hosts/claude/host.json`, `hosts/copilot/host.json`,
  `hosts/kiro/host.json`, `hosts/chatgpt/host.json`, `hosts/gemini/host.json`,
  `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/bootcamp-onboarding/module-completion.md`,
  `source/skills/bootcamp-onboarding/packaging.md`,
  `source/skills/bootcamp-preparation/SKILL.md`, `source/skills/graduation/SKILL.md`,
  `source/skills/module-02-sdk-setup/SKILL.md`,
  `source/skills/module-03b-truthset-visualization/phase1-visualization.md`,
  `source/skills/module-03b-truthset-visualization/visualization-api-reference.md`,
  `source/skills/module-04-data-collection/SKILL.md`,
  `source/skills/module-07-query-visualize-discover/phase1-query-visualize.md`,
  `source/commands/package-bootcamp.md`, `source/hooks/fallbacks/session-start.md`,
  `source/hooks/fallbacks/checkpoint-tick.md`, `source/hooks/fallbacks/precompact-recap.md`,
  `source/hooks/fallbacks/session-end.md`,
  `tests/test_each_package_states_its_own_guide_shell.py` (new),
  `tests/test_guide_run_blocks_declare_their_shell.py`,
  `tests/test_build_and_run_statement.py`, `tests/test_container_route_build_and_run.py`,
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it rewords what the bootcamp's own guide text says about the guide's shell, adds two values
  to each assistant's profile, gives four commands that run the bootcamp's own scripts a
  second form, and adds tests that read that text and those profiles. It asserts nothing
  about Senzing. No absence claim about the Senzing MCP server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** Each package now states the guide-run rule for its own assistant. This is
  finding 2 of `production-readiness-audit-2026-11-17`. Before the change all five packages
  said a guide-run block runs "with its Bash tool" in "the guide's POSIX shell, which on
  Windows is Git Bash", and the line after every guide-run block repeated it. That describes
  one assistant: the other profiles name their shell tool `bash`, `execute_bash` and
  `run_command`, one of them lists a PowerShell tool as well, and no
  `hosts/<assistant>/checks.json` records a run on Windows.
  - **The approach.** Two implementations were raced from `1f7c4d9` and judged against a rubric
    written first. The one applied here states the values in each `host.json` and carries the
    wording that differs in a `host:only` and a `host:except` block. The other had the build
    derive the tool name from `hooks.tools.shell`, and changed `tools/bootcamp_build/` to do
    it. No file under `tools/` changes here. The patch applied to `ef44a02` without a
    conflict, after #25, #47, #33, #32, #31, #26 and #29 had merged, and was then read
    against their guards.
  - **The host values.** Each `hosts/<assistant>/host.json` gains two values under `vars`.
    `shell_tool` is a second copy of that profile's `hooks.tools.shell`, needed because a
    `{{host.…}}` token reads only `vars`; a test holds the two equal. `scripts_dir_powershell`
    is `scripts_dir` with the plugin-root variable read as `$env:NAME`. The issue names one
    value. The second exists because `"${PLUGIN_ROOT}/…"` in PowerShell reads a PowerShell
    variable, which is empty: the failure INV-167's #505 note records.
  - **The statement.** `ground-rules.md` → `#guide-run-blocks` stays the one statement
    (INV-300). Its guide-run bullet is now written twice in the source, once per host block.

    | Package | The tool it names | The shell it states |
    |---|---|---|
    | Claude | `Bash` | the guide's POSIX shell, which on Windows is Git Bash |
    | GitHub Copilot | `bash` | whichever shell that tool provides; on Windows unverified |
    | Kiro | `execute_bash` | whichever shell that tool provides; on Windows unverified |
    | ChatGPT | `Bash` | whichever shell that tool provides; on Windows unverified |
    | Gemini | `run_command` | whichever shell that tool provides; on Windows unverified |

    The four packages below the first row also carry one more bullet, "Where the guide's shell
    is PowerShell": the guide translates a guide-run block to Windows PowerShell 5.1 with the
    table of 5.1 syntax limits in that section, runs the translation and treats the result as
    unverified in that shell. A translated block that fails follows its own site's failure
    rule. A PowerShell-only guide-run block is run directly, and the
    `powershell.exe -NoProfile -Command …` call and its quoting apply only from a POSIX shell.
    The Claude package's statement keeps its meaning. It differs from the earlier one in three
    places: the tool is written `` `Bash` `` from the host value, the quoted line is the new
    wording, and the PowerShell-only bullet opens "From a POSIX shell the guide runs it as one
    call".
  - **Three shared sentences are now conditions.** Each stated the guide's own shell as POSIX
    in every package: the project root's spelling ("In a POSIX shell it is written with
    forward slashes"), the native-Windows Build and Run call ("which from a POSIX shell is:")
    and the PowerShell-only bullet's runner ("From a POSIX shell the guide runs it as one
    call").
  - **The line after a guide-run block.** One wording, the same bytes in every package, which
    names no shell and no tool: "Guide-run; unverified on Windows: no test runs it there",
    then the link to `#guide-run-blocks`. The source holds it at 54 sites in 11 files, and
    the statement quotes it once in each host block. The issue counts 55: each package
    carries 54 sites and one quoted copy.
  - **The fallback commands.** `session-start.md`, `checkpoint-tick.md`, `precompact-recap.md`
    and `session-end.md` each keep their POSIX command, which ends in `< /dev/null`, and gain
    one sentence, "Where your shell is PowerShell, run this form instead:", and a `powershell`
    fence under the same heading: `$null | python3 "{{host.scripts_dir_powershell}}/<name>.py"`.
    No single form runs in both shells, because of the redirect and because of the
    plugin-root variable, so each command is given in both. The text #29 put around those
    commands is unchanged, and the new sentence names no hook. The fallback files stay exempt
    from the line after a guide-run block. The Claude package's `host-rules.md` carries no
    command, as before.
  - **Known gap: no PowerShell form was executed, by anyone, in any PowerShell.** This machine
    has no `pwsh`, `powershell` or `powershell.exe`. The 16 lines that are unexecuted are the
    four commands in each of the four packages:
    `$null | python3 "$env:PLUGIN_ROOT/scripts/<name>.py"` in the GitHub Copilot, ChatGPT and
    Gemini packages and
    `$null | python3 "$env:PLUGIN_ROOT/skills/bootcamp-onboarding/scripts/<name>.py"` in the
    Kiro package, for `session-start`, `checkpoint-tick`, `precompact-recap` and
    `session-end`. They are checked by reading only: each follows its POSIX form under the
    same heading, runs the same script, takes the scripts directory from `$env:`, opens with
    `$null |`, and carries none of `&&`, `||`, `<`, inline `python -c`, a bare `$NAME` or
    `/dev/null`. Three things are assumed and not observed: that Windows PowerShell 5.1 runs
    the line as written, that `$null |` closes the script's input as `< /dev/null` does, and
    that the interpreter is named `python3` on Windows. The last is assumed by every hook
    command and by the POSIX forms too.
  - **A raced test class was left out.** The raced patch held a class, `ThePowerShellFormsRun`,
    that ran each PowerShell form where `pwsh` or `powershell` is on `PATH` and skipped
    elsewhere. It skipped where the patch was written and it skips here, so its first real
    run would have been in CI, on both legs, never seen to pass. Nothing in this repository
    runs a native command with `$null |` under `pwsh`, so reading could not establish that
    it would pass. It is not shipped. No other test was changed to make up for it. What the
    suite does run is each script on the input `$null |` is expected to hand it (no input, or
    one empty line), which runs the script and not PowerShell.
  - **Tests.** `tests/test_each_package_states_its_own_guide_shell.py` is new and holds 33
    tests in five classes. It builds all five packages.
    - `TheHostValueIsTheProfilesOwnTool` holds `vars.shell_tool` equal to `hooks.tools.shell`
      and `vars.scripts_dir_powershell` to `vars.scripts_dir`, through the loader and from the
      JSON on disk.
    - `EachPackageStatesItsOwnToolAndShell` reads each built statement: the tool is the
      profile's own, the shell sentence is the one for that assistant and appears once, the
      other one is absent, and the four packages carry the PowerShell rule with the 5.1 table
      above it. It scans every Markdown file of the four packages for a kind of shell or a
      shell tool stated as the guide's own that the profile does not declare. A condition
      ("in a POSIX shell, …") is not reported.
    - `TheLineAfterABlockIsOneWordingEverywhere` reads every line that links the statement, in
      every package: one wording, each link reaching that package's statement, and as many
      sites as `source/` holds, derived and not a literal count (INV-246).
    - `EveryFallbackCommandHasBothForms` reads each of the four built `host-rules.md` files as
      "Known gap" above describes, and requires the Claude package's to hold no command.
    - `ThePosixFormsRun` runs each POSIX form as written, with `sh`, from the built package,
      in a throwaway bootcamp project with the input left open. A control removes the
      redirect from the checkpoint command and sees it wait.
    - Negative controls that run on every pass: a drifted, a missing and a bare-variable host
      value; the Claude package read as each other assistant's and the reverse; the wording
      before #27; another profile's tool name; each phrase of the PowerShell rule removed; the
      5.1 table moved below the statement; a link that misses the statement; the PowerShell
      forms removed; each banned shape; and a PowerShell form under another heading.
    - Negative control run once, in a throwaway clone of `ef44a02` holding only the new test
      file: 12 of the 33 tests fail (`FAILED (failures=91, errors=6)`), in four of the five
      classes. `ThePosixFormsRun` passes there, since the POSIX forms did not change.
  - **Three existing tests changed, in the wording they pin and nothing else.**
    `tests/test_guide_run_blocks_declare_their_shell.py`: the `POINTER` constant is the new
    line, the pattern for the tool reads `` `{{host.shell_tool}}` `` where it read "Bash", the
    pattern for the PowerShell-only runner reads "From a POSIX shell the guide runs it as one
    call", and its docstring says what #27 changed. `tests/test_build_and_run_statement.py`
    and `tests/test_container_route_build_and_run.py` each hold their own copy of `POINTER`,
    updated to match. Every other pattern and every negative control in those files is as it
    was. `tests/test_windows_forms_at_hand_run_sites.py` imports `POINTER` and needed no edit.
  - **Left as it is.** "There is no PowerShell fallback" stays shared: in the four packages it
    still means a block that failed in the guide's shell is not retried through PowerShell.
    The preamble the build writes at the top of `host-rules.md` names the scripts directory
    in its POSIX spelling only. The docstrings of four other test modules still explain their
    checks with "the guide's POSIX shell, Git Bash on Windows"; the checks hold in any POSIX
    shell. Which assistants keep the POSIX statement is written in two places, the two marker
    lines in `ground-rules.md` and `POSIX_SHELL_KNOWN` in the new test.
  - **Not observed.** No real assistant read the reworded text, ran a guide-run block or
    translated one. Which shell any assistant gives the guide on Windows is still not known,
    for Claude as for the others: the Claude package keeps its statement because the issue
    decided so, not because a run was recorded. Verified on Linux only, with Python 3.12.3.
    No run on macOS, on Windows or on a real assistant happened, so no record is added to any
    `hosts/<assistant>/checks.json`. The new test reads files as UTF-8 through `pathlib`; its
    one class that starts a shell skips where there is no POSIX `sh` (INV-001).
- **Invariants.** Establishes no new invariant (INV-309), and proposes a change to one in
  force. The register is not edited here (INV-365). The change adds no hard-rule line:
  `conformance.py since --since-last-audit` reports none for the range. INV-167's #508, #596
  and #597 notes word the guide's shell as one assistant's, and the #508 note fixes the
  pointer line that this change rewords. The block below proposes the dated note that scopes
  them to the assistant. Until the maintainer applies it, only the tests hold the new
  wording. INV-163's wording does not change, so it gets no block: the line after a block
  still carries its disclosure. INV-300 is unchanged: the statement is still made once.

- **PROPOSED AMENDMENT to INV-167 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **It runs in whichever shell that tool provides, and which shell that is on Windows is unverified.** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **the guide translates a guide-run block to Windows PowerShell 5.1 with the table of 5.1 syntax limits above, runs the translation, and treats the result as unverified in that shell** — in `source/skills/bootcamp-onboarding/ground-rules.md`
    - ⛔ **Guide-run; unverified on Windows: no test runs it there** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-167's #508, #596 and #597 notes say a guide-run block runs "with its Bash tool" in "the
  guide's POSIX shell (Git Bash on Windows)", with no assistant named. That is one assistant's
  shell. The other four profiles declare other shell tools, one declares a PowerShell tool as
  well, and no `checks.json` records a run on Windows, so the registered wording asserts a
  shell nobody has observed for four of the five packages. Since #27 the statement and the
  pointer line say something the notes do not, and
  `tests/test_guide_run_blocks_declare_their_shell.py`, the enforcer the #508 note names, pins
  the new pointer wording. Without the note below the registry and its enforcer disagree.
  Enforced by `tests/test_each_package_states_its_own_guide_shell.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-167** — (⚠️ **Dated note, 2026-11-17 (#27): the guide's shell is stated per assistant, and the pointer line names no shell; the syntax rules above, the hand-run rule and the #505 note are unchanged.** The #508, #596 and #597 notes describe a guide whose shell tool is Bash and whose shell is POSIX, Git Bash on Windows. The Claude package keeps that statement by the maintainer's decision on #27; no run on Windows is recorded for any assistant, and a real run recorded in `hosts/<assistant>/checks.json` is what moves an assistant from one statement to the other. `ground-rules.md` `#guide-run-blocks` stays the one statement (INV-300) and MUST, in each assistant's package, name the guide's shell tool from that assistant's `shell_tool` host value, which MUST equal its `hooks.tools.shell`, and say which shell runs a guide-run block: the POSIX shell of those notes in a package that keeps that statement, today the Claude package alone; in every other package whichever shell the assistant's tool provides, with that shell on Windows stated as unverified (INV-163). In a POSIX shell those notes bind as written. Where the guide's shell is PowerShell, the guide MUST translate a guide-run block to Windows PowerShell 5.1 with that section's table of 5.1 syntax limits, run the translation and treat the result as unverified in that shell; a translated block that fails follows its own site's failure rule; and a PowerShell-only guide-run block is run directly, the `powershell.exe -NoProfile -Command …` call and its quoting applying only from a POSIX shell. The pointer line after a guide-run block MUST name no shell and no tool, in one wording at every site and in every assistant's package: "Guide-run; unverified on Windows: no test runs it there", linking `#guide-run-blocks`. A command in a built `host-rules.md` whose package does not state a POSIX shell MUST be given in a POSIX form and in a Windows PowerShell 5.1 form that meets the syntax rules above and the #505 note. Enforced by `tests/test_each_package_states_its_own_guide_shell.py`, which builds every assistant's package, and by `tests/test_guide_run_blocks_declare_their_shell.py`. Neither establishes which shell an assistant gives the guide on Windows, and neither executes a PowerShell form: the PowerShell forms are checked by reading and were unexecuted when this note was drafted (INV-163).)

- **Commit:** uncommitted

## the-fallback-rules-and-the-ground-rules-state-opposite-facts-about-the-same-hooks

- **Implemented:** 2026-11-17 (issue #29)
- **Files changed:** `source/hooks/fallbacks/write-gate.md`,
  `source/hooks/fallbacks/stop-nudge.md`, `source/hooks/fallbacks/precompact-recap.md`,
  `source/hooks/fallbacks/session-end.md`, `source/skills/bootcamp-onboarding/ground-rules.md`,
  `source/skills/bootcamp-onboarding/notes.md`, `source/skills/bootcamp-onboarding/feedback.md`,
  `source/skills/bootcamp-onboarding/packaging.md`,
  `source/skills/bootcamp-onboarding/module-completion.md`, `source/skills/graduation/SKILL.md`,
  `source/skills/module-02-sdk-setup/SKILL.md`,
  `source/skills/module-05-data-quality-mapping/phase2-data-mapping.md`,
  `tests/test_hook_statements_hold_on_every_assistant.py` (new),
  `tests/test_claimed_hook_triggers_are_real.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it rewords what the bootcamp's own guide text says about the bootcamp's own hooks, and adds
  tests that read that text and each assistant's hook mapping. It asserts nothing about Senzing.
  No absence claim about the Senzing MCP server is made, so INV-213's `owner-checked:` clause
  is not owed.
- **Summary:** What a package says about a hook now holds on the assistant that reads it. This
  is finding 4 of `production-readiness-audit-2026-11-17`. Before the change, the Copilot,
  Kiro, ChatGPT and Gemini packages said in `host-rules.md` that nothing checks a write,
  nothing re-opens a turn that ends without its question, and nothing runs when the
  conversation is compacted or a session ends. The ground rules in the same packages said
  without condition that a hook enforces the write gate, folds the recap and stops
  containers. The shared text also named Claude's hook events in every package.
  - **The approach.** Two implementations were raced from `e90d05a` and judged against a rubric
    written first. The one applied here chooses each fallback's wording with the `host:only`
    and `host:except` markers the source already has, and adds a test that compares the
    wording with each assistant's mapping. The other had the build choose the wording, and
    changed `tools/bootcamp_build/emit.py` to do it. No file under `tools/` changes here.
  - **The four fallbacks.** `write-gate.md`, `stop-nudge.md`, `precompact-recap.md` and
    `session-end.md` each hold two statements and one instruction. A `host:only` block holds
    "When it runs, a hook …, but it may not run here." A `host:except` block naming the same
    assistants holds "Nothing …". One "So …" instruction follows both, outside the markers.
    The lists name the assistants whose mapping has an event for the hook that is not
    advisory. What each package now carries:

    | Fallback | GitHub Copilot | Kiro | ChatGPT | Gemini |
    |---|---|---|---|---|
    | `write-gate.md` | may not run | may not run | may not run | may not run |
    | `stop-nudge.md` | may not run | nothing does this | may not run | may not run |
    | `precompact-recap.md` | may not run | nothing does this | may not run | nothing does this |
    | `session-end.md` | may not run | nothing does this | may not run | nothing does this |

    The other six fallbacks say nothing about whether a hook runs and keep their text. The
    Claude package's `host-rules.md` is unchanged: its hooks are guaranteed, so it carries no
    fallback. `claude` is still named in each list, because the lists follow the mapping alone.
  - **The shared text.** Sixteen passages in eight files under `source/skills/` are reworded so
    that each holds whether or not a hook backs the rule: seven in `ground-rules.md` (worked
    steers, the working directory, file placement, the recap checkpoint, feedback, notes and
    closing questions), the trigger sentences of `notes.md` and `feedback.md`, the "no hook for
    this flow" sentence of `packaging.md`, Step 2d of `module-completion.md`, the terminal step
    of `graduation/SKILL.md`, three container passages in `module-02-sdk-setup/SKILL.md` and
    the write-gate sentence of `phase2-data-mapping.md`. The form is the one
    `phase3-test-load.md` already used: "whether or not a hook backs it on this assistant",
    with "where a hook runs it" or "where it runs" on the sentence that names what the hook
    does.
  - **Event names.** No Markdown file under `source/skills/` or `source/hooks/fallbacks/` holds
    a hook event name any more. A hook is named by what it does ("the write-gate", "the
    closing-question nudge") or by its script (`stop-nudge.py`, `feedback-capture.py`,
    `session-end.py`). `source/hooks/README.md` is not touched: it ships to the Claude package
    only and keeps Claude's event names.
  - **Built on #26, which merged first.** The issue says the `hooks/README.md` pointers are left
    as they are. #26 had already removed them when this change was applied, so three hunks of
    the raced patch did not apply to `ground-rules.md` and were redone by reading: the worked
    steers sentence and the file-placement bullet carry no pointer, the file-placement bullet
    keeps #26's "it also blocks a file write that holds an obvious hardcoded secret", and the
    bullet above #26's off-switch item no longer says "the plugin's `Stop` hook". The
    off-switch item itself is unchanged.
  - **Left as it is.** `bootcamp-onboarding/SKILL.md`, the resume step, still says which hooks
    stay silent before a module is recorded. It is not in the issue's list and the new scan
    does not report it. No `hosts/*/host.json`, no hook script and no build tool changes.
  - **Tests.** `tests/test_hook_statements_hold_on_every_assistant.py` is new and holds 30
    tests.
    - `FallbackWordingFollowsTheMapping` builds each package and compares what each section of
      its `host-rules.md` says with that assistant's `hooks` mapping. It requires each of the
      four fallbacks to make exactly one statement in each package that carries them, and no
      marker line to reach a package.
    - `TheMarkersNameTheMappedAssistants` reads the marker lists in the source: one
      `host:only` and one `host:except` block per fallback, both naming exactly the assistants
      the mappings give, for every assistant under `hosts/` including one whose package
      carries no fallback today. It also requires the two renderings to differ in the
      statement only.
    - `TheWordingRule` holds the rule on made-up mappings: no event, an advisory event, an
      event, and a hook on two events.
    - `NoRetiredSentenceIsBack` pins 21 sentences the issue retired, by file and passage, with
      whitespace collapsed (INV-346).
    - `NoUnconditionalHookStatement` scans every Markdown file under `source/skills/`
      (INV-246) for a sentence that says a hook acts and carries no condition.
    - `SharedTextNamesNoHookEvent` takes every event name from every mapping and searches
      `source/skills/` and `source/hooks/fallbacks/` for it. `APackageNamesOnlyItsOwnEvents`
      searches the Markdown of each built package for a name that is in another mapping and
      not in its own. `Stop` counts only in backticks or directly before "hook".
    - Negative controls that run on every pass: a mapping that loses an event, a mapping that
      gains one, a wording swapped, both wordings at once, a statement removed, each retired
      sentence put back, thirteen unconditional sentence shapes, every event name, `Stop` as a
      word against `Stop` as an event, and one package's Markdown read with another's mapping.
    - Negative control run once, in a throwaway clone of `ffe20a4` holding only the new test
      file: 11 of the 30 tests fail (`FAILED (failures=52, errors=1)`).
  - **One existing test changed.** `tests/test_claimed_hook_triggers_are_real.py` held the
    pattern "Triggered by the plugin's `UserPromptSubmit` hook", a sentence this issue retires.
    `CLAIMS_HOOK` now matches "Triggered by `feedback-capture.py` where a hook runs it", the
    script that test reads. Every assertion that used the pattern is kept, and its docstring
    says what changed. Two other tests were kept green by wording, not by editing them:
    `test_coherence_sweep_523.py` needs "write-gate blocks every write outside the project" on
    one line of `phase2-data-mapping.md`, and `test_recap_checkpoint_writer.py` needs "plugin
    creates the file" in `ground-rules.md`.
  - **Known limits.** The built-package event-name check reads Markdown only. The hook scripts
    and the hook adapter carry the canonical event names as protocol values in every package,
    and each hook configuration file carries its own assistant's names by design. The
    unconditional-statement scan knows a closed list of sentence shapes, taken from the
    sentences the audit found. A script named as the one that acts ("`session-end.py` stops
    recorded containers at close-out") is not counted, because it is true whether a hook or
    the guide runs the script. The mapping does not choose the wording by itself: when a
    mapping changes, the suite fails until the assistant's id is moved in or out of the two
    marker lines of the affected fallback.
  - **Not observed.** No real assistant read the reworded text or ran a hook. What is true for
    an assistant is taken from its mapping. Verified on Linux only, with Python 3.12.3. No run
    on macOS, on Windows or on a real assistant happened, so no record is added to any
    `hosts/<assistant>/checks.json`. The change is text and standard-library tests that read
    files as UTF-8 through `pathlib`, with no branch on the platform (INV-001).
- **Invariants.** The register is not edited here (INV-365). The change ships three hard-rule
  lines, in the new test module's docstring. `since` does not report them, because `tests/` is
  not a rule home. The three blocks below cover them, one rule each (INV-309). No
  `PROPOSED AMENDMENT` is written: INV-054, INV-101 and INV-420 name Claude's hook events in
  the register's own prose, which no package carries, and none of them requires shipped text
  to use an event name. INV-003 is the invariant the finding was filed under; its wording is
  not touched.

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** A fallback's statement about its hook follows the assistant's hook mapping. The rule already shipping, quoted:
    - ⛔ **A fallback says that nothing does a hook's job only where the assistant's mapping has no event for the hook or lists it as advisory, and says that the hook may not run where the mapping has one.** — in `tests/test_hook_statements_hold_on_every_assistant.py`

  Enforced by `tests/test_hook_statements_hold_on_every_assistant.py`.

  **Why it is not an existing invariant:** INV-003 says the bootcamp is consistent, coherent
  and complete, and does not say what a fallback states about its hook. INV-430 says which
  source files may ship to some assistants and not others, and nothing about what a shipped
  fallback says. INV-052 says how a hook is invoked. None of them ties the text of a fallback
  to `hooks.events` and `hooks.advisory`.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — A fallback under `source/hooks/fallbacks/` that says whether a hook does its job MUST say that nothing does it only in the package of an assistant whose `hooks.events` mapping in `hosts/<assistant>/host.json` has no event for that hook or lists the event in `hooks.advisory`. In the package of every other assistant that carries the fallback it MUST say that a hook does the job when it runs and that it may not run. A hook declared on more than one event has no event only when every one of them is null or advisory. Both wordings MUST be followed by the same instruction to the guide, and no package may carry both wordings for one hook. Observed 2026-11-17 (`production-readiness-audit-2026-11-17`, finding 4): four packages said "Nothing checks a write before it happens" although each of those assistants has an event for the write gate. Enforced by `tests/test_hook_statements_hold_on_every_assistant.py`, which builds each package and compares each fallback's statement in `host-rules.md`, and each `host:only` and `host:except` list in the source, with every assistant's mapping. It recognizes the two wordings by their shape and **cannot** establish that a hook runs on a real assistant. (Source: `the-fallback-rules-and-the-ground-rules-state-opposite-facts-about-the-same-hooks`, GitHub issue #29, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Shared skill text states what a hook does only with a condition. The rule already shipping, quoted:
    - ⛔ **No file under `source/skills/` says without a condition that a hook does something.** — in `tests/test_hook_statements_hold_on_every_assistant.py`

  Enforced by `tests/test_hook_statements_hold_on_every_assistant.py`.

  **Why it is not an existing invariant:** INV-003 does not say how a rule that a hook backs
  on some assistants is to be worded. INV-200, INV-101 and INV-054 each say what one hook
  does, in the register's own prose, and none says how shipped text may speak of a hook on an
  assistant where it does not run.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — A Markdown file under `source/skills/` that says what a hook does MUST say it in a form that holds whether or not a hook backs the rule on the assistant reading it. The rule is stated as the guide's to keep, and the sentence that names the hook's action MUST carry its condition, for example "whether or not a hook backs it on this assistant", "where a hook runs it" or "where it runs". A script MAY be named as the one that acts, because that is true whether a hook or the guide runs it. Observed 2026-11-17 (`production-readiness-audit-2026-11-17`, finding 4): the ground rules said without condition that a hook enforces the write gate, folds the recap and stops containers, in four packages whose `host-rules.md` said that nothing does. Enforced by `tests/test_hook_statements_hold_on_every_assistant.py`, which pins each sentence #29 retired and scans every Markdown file under `source/skills/` for a sentence that says a hook acts and carries no condition. The scan knows a closed list of sentence shapes, so it **cannot** find an unconditional statement worded another way, and it cannot establish that a conditional sentence is true on a real assistant. (Source: `the-fallback-rules-and-the-ground-rules-state-opposite-facts-about-the-same-hooks`, GitHub issue #29, 2026-11-17.)

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** Shared text names no hook event, and a package's Markdown names only its own assistant's events. The rule already shipping, quoted:
    - ⛔ **Shared text names no hook event, and the Markdown of a built package names a hook event only when the event is in that assistant's own mapping.** — in `tests/test_hook_statements_hold_on_every_assistant.py`

  Enforced by `tests/test_hook_statements_hold_on_every_assistant.py`.

  **Why it is not an existing invariant:** INV-003 does not name hook events. INV-430 is about
  which files a package carries, and not about a name inside a file every package carries.
  INV-052 fixes how a hook is invoked, and not what shipped text may call its event. No
  registered invariant says that text every package carries may not use one assistant's event
  names.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — A Markdown file under `source/skills/` or `source/hooks/fallbacks/` MUST NOT hold a hook event name from any assistant's `hooks.events` mapping: shared text names a hook by what it does or by its script. A Markdown file in an assistant's built package MUST NOT hold an event name that is in another assistant's mapping and not in its own. The name `Stop` is also an ordinary word, and counts as an event name only in backticks or directly before "hook". `source/hooks/README.md` ships to the Claude package only and keeps Claude's event names. Observed 2026-11-17 (`production-readiness-audit-2026-11-17`, finding 4): shared text named `UserPromptSubmit`, `PreToolUse`, `PreCompact`, `SessionEnd`, `SessionStart` and `Stop` in every package, although the Copilot and Gemini mappings spell some of those events differently and the Kiro and Gemini mappings have no event for others. Enforced by `tests/test_hook_statements_hold_on_every_assistant.py`, which takes the names from the mappings on every run. It reads Markdown only, so it **cannot** see an event name in a hook script, the hook adapter or a hook configuration file, where the canonical names are protocol values or the assistant's own by design. (Source: `the-fallback-rules-and-the-ground-rules-state-opposite-facts-about-the-same-hooks`, GitHub issue #29, 2026-11-17.)

- **Commit:** uncommitted

## four-packages-point-at-hooks-readme-md-which-they-do-not-carry

- **Implemented:** 2026-11-17 (issue #26)
- **Files changed:** `source/skills/bootcamp-onboarding/SKILL.md`,
  `source/skills/bootcamp-onboarding/ground-rules.md`, `source/scripts/stop-nudge.py`,
  `source/scripts/feedback-capture.py`, `source/scripts/write-gate.py`,
  `tests/test_partial_shipping_has_a_reason.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it removes pointers at one of the bootcamp's own pages, states the two switches one of the
  bootcamp's own scripts reads, and says what the bootcamp's own write gate blocks. It asserts
  nothing about Senzing. No absence claim about the Senzing MCP server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** No shared text points at `hooks/README.md` any more, and the stop-nudge off
  switch is stated in the ground rules, which every package carries. This is finding 1 of
  `production-readiness-audit-2026-11-17`. Before the change, four prose sites and four script
  comment lines named the page in all five packages, while the Copilot, Kiro, ChatGPT and
  Gemini layouts drop it. The page was also the only place the off switch was documented, so
  those four packages did not say how to turn the nudge off.
  - **The four prose sites.** Each pointer is removed in every package, the Claude package
    included, and no `host:only` block keeps one.
    - `bootcamp-onboarding/SKILL.md`, the resume step: the sentence that sent the reader to
      the page for "each hook's gate and why" now gives the reason. The onboarding preface
      creates the progress file empty, no module is recorded until Bootcamp preparation's
      final write, and each of the four hooks has work to do in that window.
    - `ground-rules.md`, the worked-steer trigger record: the pointer is dropped. The sentence
      already says what `failed-run-net.py` does.
    - `ground-rules.md`, the write-gate bullet under "File placement": "lists everything it
      blocks" pointed at the page. The bullet now says the gate also blocks a file write that
      holds an obvious hardcoded secret, which is the one thing the page said and the bullet
      did not. The rest of the bullet is unchanged, and #29 rewrites it.
    - `ground-rules.md`, the administrative-writes bullet under "Progress and state": the
      "(see …)" pointer is dropped and the line re-wrapped. The claim that no harness setting
      suppresses a write's inline diff keeps its wording. Whether it holds on assistants other
      than Claude was not checked: the issue puts that out of scope.
  - **The four comment lines.** `stop-nudge.py` (two), `feedback-capture.py` and `write-gate.py`
    no longer name the page. Three lose "(hooks/README.md, Gate column)". The fourth, on the
    opt-out gate, now reads "see nudge_disabled() below", the function that reads the two
    switches. No code changed. The issue cites `write-gate.py:35`; the line was at 55 on
    `a465a9f`, and it was found by its text.
  - **The off switch.** One new list item under "Closing questions" in `ground-rules.md`. It
    says the switches apply where the hook that re-opens a turn runs, so it does not say the
    nudge is active: on Kiro that hook runs only if the bootcamper installed the hooks. It
    names no hook event, because the event has no one name across the assistants. It gives
    both switches: the `SENZING_BOOTCAMP_DISABLE_STOP_NUDGE` environment variable set to `1`,
    `true`, `yes` or `on`, and the top-level key `disable_stop_nudge: true` in
    `config/bootcamp_preferences.yaml`. It says how to turn the nudge back on: unset the
    variable, or set the key to `false` or remove it. It cites INV-055.
  - **Left as it is.** `source/hooks/README.md`, every `hosts/*/host.json` and the page's
    `PARTIAL` entry are unchanged, so no package gains or loses a file. The bullet above the
    new item still calls the hook "the plugin's `Stop` hook", and the "File placement" bullets
    still say `PreToolUse`: those event names in shared text belong to #29.
  - **Tests.** `tests/test_partial_shipping_has_a_reason.py` goes from 25 tests to 38.
    - `dropped_references()` takes the partial files from the shipped sets, and for each one
      reads every file of every built package that drops it, looking in the file's bytes for
      the source path and for the path a carrying package uses. The test asserts that all five
      packages were built, that at least one partial file was checked, that the files checked
      are exactly the partial ones, that each is covered by a `PARTIAL` entry and each entry
      has a file checked, and that every dropping package was read in full (INV-265). Six
      partial files are checked today: the five under `commands/` and `hooks/README.md`.
    - A second test holds the issue's first criterion in all five packages: no file names
      `hooks/README.md` except the page itself where a package carries it.
    - Three tests read the ground rules of each built package: both switch names are there;
      one list item holds the variable, the key and its file, the four values and the way
      back; and that item is conditional, names no event from any assistant's mapping and does
      not name the page. The item is read through `tests/_wrapped_text.py` with whitespace
      collapsed (INV-346). A fourth holds the four values against `truthy()` in the script.
    - Negative controls that run on every pass: four on scratch packages (a pointer in a
      skill, a pointer in a script comment, the path a carrier uses, and nothing to report),
      one that writes a pointer into a copy of a built package for each partial file, and two
      for the event and item readers.
    - Negative controls run once, each in a throwaway clone: against `a465a9f` with only the
      new test file, 6 of the 38 tests fail (`FAILED (failures=27)`); with one change made at
      a time on this branch (each of the eight pointers put back, and nine changes to the new
      item), each of 17 mutations fails the module.
  - **Known limits.** The scan finds a path written out in full with forward slashes. It does
    not find a path put together at run time or a file named by its base name alone, and it
    is not the general check that every path a package names resolves inside that package,
    which the issue puts out of scope. The off-switch tests show the switches are named, not
    that a hook reads them on any assistant.
  - **Not observed.** No real assistant read the reworded text or ran the hook. Verified on
    Linux only, with Python 3.12.3. No run on macOS, on Windows or on a real assistant
    happened, so no record is added to any `hosts/<assistant>/checks.json`. The new test code
    is standard library only, compares package paths in posix form and adds no branch on the
    platform (INV-001).
- **Invariants.** Establishes no new invariant (INV-309), and proposes a change to two in
  force. The register is not edited here (INV-365). The change adds no hard-rule line that a
  `conformance.py` view reads: `conformance.py since --since-last-audit` reports none for the
  range. It adds one hard-rule line to the test's docstring, which the first block below
  quotes. INV-430 says which files may be partial and does not say that a package must not
  name one it drops. INV-055 says the opt-out is documented and does not say where, and until
  this change four packages did not document it. Until the maintainer applies the notes
  below, only the test holds either rule. INV-003 is the invariant the finding was filed
  under; its wording is not touched.

- **PROPOSED AMENDMENT to INV-430 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **No package names a partial source file it drops.** — in `tests/test_partial_shipping_has_a_reason.py`

  INV-430 requires a recorded reason for a file that ships to some assistants and not others,
  and says outright that its test "does not check that every path a package names resolves
  inside that package". A partial file is the one case where shared text is known to point at
  nothing: text outside a host marker reaches every package, and four packages told the guide
  to read a page they do not carry. Without the note below, a later edit can put such a
  pointer back and contradict no registered rule. Enforced by
  `tests/test_partial_shipping_has_a_reason.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-430** — (⚠️ **Dated note, 2026-11-17 (#26): a package MUST NOT name a partial source file it drops; the rule above is unchanged.** No file in an assistant's package may hold the path of a source file that ships to some assistants and not to that one: neither the file's path under `source/` nor the path a package that carries it uses. This binds Markdown and scripts alike, a comment included. `hooks/README.md` is the standing case and is held more tightly: it ships to the Claude package only, and no file in any package, the Claude package included, may name it except the page itself. Where shared text needs a fact such a file states, it states the fact. Observed (`production-readiness-audit-2026-11-17`, finding 1): four prose sites and four script comment lines named `hooks/README.md` in all five packages while four layouts dropped it. Enforced by `tests/test_partial_shipping_has_a_reason.py`, which takes the partial files from the shipped sets, requires each to be one a `PARTIAL` entry covers, and searches the bytes of every file in each built package that drops one; it fails when no partial file was checked or a package was not built. It **cannot** find a path put together at run time or a file named by its base name alone, and the limit stated above stands: it does not check that every path a package names resolves inside that package.)

- **PROPOSED AMENDMENT to INV-055 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **Where the hook that re-opens a turn to ask for a missing closing question runs, the bootcamper can turn it off with either of two switches** — in `source/skills/bootcamp-onboarding/ground-rules.md`

  INV-055 requires "a documented opt-out" and does not say where it is documented. The only
  place was `hooks/README.md`, which ships to the Claude package alone, so the Copilot, Kiro,
  ChatGPT and Gemini packages carried the switches in a script and documented them nowhere.
  Without the note below, the item can be dropped from the ground rules, or moved back into a
  file only one package carries, and contradict no registered rule. The issue did not ask for
  this block: it is written because the change ships a test that holds more than INV-055
  says. Enforced by `tests/test_partial_shipping_has_a_reason.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-055** — (⚠️ **Dated note, 2026-11-17 (#26): where the opt-out is documented; the two switches above are unchanged.** Both switches MUST be stated in `skills/bootcamp-onboarding/ground-rules.md`, which every assistant's package carries, in one list item: the `SENZING_BOOTCAMP_DISABLE_STOP_NUDGE` environment variable with the values the script reads as on (`1`, `true`, `yes`, `on`), the top-level key `disable_stop_nudge: true` in `config/bootcamp_preferences.yaml`, and how to turn the nudge back on. That item MUST say it applies where the hook that re-opens a turn runs, because hooks do not run on every assistant, and MUST name no assistant's hook event, because the event has no one name. `hooks/README.md` documents the switches too and ships to the Claude package only, so it cannot be the only place. Enforced by `tests/test_partial_shipping_has_a_reason.py`, which reads the ground rules of all five built packages; it **cannot** establish that a hook reads the switches on any assistant. What the script does with each switch is held by `tests/test_stop_nudge_silence_and_opt_outs.py`.)

- **Commit:** uncommitted

## the-feedback-hook-and-the-packager-report-the-bootcamp-version-as-unknown-on-non-claude-packages

- **Implemented:** 2026-11-17 (issue #31)
- **Files changed:** `source/scripts/feedback-capture.py`, `source/scripts/package_bootcamp.py`,
  `source/skills/bootcamp-onboarding/onboarding-flow.md`,
  `tests/test_scripts_report_the_built_version.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes which file two bundled scripts read the bootcamp's own version from and what one
  sentence says about the steps that resolve it, and asserts nothing about Senzing. No absence
  claim about the Senzing MCP server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** The feedback hook and the packager now report the version of the package they
  ship in, in every assistant's package. This is finding 4 of `dry-run-2026-11-17` and
  finding 22 of `production-readiness-audit-2026-11-17`. Before the change each script read
  only a manifest path. The hook's path exists only in the Claude package, so in the Copilot,
  ChatGPT, Gemini and Kiro packages it told the guide "the plugin version, which is Unknown --
  already resolved". The packager's two paths find no manifest in the ChatGPT and Kiro
  packages, so those archives recorded `"plugin_version": "unknown"`.
  - **The order, in both scripts.** `plugin_version()` reads `bootcamp_version` from the
    `bootcamp_host.json` beside the script first. The build writes that file beside both
    scripts in every package, with the version in `source/bootcamp.json`. Then comes the
    manifest lookup the script already had, then the unresolved value.
  - **When the file gives no version.** It is missing, cannot be read, is not valid JSON, is
    JSON that is not an object, or holds no non-empty string under `bootcamp_version`. None
    of these raises, and the script goes on to its manifest lookup.
  - **Unchanged, as the issue decides.** The hook's manifest lookup is still
    `<script dir>/../.claude-plugin/plugin.json`, and the packager's is still
    `<script dir>/../plugin.json`, then `<script dir>/../.claude-plugin/plugin.json`. The hook
    still reports "Unknown" and the packager "unknown". The `plugin_version` key of
    `PACKAGE_MANIFEST.json` keeps its name. Neither script searches for either file: every
    path is fixed from the script's own location (INV-252).
  - **Decided here, because the issue does not say.** A string that is only whitespace counts
    as no version, and a version is reported without the whitespace around it. The hook
    already treated the manifest's version that way.
  - **The sentence.** `onboarding-flow.md` said every other step resolves the version the same
    way as the WELCOME banner, "so all four report one version". It now says that the recap
    header and the recap's provenance block resolve the manifest the same way as the banner,
    and that the feedback entry reads `bootcamp_version` from `bootcamp_host.json` first and
    resolves the manifest only if that file cannot be read. That is what `feedback.md` already
    told the guide. `feedback.md`, `module-completion.md` and `graduation/SKILL.md` are not
    changed, so no other step changes how it resolves the version.
  - **What a bootcamper sees.** In the Copilot, ChatGPT, Gemini and Kiro packages the hook's
    injected text carries the built version where it said "Unknown". In the ChatGPT and Kiro
    packages `PACKAGE_MANIFEST.json` and the last line of `OPEN_ME_FIRST.md` carry it where
    they said "unknown". Nothing changes in the Claude package. Measured on this branch on
    2026-11-17, by running both scripts from each freshly built package: all ten report the
    version in `source/bootcamp.json`.
  - **Found and not fixed.** A manifest that is valid JSON and not an object makes either
    script exit 1 with an `AttributeError` traceback, because each calls `.get` on what it
    loaded. Reproduced on 2026-11-17 with `[]` as the manifest, on this branch and at
    `257ac1e`. The issue leaves the manifest lookups as they are, so this is not changed. The
    lookup is now reached only when `bootcamp_host.json` gives no version. An issue is drafted
    in the run's handoff and is **not filed**.
  - **Tests.** The new module holds 24 tests. It builds every assistant's package from
    `source/`, taking the assistants from the build's own list (INV-246), and runs both
    scripts from each as their own processes in a scratch project. The hook's injected text,
    and the packager's `PACKAGE_MANIFEST.json`, `OPEN_ME_FIRST.md` and `--dry-run` output, must
    carry the version in `source/bootcamp.json`. The fallback cases run scratch copies of the
    two scripts: fifteen kinds of `bootcamp_host.json` that give no version, each with a
    manifest above the script and without one; the host file against both manifests; each
    script's own manifest lookup; and a `bootcamp_host.json` in six other places and a
    manifest in three, none of which may be read. Those cases hold for every package because
    the code of `plugin_version()` in each built copy is compared with the source's. The text
    checks read the reworded sentence and the three files it names, with whitespace collapsed
    (INV-346).
    Negative controls, each run in a throwaway clone: against `257ac1e` with only the new
    test file, 12 of the 24 tests fail (`FAILED (failures=19)`); with one line of the fix
    changed at a time, each of 18 mutations fails at least one test.
  - **Not observed.** No real assistant ran the hook or the packager. The hook is started
    directly in the tests, and not through an assistant or through the hook adapter that four
    of the packages use, so the tests show what each script writes and not what a guide then
    records. Verified on Linux only, with Python 3.12.3. No run on macOS or on Windows
    happened, so no record is added to any `hosts/<assistant>/checks.json`. The change is
    standard library only and adds no branch on the platform (INV-001).
- **Invariants.** The register is not edited here (INV-365). INV-105 and INV-252 are not
  changed, as the issue decides. The change ships one hard-rule line, in the new test module's
  docstring. `since` does not report it, because `tests/` is not a rule home. The block below
  covers it (INV-309).

- **DEFERRED INVARIANT — awaiting the maintainer's sign-off; NOT minted.** A bundled script that reports the bootcamp's version reads it from the `bootcamp_host.json` beside it first. The rule already shipping, quoted:
    - ⛔ **A bundled script that reports the bootcamp's version reads `bootcamp_version` from the `bootcamp_host.json` beside it before any manifest.** — in `tests/test_scripts_report_the_built_version.py`

  Enforced by `tests/test_scripts_report_the_built_version.py`.

  **Why it is not an existing invariant:** INV-252 says a read of a bundled file resolves
  inside the plugin serving the run and is never found by a search, and gives the order for
  the manifest: the plugin root variable, the skill-relative fallback, then "Unknown". It does
  not name `bootcamp_host.json`, and it does not say which file a script takes the version
  from. INV-105 says the version is shown at the start and recorded in the recap, read from
  the manifest. It says nothing about the feedback hook or the packager. INV-185 is about
  running a bundled script. None of them says that a script reports the built version in every
  assistant's package, and a manifest path alone cannot: the assistants keep their manifests
  in different places.

  Drafted wording follows. The id is written as NNN deliberately: a literal number would cite an
  invariant that does not exist. Mint at the next free id, and read it off `INVARIANTS.md`.

  **INV-NNN** — A bundled script that reports the bootcamp's version MUST read it first from `bootcamp_version` in the `bootcamp_host.json` the build writes beside that script, so that it reports the built version in every assistant's package. Two scripts report it: `feedback-capture.py`, in the text it injects when the bootcamper asks to give feedback, and `package_bootcamp.py`, as `plugin_version` in `PACKAGE_MANIFEST.json` and on the last line of `OPEN_ME_FIRST.md`. When that file gives no version (it is missing, cannot be read, is not valid JSON, or holds no string under `bootcamp_version` that is more than whitespace) the script MUST NOT raise and MUST go on to its own manifest lookup, at paths fixed from the script's location, and then report its unresolved value ("Unknown" from the hook, "unknown" from the packager), never a guess. A script MUST NOT search the filesystem for either file (INV-252). Observed (`dry-run-2026-11-17`, finding 4; `production-readiness-audit-2026-11-17`, finding 22): reading a manifest path alone, the hook told the guide the version was "Unknown" in the Copilot, ChatGPT, Gemini and Kiro packages, and the packager recorded "unknown" in the ChatGPT and Kiro packages. Enforced by `tests/test_scripts_report_the_built_version.py`, which runs both scripts from every built package and the fallback cases on scratch copies; it **cannot** establish that a live assistant runs the hook or what a guide then records, and it was run on Linux only. (Source: `the-feedback-hook-and-the-packager-report-the-bootcamp-version-as-unknown-on-non-claude-packages`, GitHub issue #31, 2026-11-17.)

- **Commit:** uncommitted

## after-graduation-three-hooks-still-treat-the-bootcamp-as-in-progress

- **Implemented:** 2026-11-17 (issue #32)
- **Files changed:** `source/scripts/checkpoint-tick.py`, `source/scripts/precompact-recap.py`,
  `source/scripts/session-end.py`, `source/scripts/module_start_apparatus.py`,
  `source/skills/bootcamp-onboarding/SKILL.md`, `source/hooks/README.md`,
  `tests/test_recap_hooks_stand_down_after_graduation.py` (new),
  `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes what three hook scripts do on a finished bootcamp and what two texts say about
  one helper's callers, and asserts nothing about Senzing. No absence claim about the Senzing
  MCP server is made, so INV-213's `owner-checked:` clause is not owed.
- **Summary:** Once graduation has ended the bootcamp, three hooks no longer keep, fold or
  announce a recap checkpoint, and session end still stops the bootcamp's containers. This is
  finding 8 of `dry-run-2026-11-17` and finding 23 of `production-readiness-audit-2026-11-17`.
  Before the change the three hooks tested only `recap_checkpoint.bootcamp_active()`, which a
  finished project satisfies because its progress file still records a module. A later prompt
  recreated `docs/progress/recap_checkpoint.md` and told the guide to keep it current, and the
  pre-compact hook printed "A Senzing bootcamp is in progress."
  - **Each hook makes its own check.** Each of the three now calls
    `module_start_apparatus.bootcamp_complete()`, as `session-start.py` and
    `failed-run-net.py` do, after its `bootcamp_active()` gate. The flag in either file is
    enough. `recap_checkpoint.bootcamp_active()` is not changed and does not read the flag,
    so its other callers keep their behavior.
  - **`checkpoint-tick.py` stands down whole.** On a finished project it creates no scaffold,
    makes no announcement and gives no missing-record reminder. It writes no file, prints
    nothing on stdout or stderr and exits 0. The check sits after the read of stdin, so the
    hook still drains its payload first.
  - **`precompact-recap.py` neither folds nor prints.** Its `bootcamp_active()` test gains
    `and not module_start_apparatus.bootcamp_complete()`.
  - **`session-end.py` skips only the fold.** The stop stays a statement of the
    `bootcamp_active()` block, outside the completion check. Graduation records completion
    before its own session ends, so a stop gated on completion would leave that session's
    containers running.
  - **What a finished project keeps.** A checkpoint that still holds a narrative is left as it
    is, and so is a scaffold recreated before this fix. No hook removes either one.
  - **No list of callers.** The docstring of `bootcamp_complete()` said the function was
    shared by three named hooks, and step 2 of `bootcamp-onboarding/SKILL.md` named two. Both
    had already left out `failed-run-net.py`. Each now says that every hook that asks whether
    the bootcamp is over uses the one implementation, and names none.
  - **The README rows.** The rows for the three hooks in `source/hooks/README.md` say what
    each does once the bootcamp is complete, and their Gate cells name `bootcamp_complete()`
    after `bootcamp_active()`. The pre-compact row's purpose now also names the reminder the
    hook prints, which the row had left out. Each hook's docstring says the same.
  - **Not changed.** The text under `source/hooks/fallbacks/`, as the issue decides. The
    docstring of `stop-nudge.py` still says the rule is "shared with session start". That is
    a third partial list of callers; the issue names two files, so it is left for a later
    change.
  - **Tests.** The new module holds 33 tests. Each hook runs as its own process in a scratch
    project, with the flag in the progress file, with the flag only in preferences while the
    progress file still records a module, and with both. A finished run must exit 0, write no
    byte to stdout or stderr, and leave every path under the project as it was. Each silent
    case has a twin that is in progress, where the hook still creates the scaffold and
    announces it, folds and reminds, or folds and stops. The stdin case writes a payload
    larger than a pipe buffer and fails if the hook exits before reading it. The container
    cases run the real `session-end.py` in a child process whose CLI lookup and
    `subprocess.run` are replaced first, so they show which commands the hook builds and run
    no container command. The text checks read the callers out of the docstrings and the
    skill, and the README rows against each script's code. Negative controls: in a throwaway
    clone of `726342a` holding only the new test file, 18 of the 33 tests fail
    (`FAILED (failures=31)`). Nine more controls run on every pass, each against a scratch
    copy of the scripts or the text with one earlier line put back.
  - **Not observed.** No real assistant ran these hooks after a graduation, and no container
    runtime ran: the tests show what each script does in a scratch project. Verified on Linux
    only, with Python 3.12.3. No run on macOS, on Windows or on a real assistant happened, so
    no record is added to any `hosts/<assistant>/checks.json`. The change is standard library
    only and adds no branch on the platform (INV-001).
- **Invariants.** Establishes no new invariant (INV-309), and proposes a change to one in
  force. The register is not edited here (INV-365). The change adds no hard-rule line:
  `conformance.py since --since-last-audit` reports none for the range. INV-227's 2026-11-10
  note makes a finished bootcamp a fourth case and says what session start does with one.
  The block below proposes the dated note that would bind these three hooks too. Until the
  maintainer applies it, only the test holds it. INV-101 is unchanged: session end still
  stops the recorded containers while the progress file records a module.

- **PROPOSED AMENDMENT to INV-227 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **Once the bootcamp is complete it folds nothing and still stops the containers.** — in `source/hooks/README.md`
    - ⛔ **Once the bootcamp is complete it folds nothing and prints nothing.** — in `source/hooks/README.md`
    - ⛔ **it then creates no checkpoint and gives no reminder** — in `source/hooks/README.md`

  INV-227's dated note of 2026-11-10 says what a finished bootcamp is and what session start
  does with one. It does not say what the three recap hooks do once the bootcamp is finished,
  and INV-101 says session end stops the recorded containers "when the bootcamp is active"
  without saying whether a finished bootcamp counts. Without the note below, a later edit can
  drop a hook's completion check, or move the stop inside it, and contradict no registered
  rule. Enforced by `tests/test_recap_hooks_stand_down_after_graduation.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-227** — (⚠️ **Dated note, 2026-11-17 (#32): on a finished bootcamp the recap hooks stand down, and session end still stops the bootcamp's containers; the four cases and the one implementation above are unchanged.** Once `module_start_apparatus.bootcamp_complete()` is true, `checkpoint-tick.py` and `precompact-recap.py` MUST write no file, print nothing on stdout or stderr and exit 0: no checkpoint scaffold, no announcement, no missing-record reminder, no fold and no "in progress" reminder. `checkpoint-tick.py` MUST still read its stdin to the end first. `session-end.py` MUST skip the fold and nothing else: it MUST still stop each container the progress file records, under `bootcamp_active()`, because graduation records completion before its own session ends (INV-101). Each of the three hooks makes the check itself, after its `bootcamp_active()` gate; `recap_checkpoint.bootcamp_active()` MUST NOT read the flag, and keeps its meaning. A checkpoint that still holds a narrative, and a scaffold already there, are left as they are: no hook removes or folds either. `module_start_apparatus.py` and `bootcamp-onboarding/SKILL.md` step 2 MUST NOT list the callers of `bootcamp_complete()`; each points at the one implementation. Observed (`dry-run-2026-11-17`, finding 8; `production-readiness-audit-2026-11-17`, finding 23): with the flag set, a later prompt recreated the checkpoint scaffold and told the guide to keep it current, and the pre-compact hook printed "A Senzing bootcamp is in progress." The rules above still bind. Enforced by `tests/test_recap_hooks_stand_down_after_graduation.py`, which runs each hook against the flag in the progress file, only in the preferences and in both, each with a twin that is in progress, and with negative controls; it **cannot** establish that a live assistant fires these hooks after graduation or what a real container runtime does, and it was run on Linux only.)

- **Commit:** uncommitted

## powershell-writes-to-a-temp-directory-pass-the-write-gate-on-copilot

- **Implemented:** 2026-11-17 (issue #33)
- **Files changed:** `hosts/_shared/hook_adapter.py`, `hosts/copilot/host.json`,
  `source/hooks/README.md`, `source/scripts/write-gate.py`,
  `tests/test_write_gate_powershell.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it changes how the write gate reads a shell command and which tool an assistant's profile
  declares as PowerShell, and asserts nothing about Senzing. The URL in the new tests,
  `https://mcp.senzing.com/examples/x.py`, is the sample string `tests/test_write_gate_bash.py`
  already uses as a command argument; nothing is fetched and nothing is claimed about what the
  server serves there. No absence claim about the Senzing MCP server is made, so INV-213's
  `owner-checked:` clause is not owed.
- **Summary:** A command sent through a shell tool that an assistant's profile declares as
  PowerShell is now read by PowerShell's rules, and the write gate blocks its top-level output
  targets in system temp or Downloads outside the project, as it already did for a POSIX
  command. This is finding 9 of `dry-run-2026-11-17`. Before the change, the two reported
  commands, `python src\load\load.py > $env:TEMP\o.txt` and `echo hi > C:\Windows\Temp\o.txt`,
  were allowed through the Copilot adapter's `powershell` tool.
  - **The dialect travels with the call.** `hosts/copilot/host.json` gains
    `options.adapter.shell_dialects`, which maps the tool name `powershell` to the dialect
    `powershell`. The build already copies `options.adapter` whole into `bootcamp_host.json`,
    so no build tool changed. `hosts/_shared/hook_adapter.py` looks the tool up there, exactly
    and then lower-cased, and adds a top-level `"shell_dialect": "powershell"` to the canonical
    payload of a shell call from that tool. `tool_name` stays `Bash` and `tool_input` is
    unchanged. A tool the profile does not name gets no field, and no other assistant's
    profile declares one.
  - **One pipeline, two readers.** The second half of `bash_targets()` (the loop over
    redirects and simple commands) is now `token_targets()`, with its body unchanged. A POSIX
    command reaches it through `shlex` as before. A PowerShell command reaches it through the
    new `powershell_tokens()`, which produces the same tokens by PowerShell's rules: a
    backslash is a literal character, the backtick is the escape, a single-quoted string is
    literal, and a double-quoted string is one word whose variables still count. A stream in
    front of a redirect belongs to the operator, `2>&1` and `*>&1` name no file, and a
    here-string's body and a comment are dropped.
  - **The writers.** `POWERSHELL_WRITERS` is the Bash table plus the cmdlets and aliases of
    the issue's table: `Out-File`; `Set-Content` and `Add-Content` (`sc`, `ac`);
    `Tee-Object` (`tee`); `Copy-Item` and `Move-Item` (`cp`, `copy`, `cpi`, `mv`, `move`,
    `mi`); `Invoke-WebRequest` (`iwr`, `curl`, `wget`). Command and parameter names match in
    any case, and `-Name:value` is read. `tee`, `curl` and `wget` are read both as the cmdlet
    alias and as the program, so `curl.exe -o` and `wget -O` are read as on Bash. `cp` and
    `mv` are read as the cmdlet aliases only under PowerShell, because the getopt reading
    takes the last positional and would deny `cp -Destination src\a.txt -Path $env:TEMP\a.txt`.
    A POSIX command never sees the new names.
  - **The locations.** System temp is also `$env:TEMP`, `$env:TMP` and `$env:TMPDIR`, in any
    case, with or without braces. Downloads is reached through `$HOME`, `$env:USERPROFILE`,
    `$env:HOME` or `~`. The directories `location()` lists are unchanged, and `location()`
    itself is untouched, so a target inside the project is still allowed before any temp list
    is consulted. `$null` resolves to no temp location and is allowed.
  - **What is still allowed.** A command with an unbalanced quote, as on Bash: the gate does
    not fail closed on a command it cannot split. A quoted payload such as
    `powershell -Command '…'`, a temp path that is a source, and a target outside the project
    that is not temp or Downloads. A variable other than those named, an expression and an
    abbreviated parameter name are not evaluated. The secret check does not run on a shell
    command, as before.
  - **Where the change goes beyond the issue.** The issue lists `;`, a newline, `|`, `&&` and
    `||` as ending a PowerShell command. The gate also ends one at `&`, `(`, `)`, `{` and
    `}`, so a write inside `if (…) { … }` is read and the words of a source expression in
    parentheses are not counted as positionals. To do that the shared `COMMAND_ENDS` set
    gains `{` and `}`. The POSIX reader never produces either as an operator, so the Bash
    reading is unchanged: every case in `tests/test_write_gate_bash.py` passes with the file
    untouched.
  - **The gate says what it checks.** The gate's docstring and the write-gate row of
    `source/hooks/README.md` name the PowerShell forms. `source/hooks/fallbacks/write-gate.md`
    is not changed: the issue does not list it, and it states the rule for an assistant with
    no hook, with the Bash forms as examples.
  - **Approach.** Two implementations were raced and judged before this run applied one. The
    winner, B, normalizes a PowerShell command into the gate's existing token pipeline; the
    other, A, added a separate PowerShell reader beside the POSIX path. B's patch was made
    against `e90d05a` and applied to `8490ad2` with no conflict. #25 and #47 changed other
    lines of `write-gate.py`, and `powershell_command()` reads the same decoded payload
    `bash_command()` does.
  - **Tests.** The new module holds 40 tests. Each command goes through the Copilot package
    as the build writes it (its `hook_adapter.py`, its `bootcamp_host.json`, its
    `write-gate.py`), in the `preToolUse` payload captured from Copilot CLI 1.0.111 for its
    `bash` tool, with the tool name changed to `powershell`. A denial is compared with the
    whole of `LOC_MSG`, read from the gate's source. The tests send both reported commands;
    each redirect, spaced and attached; 59 generated forms of the cmdlets and aliases into
    temp and into Downloads, and the same 59 inside the project as the negative control; 24
    temp and Downloads spellings, each unquoted and in two double-quoted forms; the in-project
    writes, with a project that lives under the temp directory; and each allowed case with a
    denied control beside it. The Bash test's blocked forms are replayed through Copilot's
    `bash` tool, and a canonical payload with no dialect, a null one and an unknown one is
    read as POSIX. Negative control, run in a throwaway clone of `8490ad2` holding only the
    new test file: `FAILED (failures=297, errors=4)`, in 33 of the 40 tests. The seven that
    pass there pin unchanged behavior.
  - **Not observed.** No payload from Copilot on Windows has been seen. The tool name
    `powershell` comes from `hosts/copilot/host.json`, and the payload shape is the Linux
    `bash` capture with the name changed. No PowerShell ran: the tests show what the gate
    decides for a command string, not what a live PowerShell writes. Verified on Linux only,
    with Python 3.12.3. No run on macOS, on Windows or on a real assistant happened, so no
    record is added to `hosts/copilot/checks.json`. The change is standard library only, runs
    no shell and adds no branch on the platform (INV-001).
- **Invariants.** Establishes no new invariant (INV-309), and proposes a change to one in
  force. The register is not edited here (INV-365). The change adds no hard-rule line:
  `conformance.py since --since-last-audit` reports none for the range. INV-200's 2026-11-06
  note lists what the gate reads on a Bash command, and the block below proposes the dated
  note that would bind the PowerShell reading. Until the maintainer applies it, only the test
  holds it.

- **PROPOSED AMENDMENT to INV-200 — awaiting the maintainer's sign-off; NOT applied.**
    - ⛔ **A command sent by a shell tool declared as PowerShell is read by PowerShell's rules and held to the same rule** — in `source/hooks/README.md`

  INV-200's dated note of 2026-11-06 says what the gate blocks and allows on a Bash command,
  and names only POSIX forms. The gate now also reads a PowerShell command, by other rules and
  with other writers. Without the note below, the register does not say which commands get
  that reading, what is blocked on one, or that a payload naming no dialect is read as POSIX
  shell, so a later edit can drop a PowerShell form or read every command both ways and
  contradict no registered rule. Enforced by `tests/test_write_gate_powershell.py`.

  Drafted wording follows, under the registered id. A new rule's id would be
  written as NNN deliberately; for the next free one, read it off `INVARIANTS.md`.

  **INV-200** — (⚠️ **Dated note, 2026-11-17 (#33): a command from a shell tool declared as PowerShell is read by PowerShell's rules; the Bash reading and the Write/Edit boundary above are unchanged.** An assistant's profile names which of its shell tools is PowerShell (`options.adapter.shell_dialects` in `hosts/<assistant>/host.json`), and the hook adapter passes that on as `shell_dialect` in the canonical payload; `tool_name` stays `Bash`, and a payload that names no dialect MUST be read as POSIX shell. On a PowerShell command the gate MUST block, with the same temp/Downloads message, a top-level output target that resolves to system temp or Downloads outside the project, in each command the line holds: a `>` or `>>` redirect, alone or with a stream in front (`2>`, `2>>`, `*>`, `*>>`); `Out-File`; `Set-Content` and `Add-Content` (`sc`, `ac`); `Tee-Object` (`tee`); the destination of `Copy-Item` and `Move-Item` (`cp`, `copy`, `cpi`, `mv`, `move`, `mi`); and `Invoke-WebRequest -OutFile` (`iwr`, `curl`, `wget`), with `curl.exe -o` and `wget -O` read as on Bash. Command and parameter names match in any case. System temp is also `$env:TEMP`, `$env:TMP` and `$env:TMPDIR`, in any case, with or without braces; Downloads is reached through `$HOME`, `$env:USERPROFILE`, `$env:HOME` or `~`. It MUST allow a target inside the project first, as above, and MUST allow `$null`, a stream merge such as `2>&1`, a temp path that is a source, a non-temp target outside the project, a quoted payload such as `powershell -Command '…'`, a here-string's body, and a command it cannot split. A variable other than those named, an expression and an abbreviated parameter name are not evaluated, and the secret check (INV-109) does not run. Enforced by `tests/test_write_gate_powershell.py`, which sends each command through the built Copilot adapter and **cannot** establish what a live PowerShell writes or what payload Copilot sends on Windows: that payload has not been observed, and no run in `hosts/copilot/checks.json` is on Windows.)

- **Commit:** uncommitted

## three-generator-and-write-gate-messages-mislead

- **Implemented:** 2026-11-17 (issue #47)
- **Files changed:** `source/scripts/generate_recap_pdf.py`, `source/scripts/write-gate.py`,
  `tests/test_certificate_name_source.py`, `tests/test_recap_pdf_guard.py`,
  `tests/test_write_gate.py`, `specs/IMPLEMENTED.md` (this entry)
- **MCP re-check:** n/a (no Senzing fact). Re-confirmed on 2026-11-17 against the change itself:
  it rewords one warning, adds one sentence to one block message and adds space under one
  title, and asserts nothing about Senzing. The license-payload pattern the write gate matches
  is unchanged, byte for byte. No absence claim about the Senzing MCP server is made, so
  INV-213's `owner-checked:` clause is not owed.
- **Summary:** Three outputs that pointed the reader the wrong way now say what is true and
  name a next step that works. They are findings 10, 15 and 16 of `dry-run-2026-11-17`.
  - **The unprintable-name warning.** `generate_recap_pdf.py` said the name was "in" the
    recap and said to record it as a `**Bootcamper:**` line, whichever file the name came
    from. The certificate prints the preferences `name:` first and the recap's name only when
    preferences has none, so only the preferences file changes what prints. The warning now
    names the file the name was read from: the `--preferences` path when preferences has a
    name, the input path when it does not. In the first case it says to change the top-level
    `name:` in the preferences file, and in the second to record the name as the top-level
    `name:` there. It still says to ask the bootcamper for the name to print (INV-113). The
    missing-name warning and the NOTE about the two files disagreeing are unchanged.
  - **The fallback's cover.** `render_with_stdlib` advances every text line 14 pt whatever
    its size, so the 14 pt subtitle sat 14 pt under the 22 pt title and touched it. One gap
    token of 12.4 pt now follows the title, which puts the two baselines 26.4 pt apart, 1.2
    times the title size. Measured on one recap before and after the change: page 1 holds the
    same 39 lines, the title is at the same position, and every later line is 12.4 pt lower.
    No other pair of lines changed its distance. The fpdf2 renderer is unchanged.
  - **The write gate's message.** The gate judges the whole payload, so an edit whose
    replaced text holds a secret and whose new text does not is blocked, and was told "Use
    environment variables instead." It is still blocked. Its message is now `SECRET_MSG`
    followed by: "The possible secret is in the text being replaced, not in the new text. To
    take it out of the file, write the whole file again without the secret." The addition is
    made only when the payload parses, its tool name is `Edit`, and `tool_input.new_string`
    is text the secret pattern does not match. A secret in both texts, a secret only in the
    new text, a write, an edit with no `new_string`, and a payload that does not parse all
    get `SECRET_MSG` alone, as before. The hook adapter gives the gate every assistant's
    edit as `Edit` with its new text in `new_string`, so the rule has no per-assistant code,
    and the added sentence names no assistant and no tool.
  - **The inline pattern.** The gate's `re.search(` call moved into a function,
    `holds_secret`, so the same pattern can judge the new text. Its three raw strings and the
    name `data` are as they were, and `tests/test_secret_patterns_are_shared.py` still reads
    the call and finds it identical to `secret_patterns.py`.
  - **What the gate blocks is unchanged.** Exit codes are the same for every payload. One
    blocked case has a longer stderr message.
  - **A limit of the gate's rule, kept as the issue states it.** The addition is decided from
    the new text alone, because the name of the key holding the replaced text differs between
    assistants. An edit whose secret-shaped text is in neither text, in its file path for
    instance, is also told the secret is in the text being replaced.
  - **Tests.** 21 new tests in three existing modules. `tests/test_write_gate.py` gains 12:
    the addition for each of the three secret classes, each case that keeps `SECRET_MSG`
    alone, that the next step named is a write the gate allows, and every edit tool the four
    adapter-run assistants declare, sent through the adapter. `SECRET_MSG` is read out of the
    gate's source, so the tests compare against the gate's own text. The secrets are
    synthetic, built from the shapes the module already used.
    `tests/test_certificate_name_source.py` gains 5: both name sources, the paths given on
    the command line, the absence of the `**Bootcamper:**` instruction, and a control.
    `tests/test_recap_pdf_guard.py` gains 4: they render with `render_with_stdlib`, loaded
    from `source/`, and read the font size and baseline of each page-1 line from the page
    content. Negative control: with the two scripts as they were at `a8b1e5c` and the new
    tests in place, 8 of the 21 fail, and the 13 that pin unchanged behavior pass.
  - **Verified on Linux only**, with Python 3.12.3. No run on macOS or Windows happened and
    no run on a real assistant happened, so no run is added to any
    `hosts/<assistant>/checks.json`. The change adds no branch on the platform (INV-001): the
    paths in the warning are the ones the command line gave, and the tests build the paths
    they expect with `os.path.join`. What the adapter-driven test cannot establish is that an
    assistant's own edit tool sends its new text under a key the adapter knows; it starts from
    one argument shape, not from a captured payload.
- **Invariants.** Establishes no new invariant. The register is not edited here (INV-365).
  The change adds no hard-rule line. Three messages changed; none of them is a rule the
  bootcamp binds later work to.
  - **INV-109, for the maintainer to confirm.** INV-109 says the gate blocks "with
    `SECRET_MSG`". For one blocked case the message is now `SECRET_MSG` followed by one more
    sentence. The issue's decision table rules that INV-109 is untouched, so no
    `PROPOSED AMENDMENT` block is written here. If "with `SECRET_MSG`" is read as "with
    `SECRET_MSG` and nothing after it", INV-109 is owed a dated note, and that is the
    maintainer's call through `/review-invariants`.
- **Commit:** uncommitted

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
    - ⛔ **(INV-252) Read the files from there.** — in `hosts/kiro/host.json`

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
