"""`selected_modules` is kept in one file, `config/bootcamp_preferences.yaml` (#44).

Bootcamp preparation wrote the module selection twice: into `config/bootcamp_preferences.yaml`
in its consolidated write, and into `config/bootcamp_progress.json` in a second write that
said the progress copy was "where module-completion and the journey map read it". Every site
that named a file for the list named the preferences file, and the Bootcamper is told to edit
that file to change a saved choice, which left the progress copy stale. Four more sites read
the list inside a write to the progress file and named no file, so they could be taken to mean
the progress copy (finding 14 of `production-readiness-audit-2026-11-17`). The dry-run
scaffold wrote the progress copy too, and its mid-bootcamp preferences held no list.

What must hold:

- ⛔ **`selected_modules` is kept in one file, `config/bootcamp_preferences.yaml`, and nothing writes it to `config/bootcamp_progress.json`.**
  Bootcamp preparation's Step 6 writes the list in its consolidated preferences write. Its
  write to the progress file sets `current_module` to the first content module and does not
  name the list. The dry-run scaffold writes no `selected_modules` key to the progress file in
  any mode, and its mid-bootcamp preferences carry the ordered list.
- ⛔ **A step that sets `current_module` to the next module in `selected_modules` names `config/bootcamp_preferences.yaml` as the file the list is read from.**
  Held by name for the four steps that do so on 2026-11-17: module completion's Step 1 and
  the closes of Entity Resolution Concepts, System verification and Truth Set visualization.
  Held as well for any such step found anywhere under `source/`.

How "names the file" is read. The text is cut into list items and paragraphs with whitespace
collapsed, so a sentence that wraps is still one sentence (INV-346). An item ties the list to
the preferences file when `selected_modules` and `config/bootcamp_preferences.yaml` are
neighboring backticked names in one sentence: no other backticked name and no sentence end
sits between them, in either order. "`selected_modules` (read from
`config/bootcamp_preferences.yaml`)" and "`config/bootcamp_preferences.yaml`
(`selected_modules`)" both do.

⚠️ **What these checks cannot establish.** That a live guide reads the list from the
preferences file: only a run shows that. They read `source/`, which every assistant's package
is built from, and not a built package. A mention of `selected_modules` that names no file and
sets no `current_module` is not checked; the issue leaves those unedited. An item that names
the list beside both files passes the third check. A `selected_modules` key already in the
progress file of a bootcamp in progress is neither read nor removed by anything here.

Every check fails when it finds nothing to read, and each has a negative control that runs on
every pass (INV-265). The module order is read from Bootcamp preparation's own Core list and
not copied here (INV-246).

Standard library only; the scaffold is loaded by file path (INV-108). Paths are built with
`pathlib` and files are read as UTF-8, so the module does not depend on the platform
(INV-001).

Run:  python3 -m unittest discover -s tests
"""
import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from _wrapped_text import collapsed_items  # wrap-aware: one list item or paragraph at a time

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "source"
SKILLS = SOURCE / "skills"
PREPARATION = SKILLS / "bootcamp-preparation" / "SKILL.md"
SCAFFOLD = REPO_ROOT / ".claude" / "skills" / "dry-run" / "scaffold_project.py"

#: The four steps that set `current_module` from the list, recorded on 2026-11-17 (#44).
READER_SITES = (
    SKILLS / "bootcamp-onboarding" / "module-completion.md",
    SKILLS / "module-00-entity-resolution-concepts" / "SKILL.md",
    SKILLS / "module-03-system-verification" / "phase2-report-close.md",
    SKILLS / "module-03b-truthset-visualization" / "phase2-close.md",
)

KEY = "`selected_modules`"
PREFERENCES_FILE = "`config/bootcamp_preferences.yaml`"
PROGRESS_FILE = "`config/bootcamp_progress.json`"

#: A step that sets `current_module` to the next module in the list. Read on collapsed text.
SETS_NEXT_MODULE = re.compile(r"`current_module` to the next module in `selected_modules`")
#: The list and the preferences file as neighboring backticked names, in either order. The
#: text between them is group 1 or group 2.
NEIGHBORS = re.compile(
    r"`selected_modules`([^`]*)`config/bootcamp_preferences\.yaml`"
    r"|`config/bootcamp_preferences\.yaml`([^`]*)`selected_modules`")
#: A sentence end inside the text between two names.
SENTENCE_END = re.compile(r"[.!?:;](?:\s|$)")
#: A YAML `selected_modules:` list: the key first on its line, then its `- token` lines. The
#: key may be indented, as it is in an example inside a list item.
YAML_LIST = re.compile(
    r"^[ \t]*selected_modules:[ \t]*(?:#[^\n]*)?\n((?:[ \t]+-[ \t]*\w+[ \t]*(?:#[^\n]*)?\n)+)",
    re.M)


def read(path):
    return Path(path).read_text(encoding="utf-8")


def items(text):
    """The text of each list item or paragraph, whitespace collapsed."""
    return [flat for flat, _origin in collapsed_items(text)]


def ties_the_list_to_preferences(item):
    """True when the list and the preferences file are neighboring names in one sentence."""
    for match in NEIGHBORS.finditer(item):
        between = match.group(1) if match.group(1) is not None else match.group(2)
        if not SENTENCE_END.search(between):
            return True
    return False


def step6(text):
    """Bootcamp preparation's Step 6, from its heading to the next step's heading."""
    found = re.search(r"(?ms)^## 6\. .*?(?=^## 7\. )", text)
    return found.group(0) if found else ""


def progress_write_problems(text):
    """What is wrong with Step 6's write to the progress file; empty when it is right."""
    section = step6(text)
    if not section:
        return ["no `## 6.` section before `## 7.`"]
    writes = [item for item in items(section) if PROGRESS_FILE in item]
    if len(writes) != 1:
        return [f"{len(writes)} items in Step 6 name {PROGRESS_FILE}; expected exactly one"]
    write = writes[0]
    problems = []
    if "selected_modules" in write:
        problems.append("the progress write names `selected_modules`")
    if not re.search(r"`current_module`", write):
        problems.append("the progress write does not set `current_module`")
    if "first content module" not in write:
        problems.append("the progress write does not point at the first content module")
    return problems


def preferences_write_problems(text):
    """What is wrong with Step 6's one copy of the list; empty when it is right."""
    section = step6(text)
    carrying = [item for item in items(section) if PREFERENCES_FILE in item and KEY in item]
    if not carrying:
        return [f"no item in Step 6 writes {KEY} to {PREFERENCES_FILE}"]
    if not YAML_LIST.search(section):
        return ["Step 6 shows no `selected_modules:` list in its preferences example"]
    return []


def reader_site_problems(text):
    """What is wrong with a file's steps that set `current_module` from the list."""
    sites = [item for item in items(text) if SETS_NEXT_MODULE.search(item)]
    if not sites:
        return ["no item sets `current_module` to the next module in `selected_modules`"]
    return [f"reads {KEY} without naming {PREFERENCES_FILE} as its file: {site[:120]!r}"
            for site in sites if not ties_the_list_to_preferences(site)]


def named_file_problems(text):
    """Items that name the list and the progress file, and do not tie the list to preferences."""
    return [f"names {KEY} beside {PROGRESS_FILE} and not {PREFERENCES_FILE}: {item[:120]!r}"
            for item in items(text)
            if KEY in item and PROGRESS_FILE in item and not ties_the_list_to_preferences(item)]


def source_texts():
    """`(relative path, text)` for every UTF-8 file under `source/`."""
    out = []
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file():
            continue
        try:
            out.append((path.relative_to(REPO_ROOT).as_posix(), read(path)))
        except UnicodeDecodeError:
            continue
    return out


def yaml_list(text):
    """The ordered tokens of a YAML `selected_modules:` list in `text`; empty when none."""
    found = YAML_LIST.search(text)
    return re.findall(r"-[ \t]*(\w+)", found.group(1)) if found else []


def core_list():
    """The Core path's ordered tokens, from Bootcamp preparation's Step 1."""
    found = re.search(r"(?ms)^## 1\. .*?(?=^## 2\. )", read(PREPARATION))
    return yaml_list(found.group(0)) if found else []


def load_scaffold():
    spec = importlib.util.spec_from_file_location("scaffold_44", SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def progress_key_problems(progress_text):
    """What is wrong with a built `config/bootcamp_progress.json`; empty when it is right."""
    try:
        progress = json.loads(progress_text)
    except ValueError as error:
        return [f"not JSON: {error}"]
    if not isinstance(progress, dict):
        return ["not a JSON object"]
    return ["carries a `selected_modules` key"] if "selected_modules" in progress else []


class PreparationWritesTheListOnce(unittest.TestCase):

    def test_the_progress_write_does_not_name_the_list(self):
        self.assertEqual(progress_write_problems(read(PREPARATION)), [])

    def test_the_preferences_write_carries_the_list(self):
        self.assertEqual(preferences_write_problems(read(PREPARATION)), [])

    def test_the_text_as_it_shipped_fails(self):
        shipped = (
            "## 6. Consolidated preference write (once, quietly)\n\n"
            "Persist `selected_modules` to `config/bootcamp_preferences.yaml`.\n\n"
            "Also record the selection into `config/bootcamp_progress.json` where "
            "module-completion and the\njourney map read it (a single batched write, INV-012): "
            "the ordered `selected_modules` and the\n`current_module` pointing at the first "
            "content module.\n\n## 7. Recap\n")
        self.assertEqual(progress_write_problems(shipped),
                         ["the progress write names `selected_modules`"])

    def test_the_list_put_back_into_the_progress_write_fails(self):
        original = read(PREPARATION)
        text = original.replace("This write sets no other key.",
                                "It also writes the ordered `selected_modules` there.", 1)
        self.assertNotEqual(text, original)
        self.assertIn("the progress write names `selected_modules`",
                      progress_write_problems(text))

    def test_a_progress_write_without_current_module_fails(self):
        original = read(PREPARATION)
        text = original.replace("Also set `current_module` in", "Also record the start in", 1)
        self.assertNotEqual(text, original)
        self.assertIn("the progress write does not set `current_module`",
                      progress_write_problems(text))

    def test_a_progress_write_that_drops_the_first_content_module_fails(self):
        original = read(PREPARATION)
        text = original.replace("to the first content module (a single",
                                "to the next module (a single", 1)
        self.assertNotEqual(text, original)
        self.assertIn("the progress write does not point at the first content module",
                      progress_write_problems(text))

    def test_a_missing_or_second_progress_write_fails(self):
        original = read(PREPARATION)
        without = original.replace(PROGRESS_FILE, "`config/other.json`")
        self.assertNotEqual(progress_write_problems(without), [])
        doubled = original.replace(
            "## 7. ", f"Then write {PROGRESS_FILE} again.\n\n## 7. ", 1)
        self.assertNotEqual(progress_write_problems(doubled), [])
        self.assertNotEqual(progress_write_problems("no steps here"), [])

    def test_a_preferences_write_without_the_list_fails(self):
        original = read(PREPARATION)
        section = step6(original)
        self.assertTrue(section)
        stripped = original.replace(section, section.replace("selected_modules", "modules"))
        self.assertNotEqual(preferences_write_problems(stripped), [])


class EveryReaderNamesThePreferencesFile(unittest.TestCase):

    def test_the_four_sites(self):
        for path in READER_SITES:
            with self.subTest(site=path.relative_to(REPO_ROOT).as_posix()):
                self.assertEqual(reader_site_problems(read(path)), [])

    def test_every_such_step_under_source(self):
        found, problems = [], []
        for name, text in source_texts():
            if not SETS_NEXT_MODULE.search(" ".join(items(text))):
                continue
            found.append(name)
            problems += [f"{name}: {problem}" for problem in reader_site_problems(text)]
        expected = sorted(path.relative_to(REPO_ROOT).as_posix() for path in READER_SITES)
        self.assertEqual([], [name for name in expected if name not in found],
                         "a recorded site no longer sets `current_module` from the list")
        self.assertEqual(problems, [])

    def test_no_item_under_source_names_the_progress_file_for_the_list(self):
        texts = source_texts()
        mentions = [name for name, text in texts if KEY in text]
        self.assertGreaterEqual(len(mentions), 4, "found too little under source/ to check")
        problems = [f"{name}: {problem}"
                    for name, text in texts for problem in named_file_problems(text)]
        self.assertEqual(problems, [])

    def test_each_site_without_the_file_name_fails(self):
        for path in READER_SITES:
            original = read(path)
            for label, text in (
                    ("the progress file named instead",
                     original.replace(PREFERENCES_FILE, PROGRESS_FILE)),
                    ("another file named instead",
                     original.replace(PREFERENCES_FILE, "`config/other.yaml`")),
                    ("no file named",
                     re.sub(r"\s*\(read\s+from\s+`config/bootcamp_preferences\.yaml`\)"
                            r"|\s*Read `selected_modules` from "
                            r"`config/bootcamp_preferences\.yaml`,[^.]*\.", "", original))):
                with self.subTest(site=path.name, mutation=label):
                    self.assertNotEqual(text, original)
                    self.assertNotEqual(reader_site_problems(text), [])

    def test_a_reworded_site_that_is_no_longer_found_fails(self):
        for path in READER_SITES:
            original = read(path)
            text = re.sub(r"to\s+the\s+next\s+module\s+in\s+`selected_modules`",
                          "to whichever module follows", original)
            with self.subTest(site=path.name):
                self.assertNotEqual(text, original)
                self.assertNotEqual(reader_site_problems(text), [])

    def test_the_tie_is_found_across_a_line_wrap_and_in_either_order(self):
        for item in (
                "1. Set `current_module` to the next module in\n   `selected_modules` (read\n"
                "   from\n   `config/bootcamp_preferences.yaml`), and `current_step` to `null`.",
                "- Set `current_module` to the next module in `selected_modules`, always. "
                "Read `selected_modules`\n  from `config/bootcamp_preferences.yaml`.",
                "Read `config/bootcamp_preferences.yaml`\n(`selected_modules`), then set "
                "`current_module` to the next module in `selected_modules`."):
            with self.subTest(item=item[:50]):
                self.assertEqual(reader_site_problems(item), [])

    def test_a_file_named_in_another_sentence_or_for_another_key_is_not_a_tie(self):
        for item in (
                "- Set `current_module` to the next module in `selected_modules`. The name is "
                "in `config/bootcamp_preferences.yaml`.",
                "- Set `current_module` to the next module in `selected_modules`, with `name` "
                "from `config/bootcamp_preferences.yaml`.",
                "1. In `config/bootcamp_progress.json`: set `current_module` to the next module "
                "in `selected_modules`, and `current_step` to `null`."):
            with self.subTest(item=item[:60]):
                self.assertNotEqual(reader_site_problems(item), [])

    def test_the_progress_file_named_for_the_list_fails(self):
        self.assertNotEqual(named_file_problems(
            "Write the ordered `selected_modules` to\n`config/bootcamp_progress.json`."), [])
        self.assertNotEqual(named_file_problems(
            "1. In `config/bootcamp_progress.json`: set `current_module` to the next module in "
            "`selected_modules`."), [])
        self.assertEqual(named_file_problems(
            "First read `config/bootcamp_preferences.yaml` (`selected_modules`)\nand "
            "`config/bootcamp_progress.json` (`modules_completed`)."), [])
        self.assertEqual(named_file_problems(
            "Set `current_module` in `config/bootcamp_progress.json` to the first module."), [])


class TheScaffoldKeepsTheListInPreferences(unittest.TestCase):

    MODES = (("mid", False, False), ("fresh", True, False), ("seeded", False, True))

    @classmethod
    def setUpClass(cls):
        cls.scaffold = load_scaffold()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.projects = {}
        for mode, fresh, seeded in cls.MODES:
            root = Path(cls.tmp.name) / mode
            with contextlib.redirect_stdout(io.StringIO()):
                cls.scaffold.build(root, fresh, seeded)
            cls.projects[mode] = root

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_no_mode_writes_the_key_to_the_progress_file(self):
        self.assertNotIn("selected_modules", self.scaffold.PROGRESS)
        for mode, root in self.projects.items():
            with self.subTest(mode=mode):
                text = read(root / "config" / "bootcamp_progress.json")
                self.assertEqual(progress_key_problems(text), [])
                self.assertNotIn("selected_modules", text)

    def test_the_mid_progress_file_is_still_a_bootcamp_in_progress(self):
        progress = json.loads(read(self.projects["mid"] / "config" / "bootcamp_progress.json"))
        self.assertEqual(progress.get("current_module"), "data_quality_mapping")
        self.assertTrue(progress.get("modules_completed"))

    def test_the_mid_preferences_carry_the_ordered_list(self):
        expected = core_list()
        self.assertEqual(len(expected), 11, "Bootcamp preparation's Core list was not read")
        text = read(self.projects["mid"] / "config" / "bootcamp_preferences.yaml")
        self.assertEqual(text, self.scaffold.PREFERENCES)
        self.assertEqual(yaml_list(text), expected)

    def test_the_mid_list_holds_the_module_the_progress_file_is_on(self):
        progress = self.scaffold.PROGRESS
        listed = yaml_list(self.scaffold.PREFERENCES)
        self.assertIn(progress["current_module"], listed)
        for token in progress["modules_completed"]:
            with self.subTest(token=token):
                self.assertIn(token, listed)

    def test_the_seeded_preferences_carry_the_same_list(self):
        expected = core_list()
        self.assertEqual(len(expected), 11, "Bootcamp preparation's Core list was not read")
        self.assertEqual(yaml_list(self.scaffold.SEEDED_PREFERENCES), expected)

    def test_a_progress_file_with_the_key_fails(self):
        self.assertEqual(progress_key_problems('{"current_module": "sdk_setup"}'), [])
        self.assertEqual(progress_key_problems("{}"), [])
        self.assertNotEqual(progress_key_problems(
            '{"current_module": "sdk_setup", "selected_modules": ["sdk_setup"]}'), [])
        self.assertNotEqual(progress_key_problems("not json"), [])
        self.assertNotEqual(progress_key_problems("[]"), [])

    def test_a_preferences_file_without_the_list_reads_as_empty(self):
        self.assertEqual(yaml_list("path: core\nprogramming_language: Python\n"), [])
        self.assertEqual(yaml_list("path: core\nselected_modules:\n  - a   # note\n  - b\n"),
                         ["a", "b"])


if __name__ == "__main__":
    unittest.main()
