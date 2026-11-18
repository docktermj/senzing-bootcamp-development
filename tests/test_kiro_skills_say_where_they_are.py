"""Every skill in the Kiro package says where its own directory is.

Kiro hands the assistant a ``SKILL.md`` without its path, so "this skill directory" names
nothing. On Kiro IDE 1.4.26 (2026-11-15) the first turn ran ``find /`` for the files beside the
skill and reached a backup of another copy of the bootcamp. The Kiro package therefore states
each skill's installed location in the skill itself.

The location is stated inside the Kiro home, which the note defines, and not as a path under
``~`` (issue #11): Kiro documents one location for every platform, an absolute ``KIRO_HOME``
moves it, and ``~`` names nothing on Windows. ``options.skill_location_sources`` in
``hosts/kiro/host.json`` records, for each platform the bootcamp supports, what the stated
location rests on: an observed run, documentation, or nothing.

This module reads the note's wording and the record's shape. It cannot establish where Kiro
installs a Power on any platform; only a run on that platform can, and
``hosts/kiro/checks.json`` records the ones that happened.

Enforces the note on **INV-252** dated 2026-11-16 (issue #11), applied by the maintainer that
day: the stated location holds on every supported platform and its sources are recorded.

Issue #42 gave the note one order of places to look. Until then it had two sentences for a
bootcamp missing from the Kiro home, "look under `.kiro` in the user's home directory next" and
"look only inside `powers/` in the Kiro home", with no order between them, and none for a
bootcamp found nowhere.

⛔ **The note names four places to look, in one order, and tells the guide to stop when the bootcamp is in none of them.**

The order finishes one Kiro home before the next: the exact directory under ``KIRO_HOME``, then
anywhere inside its ``powers/``, then the same two under ``.kiro`` in the home directory. That
rule is INV-252's dated note of 2026-11-17 (#42), which the maintainer applied on 2026-11-18,
and this module enforces it. The module reads
the order the note states. It cannot establish which place a guide looks in first on a real
run.
"""

import json
import re
import unittest
from pathlib import Path

from _built import built

REPO_ROOT = Path(__file__).resolve().parents[1]
HOST_DIR = REPO_ROOT / "hosts" / "kiro"

HEADING = "**Where this skill's files are.**"
BOOTCAMP = "powers/installed/senzing-bootcamp"
PLATFORMS = ("linux", "macos", "windows")
STATUSES = ("observed", "documented", "unchecked")

#: The places the note sends the guide to, in the order it gives them (issue #42).
PLACES = (
    "(1) `powers/installed/senzing-bootcamp/` inside the directory `KIRO_HOME` names;",
    "(2) a `senzing-bootcamp` directory anywhere inside `powers/` in the directory `KIRO_HOME` names;",
    "(3) `powers/installed/senzing-bootcamp/` inside `.kiro` in the user's home directory;",
    "(4) a `senzing-bootcamp` directory anywhere inside `powers/` in `.kiro` in the user's home directory.",
)
SEQUENCE_OPENS = (
    "If the bootcamp is not there, look in these places, in this order, and take the first one that "
    "holds the bootcamp as the bootcamp's directory:"
)
ONLY_WHEN_SET = "Places 1 and 2 apply only when `KIRO_HOME` is set."
STOP = (
    "If none of the four places holds the bootcamp, stop and tell the bootcamper that the bootcamp's "
    "files were not found."
)
#: The two sentences issue #42 replaced: one condition, two instructions, no order.
REPLACED = (
    "If `KIRO_HOME` is set and the bootcamp is not under it, look under `.kiro` in the user's home "
    "directory next.",
    "If the bootcamp's directory is missing from the Kiro home, look only inside `powers/` in the Kiro "
    "home for `senzing-bootcamp`.",
)


def out_of_order(note):
    """What is wrong with the order of the note's places and its stop; empty when nothing is.

    Each part is stated once, and each starts after the one before it: the sentence that opens
    the sequence, the four places, the sentence limiting places 1 and 2, the stop, and the ban
    on searching the rest of the filesystem.
    """
    parts = (SEQUENCE_OPENS, *PLACES, ONLY_WHEN_SET, STOP, "Never search the rest of the filesystem")
    problems = [f"stated {note.count(part)} times, not once: {part}" for part in parts if note.count(part) != 1]
    if problems:
        return problems
    positions = [note.index(part) for part in parts]
    return [
        f"comes before the part it follows: {later}"
        for earlier, later, a, b in zip(parts, parts[1:], positions, positions[1:])
        if b < a + len(earlier)
    ]


def kiro_skills():
    """Every skill directory in the built Kiro package."""
    return sorted(path for path in (built("kiro") / "skills").iterdir() if path.is_dir())


def location_notes(skill):
    """The lines of a skill's ``SKILL.md`` that open with the note's heading.

    Line-scoped by design (#11): the build appends the note as one unwrapped line, so the note
    is that line and nothing beside it.
    """
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line.startswith(HEADING)]


def sources():
    """The per-platform record beside the note in ``hosts/kiro/host.json``."""
    host = json.loads((HOST_DIR / "host.json").read_text(encoding="utf-8"))
    return host["options"].get("skill_location_sources", {})


class KiroSkillsSayWhereTheyAre(unittest.TestCase):
    def each_note(self):
        skills = kiro_skills()
        self.assertTrue(skills)
        for skill in skills:
            notes = location_notes(skill)
            with self.subTest(skill=skill.name):
                self.assertEqual(len(notes), 1, "the note is stated once in each skill")
                yield skill.name, notes[0]

    def test_every_kiro_skill_names_its_own_directory(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                self.assertIn(f"The bootcamp's directory is `{BOOTCAMP}/` inside the Kiro home", note)
                self.assertIn(
                    f"this skill's directory is `{BOOTCAMP}/skills/{name}/` inside the Kiro home", note
                )

    def test_the_note_says_what_the_kiro_home_is(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                self.assertIn(
                    "The Kiro home is the value of the `KIRO_HOME` environment variable when it is "
                    "set, otherwise `.kiro` in the user's home directory (`%USERPROFILE%` on Windows).",
                    note,
                )

    def test_the_note_does_not_rely_on_a_tilde(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                self.assertNotIn("~", note)

    def test_the_note_says_what_each_reference_resolves_to(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                self.assertIn(
                    '"This skill directory", `<this-skill-dir>` and every `../` path in this file '
                    "count from this skill's directory",
                    note,
                )
                self.assertIn("`${PLUGIN_ROOT}` is the bootcamp's directory", note)

    def test_the_note_keeps_the_search_inside_the_kiro_home(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                self.assertIn("Never search the rest of the filesystem", note)
                self.assertIn("a second copy of the bootcamp on the same machine is normal", note)

    def test_the_note_names_the_four_places_in_order(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                for place in PLACES:
                    self.assertEqual(note.count(place), 1, place)
                positions = [note.index(place) for place in PLACES]
                self.assertEqual(positions, sorted(positions))
                self.assertLess(note.index(SEQUENCE_OPENS), positions[0])
                self.assertLess(positions[-1], note.index(ONLY_WHEN_SET))
                self.assertEqual(out_of_order(note), [])

    def test_the_stop_comes_after_the_last_place(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                self.assertEqual(note.count(STOP), 1)
                self.assertLess(note.index(PLACES[-1]), note.index(STOP))
                self.assertLess(note.index(STOP), note.index("Never search the rest of the filesystem"))

    def test_no_condition_in_the_note_has_two_instructions(self):
        for name, note in self.each_note():
            with self.subTest(skill=name):
                for sentence in REPLACED:
                    self.assertNotIn(sentence, note)
                self.assertNotIn("look only inside", note)
                conditions = re.findall(r"\bIf ([^,.:;]+),", note)
                self.assertEqual(
                    conditions, ["the bootcamp is not there", "none of the four places holds the bootcamp"]
                )

    def test_the_order_check_reports_a_note_that_is_out_of_order(self):
        """Negative controls, so the order check cannot pass on a note it does not read."""
        note = location_notes(kiro_skills()[0])[0]
        self.assertEqual(out_of_order(note), [])
        first, second, third, fourth = PLACES
        swapped = note.replace(second, "@@").replace(third, second).replace("@@", third)
        self.assertNotEqual(swapped, note)
        self.assertTrue(out_of_order(swapped), "places 2 and 3 exchanged")
        home_first = note.replace(first, "@@").replace(third, first).replace("@@", third)
        self.assertTrue(out_of_order(home_first), "the home directory looked at before `KIRO_HOME`")
        self.assertTrue(out_of_order(note.replace(fourth, "")), "the last place taken out")
        self.assertTrue(out_of_order(note.replace(STOP + " ", "")), "the stop taken out")
        early = note.replace(STOP + " ", "").replace(SEQUENCE_OPENS, STOP + " " + SEQUENCE_OPENS)
        self.assertTrue(out_of_order(early), "the stop given before the places")
        self.assertTrue(out_of_order(note + " " + STOP), "the stop given twice")

    def test_the_note_is_stated_once(self):
        for skill in kiro_skills():
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill.name):
                self.assertEqual(text.count(HEADING), 1)
                self.assertEqual(text.count("The Kiro home is the value of"), 1)
                self.assertEqual(text.count("Never search the rest of the filesystem"), 1)

    def test_an_assistant_that_gives_the_path_gets_no_note(self):
        for host in ("claude", "copilot"):
            for skill in sorted((built(host) / "skills").iterdir()):
                if skill.is_dir():
                    text = (skill / "SKILL.md").read_text(encoding="utf-8")
                    with self.subTest(host=host, skill=skill.name):
                        self.assertNotIn(".kiro/", text)
                        self.assertNotIn(HEADING, text)
                        self.assertNotIn("KIRO_HOME", text)
                        self.assertNotIn("Kiro home", text)


class TheLocationHasARecordedSourceOnEveryPlatform(unittest.TestCase):
    def test_the_record_has_every_supported_platform(self):
        self.assertEqual(sorted(sources()), sorted(PLATFORMS))

    def test_every_entry_has_a_known_status(self):
        for platform, entry in sources().items():
            with self.subTest(platform=platform):
                self.assertEqual(sorted(entry), ["date", "source", "status"])
                self.assertIn(entry["status"], STATUSES)

    def test_a_checked_platform_names_its_source_and_date(self):
        for platform, entry in sources().items():
            if entry["status"] == "unchecked":
                continue
            with self.subTest(platform=platform):
                self.assertTrue(entry["source"].strip())
                self.assertRegex(entry["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_an_observed_platform_points_at_a_recorded_run(self):
        runs = json.loads((HOST_DIR / "checks.json").read_text(encoding="utf-8"))
        for platform, entry in sources().items():
            if entry["status"] != "observed":
                continue
            with self.subTest(platform=platform):
                self.assertIn("hosts/kiro/checks.json", entry["source"])
                matching = [
                    run for run in runs if run["date"] == entry["date"] and run["client"] in entry["source"]
                ]
                self.assertTrue(matching, "no recorded run has this date and client")

    def test_a_documented_platform_names_a_page_and_claims_no_run(self):
        for platform, entry in sources().items():
            if entry["status"] != "documented":
                continue
            with self.subTest(platform=platform):
                self.assertIn("https://", entry["source"])
                self.assertIn("no run was observed", entry["source"])

    def test_the_record_as_it_stands(self):
        record = sources()
        self.assertEqual(record["linux"]["status"], "observed")
        self.assertEqual(record["linux"]["date"], "2026-11-15")
        self.assertIn("Kiro IDE 1.4.26", record["linux"]["source"])
        for platform in ("macos", "windows"):
            with self.subTest(platform=platform):
                self.assertEqual(record[platform]["status"], "documented")
                self.assertEqual(record[platform]["date"], "2026-11-16")
                self.assertIn("https://kiro.dev/docs/configuration/", record[platform]["source"])
                self.assertIn("https://docs.jfrog.com/ai-ml/docs/kiro", record[platform]["source"])

    def test_the_record_stays_out_of_the_package(self):
        for path in sorted(built("kiro").rglob("*")):
            if path.is_file():
                with self.subTest(file=path.relative_to(built("kiro")).as_posix()):
                    self.assertNotIn(b"skill_location_sources", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
