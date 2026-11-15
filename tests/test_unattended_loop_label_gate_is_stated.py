"""`docs/development.md` states the unattended loop's label gate.

`/unattended-issue-loop` *(user level)* opens and merges pull requests with nobody watching, so
which issues it may work is the one thing a maintainer must be able to read before starting it.
Until the one-repository migration, 2026-11-14, that was stated in the family workflow page's
row for the loop, which the overlay under `.claude/skill-overlays/` points to. That page was not
carried into this repository, so the statement had no home here. It now lives in
`docs/development.md`, in the section headed "The unattended loop works only on labeled issues",
and this module holds it there.

Three statements, each required in that section:

1. `/unattended-issue-loop` works only on issues labeled `unattended-ok`;
2. an unlabeled backlog is a no-op;
3. the loop never applies that label itself, citing **INV-318** in the same list item or
   paragraph.

The rule is about sentences, so the section is read through `collapsed_items()` from
`tests/_wrapped_text.py` (INV-346): a statement wrapped across lines still matches, each list
item is read on its own, and the citation must sit in the unit that makes the claim. Only the
section is read. The same words elsewhere on the page, in the command list for instance, do not
count, because the section is where a maintainer is sent to read the gate.

Negative controls: each statement struck from the real section is reported by name and alone; a
statement re-wrapped across lines is still found; the three statements placed outside the
section are not accepted; the third statement without its citation, or with the citation in a
different list item, is reported; and a section saying the loop applies the label is reported.

⚠️ **What a green run does not establish.** That the loop behaves this way. Its governing copy
is the user-level skill under `~/.claude/skills/`, which is not checked in CI (INV-308), and
nothing here runs it. This module establishes only that the page a maintainer reads says what
the gate is, and that INV-318 is still the invariant about that label.

Stdlib only (INV-108); two files read as text, no network.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

from _wrapped_text import collapsed_items

REPO_ROOT = Path(__file__).resolve().parent.parent
DEV_DOCS = REPO_ROOT / "docs" / "development.md"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

HEADING = "## The unattended loop works only on labeled issues"

#: (name, the statement, the citation its unit must carry or None).
STATEMENTS = (
    ("works only on labeled issues",
     re.compile(r"`/unattended-issue-loop`(?: \*\(user level\)\*)? works only on issues "
                r"labeled `unattended-ok`"),
     None),
    ("an unlabeled backlog is a no-op",
     re.compile(r"(?i)\bunlabeled backlog is a no-op\b"),
     None),
    ("the loop never applies the label",
     re.compile(r"(?i)\bloop never applies that label itself\b"),
     "INV-318"),
)


def section(text):
    """The body of the label-gate section: from its heading to the next `## ` heading, or ''.

    Line-scoped by design (INV-346): an ATX heading is one line, and it is the heading that is
    looked for here. The statements inside the section are read wrap-aware, in `missing()`.
    """
    body, inside = [], False
    for line in text.splitlines():
        if line.strip() == HEADING:
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            body.append(line)
    return "\n".join(body)


def missing(text):
    """The names of the statements the label-gate section of ``text`` does not make."""
    units = [flat for flat, _origin in collapsed_items(section(text))]
    absent = []
    for name, statement, citation in STATEMENTS:
        made = [unit for unit in units if statement.search(unit)]
        if citation is not None:
            made = [unit for unit in made if citation in unit]
        if not made:
            absent.append(name)
    return absent


def dev_docs():
    return DEV_DOCS.read_text(encoding="utf-8")


class TheSectionStatesTheGate(unittest.TestCase):
    def test_the_section_exists(self):
        self.assertTrue(section(dev_docs()).strip(),
                        "docs/development.md has no section headed %r, or it is empty" % HEADING)

    def test_all_three_statements_are_made(self):
        self.assertEqual(
            [], missing(dev_docs()),
            "the label-gate section of docs/development.md does not state every part of the "
            "gate. A maintainer starting the loop must be able to read which issues it works, "
            "that no label means no work, and that it never labels an issue itself (INV-318)")

    def test_inv318_is_still_the_invariant_about_that_label(self):
        """The citation must not point at a rule about something else."""
        entry = [line for line in INVARIANTS.read_text(encoding="utf-8").splitlines()
                 if line.startswith("- **INV-318**")]
        self.assertEqual(1, len(entry), "INV-318 was not found once in specs/INVARIANTS.md")
        self.assertIn("`unattended-ok`", entry[0])
        self.assertIn("/unattended-issue-loop", entry[0])


class TheCheckCatchesAMissingStatement(unittest.TestCase):
    """Negative controls, on the real page and on synthetic ones."""

    SYNTHETIC = (
        "# Page\n\n" + HEADING + "\n\n"
        "`/unattended-issue-loop` *(user level)* works only on issues labeled `unattended-ok`.\n\n"
        "- **An unlabeled backlog is a no-op.**\n"
        "- ⛔ **(INV-318) The loop never applies that label itself.**\n\n"
        "## Next\n")

    def test_the_synthetic_page_passes(self):
        self.assertEqual([], missing(self.SYNTHETIC))

    def test_each_statement_struck_from_the_real_section_is_reported_alone(self):
        text = dev_docs()
        for name, struck in (
                ("works only on labeled issues", "works only on issues"),
                ("an unlabeled backlog is a no-op", "is a no-op"),
                ("the loop never applies the label", "never applies that label")):
            with self.subTest(statement=name):
                self.assertEqual(1, section(text).count(struck),
                                 "the control's wording moved: %r" % struck)
                self.assertEqual([name], missing(text.replace(struck, "does something")))

    def test_a_statement_wrapped_across_lines_is_still_found(self):
        wrapped = (self.SYNTHETIC
                   .replace("works only on issues labeled", "works only\non issues\nlabeled")
                   .replace("backlog is a no-op", "backlog is\n  a no-op")
                   .replace("never applies that label", "never applies\n  that label"))
        self.assertNotEqual(self.SYNTHETIC, wrapped)
        self.assertEqual([], missing(wrapped))

    def test_the_statements_outside_the_section_do_not_count(self):
        moved = self.SYNTHETIC.replace(HEADING, "## Something else")
        self.assertEqual([name for name, _statement, _citation in STATEMENTS], missing(moved))
        after = self.SYNTHETIC.replace(HEADING + "\n\n", "").replace(
            "## Next\n", "## Next\n\n" + HEADING + "\n\nNothing is said here.\n")
        self.assertEqual([name for name, _statement, _citation in STATEMENTS], missing(after))

    def test_the_third_statement_needs_its_citation_in_the_same_item(self):
        uncited = self.SYNTHETIC.replace("(INV-318) ", "")
        self.assertEqual(["the loop never applies the label"], missing(uncited))
        elsewhere = uncited.replace("- **An unlabeled", "- (INV-318) **An unlabeled")
        self.assertEqual(["the loop never applies the label"], missing(elsewhere))

    def test_a_section_saying_the_loop_applies_the_label_is_reported(self):
        reversed_rule = self.SYNTHETIC.replace("never applies that label itself",
                                               "applies that label itself")
        self.assertEqual(["the loop never applies the label"], missing(reversed_rule))


if __name__ == "__main__":
    unittest.main()
