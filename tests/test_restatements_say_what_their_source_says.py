"""Restated lists, citations and pointers say what their source says (#45).

Seven places in shipped text restated something another place owns, and had drifted from it
(findings 15, 20, 21, 23, 28 and 29 of `production-readiness-audit-2026-11-17`). This file
holds the guards for six of them. The seventh, Module 4's data hierarchy, is held by
`tests/test_gate_options_have_handling_steps.py`, which already read its secondary offer.

What must hold:

- ⛔ **A module close that lists the steps of Module Completion names its Step 0 first, then progress, recap and summary, in the order `module-completion.md` fixes.**
  The order is read from the opening of `module-completion.md`, not copied here. A close is
  any passage under `source/skills/` that runs the "standard **Module Completion** process",
  read from that phrase to the module's transition question. A passage that names the process
  and lists fewer than two of its steps is a pointer, and a pointer is not checked. Modules
  1, 2 and 5 listed the steps without Step 0 or with the summary before the recap; Modules 3
  and 3b numbered steps 1 to 4 and left Step 0 out.
- **The sentence above the stage table cites both invariants whose subjects it states.** "One
  row per stage" is INV-140 and "one level per row" is INV-141.
- **The list of retired nudge rules names only invariants the register lists as fully
  superseded.** The register is `specs/INVARIANTS.md`; its index gives each group's "Fully
  superseded" list. INV-141 was listed as retired while in force.
- **The generated-scenario marker's reader list names every reader.** A reader is a file
  under `source/skills/` that contains the marker and is neither Module 1's writer nor
  `graduation/SKILL.md`, which holds the list. The list names readers by module and phase,
  and the name is read from the file's path: `module-06-…/phaseC-….md` is "Module 6 Phase C",
  and a module's `SKILL.md` is the module alone. The docstring of
  `tests/test_generated_scenario_marker_drop_is_exempt.py` repeats the list and must agree.
- **The checkpoint fallback names the rule's owner.** `source/hooks/fallbacks/checkpoint-tick.md`
  points at the "In-progress recap checkpoint" rule in `ground-rules.md`, and that rule is
  there under that name.
- **The packager's comment names the test that holds the pin.** The comment above
  `DATABASE_BACKUP_ROOT` in `source/scripts/package_bootcamp.py` names a test file that
  exists and reads that constant.
- ⛔ **Module 5 writes one per-source mapping document, `docs/mapping/{source_name}_mapper.md`, and its structure has a `## How to run` section.**
  No file under `source/` names a `docs/mapping/mapping_…` document, and step 18 names no
  mapping document but `_mapper.md` beside the transformation lineage. The dropped document
  held one thing `_mapper.md` lacked: how to run the transformation.

How the text is read. Prose is matched with whitespace collapsed, so a sentence that wraps is
still one sentence (INV-346). Two reads are by line on purpose, and each says why where it is
made. Sites are found by scanning, not listed (INV-246): the closes, the marker's readers and
the files under `source/`.

⚠️ **What these checks cannot establish.** That a live guide runs Step 0 at a module close,
recommends free raw data before synthesized data, or writes a `## How to run` section: only a
run shows that. They read `source/`, which every assistant's package is built from, and not a
built package. The marker check finds a reader by the marker's text, so a step that reads
`docs/business_problem.md` for it without naming it is not found. The close check takes the
first mention of each step in a passage. A `docs/mapping/mapping_[name].md` left in a project
by an earlier run is neither read nor removed by anything here.

Every check fails when it finds nothing to read, and each has a negative control that runs on
every pass (INV-265).

Standard library only (INV-108). Paths are built with `pathlib` and files are read as UTF-8,
so the module does not depend on the platform (INV-001).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "source"
SKILLS = SOURCE / "skills"
ONBOARDING = SKILLS / "bootcamp-onboarding"
MODULE_COMPLETION = ONBOARDING / "module-completion.md"
GROUND_RULES = ONBOARDING / "ground-rules.md"
GRADUATION = SKILLS / "graduation" / "SKILL.md"
MODULE_5_PHASE_2 = SKILLS / "module-05-data-quality-mapping" / "phase2-data-mapping.md"
CHECKPOINT_FALLBACK = SOURCE / "hooks" / "fallbacks" / "checkpoint-tick.md"
PACKAGER = SOURCE / "scripts" / "package_bootcamp.py"
REGISTER = REPO_ROOT / "specs" / "INVARIANTS.md"
MARKER_TEST = REPO_ROOT / "tests" / "test_generated_scenario_marker_drop_is_exempt.py"


def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    """``text`` with whitespace collapsed, so a phrase that wraps is one phrase (INV-346)."""
    return re.sub(r"\s+", " ", text).strip()


# --- Item 1: module closes -----------------------------------------------------------------

#: Each step of Module Completion a close can list: its name here, how a close or the opening
#: of `module-completion.md` names it, and how that file's `## Step N:` heading names it.
STEPS = (
    ("its Step 0 checks", re.compile(r"\bStep 0\b"),
     re.compile(r"required step that never ran", re.I)),
    ("update progress", re.compile(r"\bupdate progress\b", re.I),
     re.compile(r"progress state", re.I)),
    ("append the recap section",
     re.compile(r"\bappend\b[^.;:()]{0,60}?\brecap section\b", re.I),
     re.compile(r"recap section", re.I)),
    ("present the end-of-module summary",
     re.compile(r"\bpresent\b[^.;:()]{0,60}?\bend-of-module summary\b", re.I),
     re.compile(r"end-of-module summary", re.I)),
)
#: The phrase every close uses to run the process. `\s+` because the phrase may wrap.
CLOSE_LEAD = re.compile(r"standard\s+\*\*Module\s+Completion\*\*\s+process")
#: Where a close passage ends: the module's transition question, or the next heading.
PASSAGE_END = re.compile(r"(?m)^(?:👉|#{1,6} )")
#: A `## Step N: title` heading of `module-completion.md`. A heading is one line by definition.
STEP_HEADING = re.compile(r"(?m)^## Step (\d+): (.+)$")
#: Entity Resolution Concepts runs the process step by step and departs from it on purpose, so
#: its close is not one of these (out of scope in #45).
NOT_A_STANDARD_CLOSE = "module-00-"


def fixed_order(completion_text):
    """Module Completion's steps in the order its opening fixes: ``[(name, pattern), …]``."""
    opening = flat(completion_text.split("\n## ", 1)[0])
    found = []
    for name, pattern, _ in STEPS:
        m = pattern.search(opening)
        if m is None:
            raise AssertionError("the opening of module-completion.md no longer names %r" % name)
        found.append((m.start(), name, pattern))
    return [(name, pattern) for _, name, pattern in sorted(found)]


def heading_numbers(completion_text, order):
    """The `## Step N:` number of each step in ``order``, or None where no heading names it."""
    headings = [(int(n), title) for n, title in STEP_HEADING.findall(completion_text)]
    by_name = {name: heading for name, _, heading in STEPS}
    return [next((n for n, title in headings if by_name[name].search(title)), None)
            for name, _ in order]


def close_passages(text):
    """``(line, passage)`` for each passage of ``text`` that runs Module Completion.

    A passage runs from the phrase to the next line that opens with the transition question's
    👉 or with a heading, with whitespace collapsed.
    """
    out = []
    for m in CLOSE_LEAD.finditer(text):
        end = PASSAGE_END.search(text, m.end())
        stop = end.start() if end else len(text)
        out.append((text.count("\n", 0, m.start()) + 1, flat(text[m.start():stop])))
    return out


def lists_the_steps(passage):
    """True when ``passage`` lists the process's steps, and is not just a pointer at it."""
    return sum(1 for _, pattern, _ in STEPS[1:] if pattern.search(passage)) >= 2


def close_problems(passage, order):
    """What a close that lists the steps gets wrong against ``order``."""
    problems, last, last_name = [], -1, None
    for name, pattern in order:
        m = pattern.search(passage)
        if m is None:
            problems.append("does not name %s" % name)
        elif m.start() < last:
            problems.append("names %s before %s" % (name, last_name))
        else:
            last, last_name = m.start(), name
    return problems


def listing_closes():
    """``(relative path, line, passage)`` for every close under `source/skills/` that lists."""
    out = []
    for path in sorted(SKILLS.rglob("*.md")):
        if path == MODULE_COMPLETION:
            continue
        for line, passage in close_passages(read(path)):
            if lists_the_steps(passage):
                out.append((path.relative_to(SKILLS).as_posix(), line, passage))
    return out


class ModuleClosesFollowModuleCompletion(unittest.TestCase):
    """Item 1: every close that lists the steps lists them as `module-completion.md` does."""

    @classmethod
    def setUpClass(cls):
        cls.completion = read(MODULE_COMPLETION)
        cls.order = fixed_order(cls.completion)
        cls.closes = listing_closes()

    def _close(self, relative):
        text = read(SKILLS / relative)
        passages = close_passages(text)
        self.assertEqual(1, len(passages), "%s no longer has one close" % relative)
        return text, passages[0][1]

    def test_the_order_is_read_from_module_completion(self):
        self.assertEqual([name for name, _, _ in STEPS], [name for name, _ in self.order],
                         "module-completion.md's opening fixes another order; the closes are "
                         "checked against the order read here, and this list only says what "
                         "it was on 2026-11-17")

    def test_the_sections_run_in_the_order_the_opening_fixes(self):
        numbers = heading_numbers(self.completion, self.order)
        self.assertNotIn(None, numbers, "a step of the opening has no `## Step N:` heading")
        self.assertEqual(sorted(numbers), numbers,
                         "module-completion.md's opening and its headings give two orders")
        self.assertEqual(0, numbers[0], "the first step is not Step 0")

    def test_every_content_module_has_a_close_that_lists_the_steps(self):
        """Anti-vacuity (INV-265): the scan finds a close in every module directory but one."""
        modules = sorted(p.name for p in SKILLS.iterdir()
                         if p.is_dir() and p.name.startswith("module-")
                         and not p.name.startswith(NOT_A_STANDARD_CLOSE))
        self.assertGreaterEqual(len(modules), 8, modules)
        found = sorted({relative.split("/")[0] for relative, _, _ in self.closes})
        self.assertEqual(modules, found)

    def test_every_close_names_step_0_first_and_keeps_the_order(self):
        problems = ["%s:%d %s" % (relative, line, problem)
                    for relative, line, passage in self.closes
                    for problem in close_problems(passage, self.order)]
        self.assertEqual([], problems)

    def test_a_close_without_step_0_fails(self):
        for relative in ("module-01-business-problem/phase2-document-confirm.md",
                         "module-02-sdk-setup/SKILL.md"):
            with self.subTest(close=relative):
                text, passage = self._close(relative)
                self.assertEqual([], close_problems(passage, self.order))
                mutant = text.replace("(its Step 0 checks, update progress,",
                                      "(update progress,", 1)
                self.assertNotEqual(text, mutant, "the mutation no longer applies")
                passage = close_passages(mutant)[0][1]
                self.assertTrue(lists_the_steps(passage))
                self.assertEqual(["does not name its Step 0 checks"],
                                 close_problems(passage, self.order))

    def test_a_numbered_close_without_step_0_fails(self):
        for relative in ("module-03-system-verification/phase2-report-close.md",
                         "module-03b-truthset-visualization/phase2-close.md"):
            with self.subTest(close=relative):
                text, passage = self._close(relative)
                self.assertEqual([], close_problems(passage, self.order))
                self.assertLess(passage.index("Step 0"), passage.index("1. **Update progress"),
                                "Step 0 is not named before item 1")
                mutant = re.sub(r"Run\s+Module\s+Completion's\s+Step\s+0\s+checks\s+first,\s+then:",
                                "Then:", text, count=1)
                self.assertNotEqual(text, mutant, "the mutation no longer applies")
                self.assertEqual(["does not name its Step 0 checks"],
                                 close_problems(close_passages(mutant)[0][1], self.order))

    def test_a_summary_before_the_recap_fails(self):
        """Module 5's close as it shipped: Step 0, the summary, then the recap."""
        relative = "module-05-data-quality-mapping/phase2-data-mapping.md"
        text, passage = self._close(relative)
        self.assertEqual([], close_problems(passage, self.order))
        for citation in ("(INV-085)", "(INV-032)", "(INV-079)"):
            self.assertIn(citation, passage, "Module 5's close lost a citation")
        self.assertLess(passage.index("(INV-085)"), passage.index("(INV-032)"))
        self.assertLess(passage.index("(INV-032)"), passage.index("(INV-079)"))
        shipped = ("run its Step 0 checks, present the end-of-module summary (INV-032), append "
                   "the name-based Module 5 recap section to `docs/bootcamp_recap.md` "
                   "(INV-085), show the")
        problems = close_problems(flat("standard **Module Completion** process in "
                                       "`module-completion.md`: " + shipped), self.order)
        self.assertEqual(["does not name update progress",
                          "names present the end-of-module summary before append the recap "
                          "section"], problems)

    def test_the_closes_follow_a_changed_order(self):
        """The order comes from `module-completion.md`: change it there and every close fails."""
        recap = re.search(r"(?m)^2\. Append this module's recap section", self.completion)
        summary = re.search(r"(?m)^3\. Present the end-of-module summary", self.completion)
        self.assertTrue(recap and summary, "the opening's numbered list moved")
        mutant = (self.completion[:recap.start()] + "2. Present the end-of-module summary.\n"
                  "3. Append this module's recap section.\n\n"
                  + self.completion[self.completion.index("\n\n", summary.start()):])
        order = fixed_order(mutant)
        self.assertNotEqual([name for name, _ in self.order], [name for name, _ in order])
        self.assertGreaterEqual(len(self.closes), 8)
        for relative, _, passage in self.closes:
            with self.subTest(close=relative):
                self.assertNotEqual([], close_problems(passage, order))

    def test_a_rewrap_still_passes(self):
        """INV-346: the phrase and the list may wrap anywhere."""
        relative = "module-04-data-collection/SKILL.md"
        text, _ = self._close(relative)
        mutant = text.replace("Run the standard **Module Completion** process",
                              "Run the standard **Module\nCompletion** process", 1)
        mutant = mutant.replace("(its Step 0 checks, update progress,",
                                "(its Step\n0 checks, update\nprogress,", 1)
        self.assertNotEqual(text, mutant, "the re-wrap no longer applies")
        passages = close_passages(mutant)
        self.assertEqual(1, len(passages))
        self.assertTrue(lists_the_steps(passages[0][1]))
        self.assertEqual([], close_problems(passages[0][1], self.order))

    def test_a_pointer_that_lists_no_step_is_not_a_close(self):
        self.assertFalse(lists_the_steps(
            "standard **Module Completion** process in `module-completion.md`, then ask the "
            "single transition question."))


# --- Item 3: the two citations -------------------------------------------------------------

INV = re.compile(r"INV-\d{3}")
#: The sentence above the stage table, up to its citation, with the table's header after it.
STAGE_SENTENCE = re.compile(
    r"One row per stage\b[^()]*\((?P<ids>[^()]*)\)(?=[^|]{0,200}\| Stage \| Effort \|)")
#: The list of retired nudge rules: the first parenthesis after the sentence that retires them.
RETIRED_LIST = re.compile(r"The earlier nudge is retired\b[^()]*\((?P<ids>[^()]*)\)")
#: One "Fully superseded" list in the register's index.
FULLY_SUPERSEDED = re.compile(r"^\s*\*Fully superseded\b[^*]*\*(?P<ids>.*)$")
#: The subject each cited invariant states, as the register words it.
SUBJECTS = {"INV-140": "exactly one row", "INV-141": "exactly one effort level"}


def stage_citation_problems(ground_rules):
    m = STAGE_SENTENCE.search(flat(ground_rules))
    if m is None:
        return ["the sentence above the stage table moved"]
    cited = set(INV.findall(m.group("ids")))
    return ["the sentence above the stage table does not cite %s" % inv
            for inv in sorted(SUBJECTS) if inv not in cited]


def fully_superseded(register):
    """Every invariant the register's index lists as fully superseded."""
    ids = set()
    # Line-scoped by design (#45): the register's index writes each "Fully superseded" list on
    # one line of its own, and the next line is another list.
    for line in register.splitlines():
        m = FULLY_SUPERSEDED.match(line)
        if m:
            ids.update(INV.findall(m.group("ids")))
    return ids


def retired_list_problems(ground_rules, superseded):
    m = RETIRED_LIST.search(flat(ground_rules))
    if m is None:
        return ["the list of retired nudge rules moved"]
    retired = INV.findall(m.group("ids"))
    if not retired:
        return ["the list of retired nudge rules names no invariant"]
    return ["%s is listed as retired, and the register does not list it as fully superseded"
            % inv for inv in retired if inv not in superseded]


class TheTwoCitationsNameWhatTheyState(unittest.TestCase):
    """Item 3: the stage table's sentence and the list of retired nudge rules."""

    @classmethod
    def setUpClass(cls):
        cls.ground_rules = read(GROUND_RULES)
        cls.register = read(REGISTER)
        cls.superseded = fully_superseded(cls.register)

    def test_the_register_lists_are_read(self):
        """Anti-vacuity (INV-265): an empty list would clear nothing, and say so."""
        self.assertGreaterEqual(len(self.superseded), 10, sorted(self.superseded))
        self.assertIn("INV-063", self.superseded)

    def test_the_register_states_the_two_subjects(self):
        for inv, subject in SUBJECTS.items():
            entry = re.search(r"(?m)^- \*\*%s\*\* — .*$" % inv, self.register)
            self.assertIsNotNone(entry, "%s is not in the register" % inv)
            self.assertIn(subject, entry.group(0))
            self.assertNotIn(inv, self.superseded, "%s is no longer in force" % inv)

    def test_the_sentence_above_the_stage_table_cites_both(self):
        self.assertEqual([], stage_citation_problems(self.ground_rules))

    def test_the_retired_list_names_only_fully_superseded_invariants(self):
        self.assertEqual([], retired_list_problems(self.ground_rules, self.superseded))

    def test_negative_controls(self):
        t = self.ground_rules
        both = "row (INV-140, INV-141). This table"
        self.assertIn(both, t)
        for name, mutant in {
            "INV-141 is not cited": t.replace(both, "row (INV-140). This table", 1),
            "INV-140 is not cited": t.replace(both, "row (INV-141). This table", 1),
            "the sentence cites nothing": t.replace(both, "row. This table", 1),
        }.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(t, mutant, "the mutation no longer applies")
                self.assertNotEqual([], stage_citation_problems(mutant))
        in_force = t.replace("INV-138, INV-139). Surface,",
                             "INV-138, INV-139, INV-141). Surface,", 1)
        self.assertNotEqual(t, in_force, "the mutation no longer applies")
        self.assertEqual(
            ["INV-141 is listed as retired, and the register does not list it as fully "
             "superseded"], retired_list_problems(in_force, self.superseded))
        self.assertNotEqual([], retired_list_problems(t, set()))
        emptied = re.sub(r"\(INV-063,[^()]*\)\. Surface,", "(none). Surface,", flat(t), count=1)
        self.assertNotEqual(flat(t), emptied, "the mutation no longer applies")
        self.assertNotEqual([], retired_list_problems(emptied, self.superseded))

    def test_a_rewrap_still_passes(self):
        """INV-346: both citations may wrap."""
        t = self.ground_rules
        mutant = t.replace("row (INV-140, INV-141). This table",
                           "row (INV-140,\n  INV-141). This\n  table", 1)
        mutant = mutant.replace("The earlier nudge is retired",
                                "The earlier\n  nudge is retired", 1)
        self.assertNotEqual(t, mutant, "the re-wrap no longer applies")
        self.assertEqual([], stage_citation_problems(mutant))
        self.assertEqual([], retired_list_problems(mutant, self.superseded))


# --- Item 4: the marker's readers ----------------------------------------------------------

#: The marker as a reader names it. Module 1 writes it as a blockquote line, `> ` first; a
#: reader may name it without that prefix, so the scan does, and it reads each file with
#: whitespace collapsed, since a reader's sentence may wrap inside the marker. Built from the
#: code point so this file's code does not depend on how the emoji is typed.
MARKER_TEXT = chr(0x1F916) + " Bootcamp-generated business case"
WRITER = "module-01-business-problem/phase2-document-confirm.md"
LIST_HOLDER = "graduation/SKILL.md"
READER_LIST = re.compile(
    r"machine-readable flag for the plugin's own branches \((?P<list>[^()]*)\)")
DOCSTRING_LIST = re.compile(r"its own branches -- (?P<list>.*?) -- every one of which")
_MODULE_DIR = re.compile(r"^module-0*(\d+[a-z]?)-")
_PHASE_FILE = re.compile(r"^phase([A-Za-z0-9]+)-")


def reader_name(relative):
    """A reader's name in the list, from its path: "Module 6 Phase C", or "Module 4"."""
    parts = relative.split("/")
    module = _MODULE_DIR.match(parts[0])
    if module is None:
        return None
    phase = _PHASE_FILE.match(parts[-1])
    return "Module %s" % module.group(1) + (" Phase %s" % phase.group(1) if phase else "")


def listed(names):
    return [name.strip() for name in re.split(r",| and ", names) if name.strip()]


def marker_reader_problems(files, graduation):
    """``files`` maps each path under `source/skills/` to its text."""
    m = READER_LIST.search(flat(graduation))
    if m is None:
        return ["graduation's list of the marker's readers moved"]
    named = listed(m.group("list"))
    readers = sorted(relative for relative, text in files.items()
                     if MARKER_TEXT in flat(text) and relative not in (WRITER, LIST_HOLDER))
    if not readers:
        return ["no file under source/skills/ reads the marker; the scan broke"]
    problems = []
    for relative in readers:
        name = reader_name(relative)
        if name is None:
            problems.append("%s reads the marker and is in no module, so the list cannot name "
                            "it by module and phase" % relative)
        elif name not in named:
            problems.append("%s reads the marker, and the list does not name %s"
                            % (relative, name))
    return problems


class TheMarkerReaderListNamesEveryReader(unittest.TestCase):
    """Item 4: graduation's list of the generated-scenario marker's readers."""

    @classmethod
    def setUpClass(cls):
        cls.files = {path.relative_to(SKILLS).as_posix(): read(path)
                     for path in sorted(SKILLS.rglob("*.md"))}
        cls.graduation = cls.files[LIST_HOLDER]

    def test_the_scan_reads_the_writer_and_the_readers(self):
        """Anti-vacuity (INV-265)."""
        self.assertIn(MARKER_TEXT, self.files[WRITER], "Module 1 no longer writes the marker")
        self.assertIn(MARKER_TEXT, self.graduation)
        readers = [relative for relative, text in self.files.items()
                   if MARKER_TEXT in flat(text) and relative not in (WRITER, LIST_HOLDER)]
        self.assertGreaterEqual(len(readers), 3, readers)

    def test_a_marker_that_wraps_is_still_found(self):
        """INV-346: Module 6 Phase C step 13 names the marker across a line break."""
        wrapped = {WRITER: self.files[WRITER], LIST_HOLDER: self.graduation,
                   "module-07-query-visualize-discover/SKILL.md":
                       "the `> %s` marker" % MARKER_TEXT.replace(" business", "\nbusiness")}
        self.assertEqual(
            ["module-07-query-visualize-discover/SKILL.md reads the marker, and the list does "
             "not name Module 7"], marker_reader_problems(wrapped, self.graduation))

    def test_the_list_names_every_reader(self):
        self.assertEqual([], marker_reader_problems(self.files, self.graduation))

    def test_the_list_names_readers_by_module_and_phase(self):
        named = listed(READER_LIST.search(flat(self.graduation)).group("list"))
        self.assertGreaterEqual(len(named), 3, named)
        for name in named:
            self.assertRegex(name, r"^Module \d+[a-z]?(?: Phase [A-Za-z0-9]+)?$",
                             "the list names a reader by something other than module and phase")

    def test_the_marker_test_docstring_repeats_the_same_list(self):
        docstring = DOCSTRING_LIST.search(flat(read(MARKER_TEST)))
        self.assertIsNotNone(docstring, "the marker test's docstring no longer lists the readers")
        self.assertEqual(listed(READER_LIST.search(flat(self.graduation)).group("list")),
                         listed(docstring.group("list")))

    def test_reader_names_come_from_the_path(self):
        self.assertEqual("Module 4", reader_name("module-04-data-collection/SKILL.md"))
        self.assertEqual("Module 6 Phase C",
                         reader_name("module-06-data-processing/phaseC-multi-source.md"))
        self.assertEqual("Module 3b Phase 2",
                         reader_name("module-03b-truthset-visualization/phase2-close.md"))
        self.assertIsNone(reader_name("bootcamp-onboarding/feedback.md"))

    def test_negative_controls(self):
        g = self.graduation
        shipped_list = "(Module 4, Module 6 Phase C and Module 6 Phase D)"
        self.assertIn(shipped_list, g)
        new_reader = dict(self.files)
        new_reader["module-07-query-visualize-discover/phase1-query-visualize.md"] += (
            "\nRead `docs/business_problem.md` for the `> %s` marker.\n" % MARKER_TEXT)
        outside = dict(self.files)
        outside["bootcamp-onboarding/feedback.md"] += "\n`> %s`\n" % MARKER_TEXT
        cases = {
            "a reader is left out": (self.files, g.replace(
                shipped_list, "(Module 4 and Module 6 Phase D)", 1)),
            "a phase is left out of a name": (self.files, g.replace(
                shipped_list, "(Module 4 and Module 6)", 1)),
            "the list is gone": (self.files, g.replace(shipped_list, "", 1)),
            "a new reader is not listed": (new_reader, g),
            "a reader outside every module": (outside, g),
            "nothing reads the marker": ({WRITER: self.files[WRITER], LIST_HOLDER: g}, g),
        }
        for name, (files, graduation) in cases.items():
            with self.subTest(mutant=name):
                self.assertTrue(files != self.files or graduation != g,
                                "the mutation no longer applies")
                self.assertNotEqual([], marker_reader_problems(files, graduation))
        self.assertEqual(
            ["module-07-query-visualize-discover/phase1-query-visualize.md reads the marker, "
             "and the list does not name Module 7 Phase 1"],
            marker_reader_problems(new_reader, g))

    def test_a_rewrap_still_passes(self):
        mutant = self.graduation.replace("(Module 4, Module 6 Phase C and Module 6 Phase D)",
                                         "(Module 4, Module 6\nPhase C and Module\n6 Phase D)", 1)
        self.assertNotEqual(self.graduation, mutant, "the re-wrap no longer applies")
        self.assertEqual([], marker_reader_problems(self.files, mutant))


# --- Items 5 and 6: one pointer and one comment --------------------------------------------

#: A fallback's pointer at a ground rule, in the form `failed-run-net.md` uses.
RULE_POINTER = re.compile(r'the "(?P<rule>[^"]+)" rule in `ground-rules\.md`')
CHECKPOINT_RULE = "In-progress recap checkpoint"
#: The packager's sentence naming the test that pins `DATABASE_BACKUP_ROOT` to the tuple.
PIN_SENTENCE = re.compile(r"`(?P<path>tests/[\w./-]+\.py)` pins the two together")
PINNED_CONSTANT = "DATABASE_BACKUP_ROOT"


def checkpoint_pointer_problems(fallback, ground_rules):
    text = flat(fallback)
    rules = [m.group("rule") for m in RULE_POINTER.finditer(text)]
    problems = []
    if CHECKPOINT_RULE not in rules:
        problems.append('the fallback does not point at the "%s" rule in `ground-rules.md`'
                        % CHECKPOINT_RULE)
    if "module-completion.md" in text:
        problems.append("the fallback names `module-completion.md`, which does not hold the rule")
    if "- **%s" % CHECKPOINT_RULE not in flat(ground_rules):
        problems.append('`ground-rules.md` has no rule that opens "%s"' % CHECKPOINT_RULE)
    return problems


def pin_comment_problems(packager, repo_root):
    m = PIN_SENTENCE.search(flat(packager.replace("#:", " ")))
    if m is None:
        return ["the packager's comment no longer names the test that pins the two together"]
    named = repo_root / m.group("path")
    if not named.is_file():
        return ["the packager's comment names %s, which does not exist" % m.group("path")]
    if PINNED_CONSTANT not in read(named):
        return ["the packager's comment names %s, which does not read %s"
                % (m.group("path"), PINNED_CONSTANT)]
    return []


class ThePointerAndTheCommentNameTheOwner(unittest.TestCase):
    """Items 5 and 6: `checkpoint-tick.md`'s pointer and `package_bootcamp.py`'s comment."""

    def setUp(self):
        self.fallback = read(CHECKPOINT_FALLBACK)
        self.ground_rules = read(GROUND_RULES)
        self.packager = read(PACKAGER)

    def test_the_fallback_names_the_rule_in_the_ground_rules(self):
        self.assertEqual([], checkpoint_pointer_problems(self.fallback, self.ground_rules))

    def test_the_fallback_names_no_assistant_specific_path(self):
        """The pointer reads the same in every package: a file name, no host value."""
        pointer = RULE_POINTER.search(flat(self.fallback))
        self.assertNotIn("{{", pointer.group(0))

    def test_the_comment_names_the_test_that_holds_the_pin(self):
        self.assertEqual([], pin_comment_problems(self.packager, REPO_ROOT))
        self.assertEqual("tests/test_quoted_sizes_say_what_they_missed.py",
                         PIN_SENTENCE.search(flat(self.packager.replace("#:", " "))).group("path"))

    def test_negative_controls(self):
        pointer = 'the\n"In-progress recap checkpoint" rule in `ground-rules.md` describes'
        self.assertIn(pointer, self.fallback)
        shipped = self.fallback.replace(pointer, "\n`module-completion.md` describes", 1)
        self.assertEqual(2, len(checkpoint_pointer_problems(shipped, self.ground_rules)))
        renamed = self.ground_rules.replace("- **In-progress recap checkpoint",
                                            "- **Recap checkpoint", 1)
        self.assertNotEqual(self.ground_rules, renamed, "the mutation no longer applies")
        self.assertEqual(1, len(checkpoint_pointer_problems(self.fallback, renamed)))
        named = "`tests/test_quoted_sizes_say_what_they_missed.py` pins the two together"
        self.assertIn(named, self.packager)
        for name, path in {
            "a test that does not read the constant": "tests/test_package_bootcamp.py",
            # A placeholder name, the form `test_comment_test_pointers_resolve.py` sets aside.
            "a test that does not exist": "tests/test_x.py",
        }.items():
            with self.subTest(mutant=name):
                mutant = self.packager.replace(named, "`%s` pins the two together" % path, 1)
                self.assertNotEqual([], pin_comment_problems(mutant, REPO_ROOT))
        self.assertNotEqual([], pin_comment_problems(self.packager.replace(named, "", 1),
                                                     REPO_ROOT))


# --- Item 7: one per-source mapping document -----------------------------------------------

#: Any document under `docs/mapping/` whose name opens `mapping_`: the dropped
#: `docs/mapping/mapping_[name].md`, whatever placeholder stands for the name.
DROPPED_DOCUMENT = re.compile(r"docs/mapping/mapping_")
MAPPER = "docs/mapping/{source_name}_mapper.md"
STRUCTURE_LEAD = "**Per-source mapping specification:**"
HOW_TO_RUN = "## How to run"
STEP_18 = ("### 18. Save and document", "### 18a.")
_MAPPING_PATH = re.compile(r"`(docs/mapping/[^`]+)`")


def text_files(root):
    """``(relative path, text)`` for every file under ``root`` that reads as UTF-8 text."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            yield path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def dropped_document_sites(files):
    """``relative:line`` for each place a file names the dropped document."""
    return ["%s:%d" % (relative, text.count("\n", 0, m.start()) + 1)
            for relative, text in files for m in DROPPED_DOCUMENT.finditer(text)]


def mapper_structure(text):
    """The headings of the `_mapper.md` structure step 18 gives, or None when it is not found."""
    lead = text.find(STRUCTURE_LEAD)
    if lead < 0:
        return None
    inside, headings = False, []
    # Line-scoped by design (#45): the structure is a fenced template, and a heading inside a
    # fence is a line. The fence is the first one after the lead.
    for line in text[lead:].splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if inside:
                return headings
            inside = True
        elif inside and stripped.startswith("#"):
            headings.append(stripped)
    return None


def structure_problems(text):
    headings = mapper_structure(text)
    if not headings:
        return ["step 18's `_mapper.md` structure was not found"]
    return ["the `_mapper.md` structure has no `%s` section" % heading
            for heading in (HOW_TO_RUN, "## Record Type Check") if heading not in headings]


def step_18_documents(text):
    """The documents under `docs/mapping/` that step 18 names, the lineage document aside."""
    start = text.find(STEP_18[0])
    end = text.find(STEP_18[1], start + 1)
    if start < 0 or end < 0:
        return None
    return sorted({path for path in _MAPPING_PATH.findall(text[start:end])
                   if "transformation_lineage_" not in path})


class Module5WritesOnePerSourceMappingDocument(unittest.TestCase):
    """Item 7: `_mapper.md` is the one per-source mapping document, with how to run in it."""

    @classmethod
    def setUpClass(cls):
        cls.files = list(text_files(SOURCE))
        cls.phase2 = read(MODULE_5_PHASE_2)

    def test_the_scan_reads_the_source_tree(self):
        """Anti-vacuity (INV-265): the scan reaches the files that name mapping documents."""
        self.assertGreaterEqual(len(self.files), 50)
        naming = [relative for relative, text in self.files if "docs/mapping/" in text]
        self.assertGreaterEqual(len(naming), 3, naming)

    def test_no_file_under_source_names_the_dropped_document(self):
        self.assertEqual([], dropped_document_sites(self.files))

    def test_step_18_names_one_mapping_document(self):
        self.assertEqual([MAPPER], step_18_documents(self.phase2))

    def test_the_structure_has_a_how_to_run_section(self):
        self.assertEqual([], structure_problems(self.phase2))
        self.assertIn("# Mapping Specification: {SOURCE_NAME}", mapper_structure(self.phase2))

    def test_how_to_run_names_the_program_and_the_command(self):
        """The one thing the dropped document held: the program, shared or not, and its run."""
        start = self.phase2.index("  " + HOW_TO_RUN)
        section = flat(self.phase2[start:self.phase2.index("  ## Record Type Check", start)])
        for needle in ("**Program:**", "shared program", "**Command:**", "data/raw/",
                       "data/senzing-ready/"):
            self.assertIn(needle, section)

    def test_the_record_type_check_section_is_still_kept(self):
        self.assertIn("**Keep the `## Record Type Check` section Phase 1 wrote.**", self.phase2)

    def test_negative_controls(self):
        t = self.phase2
        shipped = ("- Docs in `docs/mapping/mapping_[name].md` (field mappings, logic, quality, "
                   "how to run).\n")
        anchor = "- Sample output in `data/mapping/[name]_sample.jsonl`.\n"
        self.assertIn(anchor, t)
        put_back = t.replace(anchor, shipped + anchor, 1)
        self.assertEqual(1, len(dropped_document_sites([("phase2-data-mapping.md", put_back)])))
        self.assertEqual(["docs/mapping/mapping_[name].md", MAPPER], step_18_documents(put_back))
        for spelling in ("docs/mapping/mapping_{name}.md", "docs/mapping/mapping_customers.md"):
            self.assertEqual(["a.md:2"], dropped_document_sites([("a.md", "x\n" + spelling)]))
        self.assertEqual([], dropped_document_sites(
            [("a.md", "docs/visualizations/mapping_[name]_quality.html and " + MAPPER)]))
        no_section = t.replace("  " + HOW_TO_RUN + "\n", "  ## Running\n", 1)
        self.assertNotEqual(t, no_section, "the mutation no longer applies")
        self.assertEqual(["the `_mapper.md` structure has no `## How to run` section"],
                         structure_problems(no_section))
        self.assertEqual(["step 18's `_mapper.md` structure was not found"],
                         structure_problems(t.replace(STRUCTURE_LEAD, "**Specification:**", 1)))


if __name__ == "__main__":
    unittest.main()
