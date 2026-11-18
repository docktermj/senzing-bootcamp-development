"""A result from a bootcamp repository is not a Senzing source (issue #37).

The Senzing MCP server's example and documentation corpus indexes the bootcamp's own
repositories. On server 1.46.1 (docs index 2026-11-14 17:44 UTC, asked 2026-11-17 and again
2026-11-18) `find_examples(query='multi-source')` surfaced the changelogs of two bootcamp
repositories and nothing else, and a `search_docs` query ranked a bootcamp script first. Until
#37 no shipped text said such a hit is not Senzing evidence, so a guide that treats the server
as its only source of Senzing facts could be handed the bootcamp's own text back.

What this file holds, all of it read from `source/`, so it holds for every assistant:

- **The rule is stated once, in the ground rules' MCP-first section.** Its bold label opens a
  bullet in `ground-rules.md` under "MCP-first invariant (absolute precedence)" and appears in
  no other shipped file (INV-300).
- **The rule is a property of the result, not a list.** It says a result whose repository name
  contains `bootcamp`, compared without regard to case, is disregarded; that it covers any MCP
  result that names its repository and a repository added or renamed later; and where the
  repository is read: the `repo` field of a `find_examples` hit, and the `title` and
  `source_url` of a `search_docs` hit, which has no `repo` field.
- **Partial and total disregard.** Some hits disregarded: the rest are used as before. Every hit
  disregarded: the call counts as having returned no Senzing example, the step continues on its
  existing fallback, and nothing is said to the bootcamper.
- **The observation is dated.** The rule names `find_examples` and `search_docs` as the observed
  cases with a server version and a date.
- **No shipped file names a bootcamp repository.** Each repository's name holds an assistant's
  name, so `source/` names none of them, in any file and any letter case.
- **The orchestrator marker agrees with its evidence.** Module 6 Phase C's `MCP-NEGATIVE` marker
  points at the ground rules' MCP-first section, and its server version and date are the ones
  the two `find_examples` evidence slots in `tests/test_prescribed_search_queries.py` carry.

Drafted as a DEFERRED INVARIANT in this issue's `specs/IMPLEMENTED.md` entry; minting it is the
maintainer's.

**Properties, not wording (INV-219).** Nothing here pins what the server returns, and the rule's
own sentences are checked for what they say, by co-occurrence within the rule's bullet, not
for their exact words.

**Negative controls.** Every check is one function, `problems(texts)`, run on the shipped files
and on in-memory copies with one thing taken out or added. Each copy must be reported.

**What this cannot establish.** It reads Markdown and calls no server (INV-108). It does not
show that a live guide disregards such a hit, that the server still indexes these repositories,
or which hits a query returns today. A repository named in some other field of a future result
is not seen here.

Prose is collapsed with `" ".join(text.split())` before it is matched (INV-346). The marker is
read as one line on purpose. Line-scoped by design (#37): INV-209 requires an `MCP-NEGATIVE`
marker on ONE line, so the marker's own line is the unit.

Stdlib only; nothing under ``source/`` is imported (INV-108).

Source issue: #37.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

import _corpus
import test_prescribed_search_queries as prescribed

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "source" / "skills"
RULE_FILE = SKILLS / "bootcamp-onboarding" / "ground-rules.md"
MARKER_FILE = SKILLS / "module-06-data-processing" / "phaseC-multi-source.md"

RULE_LABEL = "**A result from a bootcamp repository is not a Senzing source"
SECTION = "## MCP-first invariant (absolute precedence)"
#: Built, not written, so this file never carries a bare marker token of its own.
TOKEN = "MCP-" + "NEGATIVE:"
MARKER_OPENING = TOKEN + " find_examples(query='multi-source')"
SLOT_KEYS = (
    ("find_examples", "multi-source", None),
    ("find_examples", "orchestrator load multiple data sources", None),
)
#: The bootcamp repositories the server indexed when #37 was filed. Each holds an assistant's
#: name, which is why `source/` may not carry them; built from parts so the list reads as data.
REPOSITORIES = tuple("senzing-bootcamp-" + rest
                     for rest in ("claude-plugin", "kiro-power", "chatgpt-plugin"))

#: What the rule must say, each as a pattern found in the rule's own bullet, wraps collapsed.
CLAUSES = {
    "the property: a repository name containing `bootcamp`":
        r"repository's name contains `bootcamp`",
    "the case rule": r"without regard to case",
    "that the result is disregarded": r"\bdisregard",
    "that it covers any MCP result that names its repository":
        r"[Aa]ny MCP result that names its repository",
    "the find_examples field": r"`repo` field of a `find_examples` hit",
    "the search_docs fields": r"`title` and `source_url` of a\s+`search_docs` hit",
    "that a search_docs hit has no repo field": r"`search_docs` hit, which has no `repo` field",
    "that it is a property, not a list": r"property of the name, not a list",
    "a repository added or renamed later": r"added or renamed later",
    "partial disregard: the rest are used as before": r"use the rest as before",
    "total disregard: no Senzing example": r"counts as having returned no\s+Senzing example",
    "total disregard: the existing fallback": r"continues on its existing fallback",
    "total disregard: nothing said to the bootcamper":
        r"nothing is said to the\s+bootcamper",
    "the observed cases, dated":
        r"Observed in `find_examples` and `search_docs` results[^.]*?"
        r"server \d+\.\d+\.\d+[^.]*?\d{4}-\d{2}-\d{2}",
}
STAMP = re.compile(r"— server (\d+\.\d+\.\d+), (\d{4}-\d{2}-\d{2}) -->")


def flat(text):
    return " ".join(text.split())


def shipped():
    """Every file under `source/` that reads as UTF-8 text, by path."""
    out = {}
    for path in _corpus.corpus_files("source"):
        try:
            out[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return out


def rule_bullet(text):
    """The rule's bullet, from its `- ` to the next top-level item or heading, comments kept."""
    label = text.find(RULE_LABEL)
    if label < 0:
        return ""
    start = text.rfind("\n- ", 0, label) + 1
    following = re.search(r"\n(?:- |#)", text[label:])
    end = label + following.start() if following else len(text)
    return text[start:end]


def section_of(text, index):
    """The `## ` heading the character at ``index`` sits under."""
    headings = [m for m in re.finditer(r"(?m)^## .*$", text) if m.start() < index]
    return headings[-1].group(0) if headings else ""


def marker_line(text):
    """The orchestrator marker's one line. Line-scoped by design (#37), as INV-209 asks."""
    return [ln for ln in text.splitlines() if MARKER_OPENING in ln]


def problems(texts, slots):
    """Everything wrong with the rule, the repository names and the marker. Empty is clean."""
    out = []
    owners = sorted(path for path, text in texts.items() if RULE_LABEL in text)
    if owners != [RULE_FILE]:
        out.append("the rule must be stated in ground-rules.md and nowhere else; found in %s"
                   % [str(p.relative_to(REPO)) for p in owners] if owners else
                   "no shipped file states the rule")
    rule_text = texts.get(RULE_FILE, "")
    if RULE_LABEL in rule_text:
        if rule_text.count(RULE_LABEL) != 1:
            out.append("ground-rules.md states the rule more than once")
        if section_of(rule_text, rule_text.find(RULE_LABEL)) != SECTION:
            out.append("the rule is not in the section %r" % SECTION)
        bullet = flat(re.sub(r"<!--.*?-->", " ", rule_bullet(rule_text), flags=re.S))
        for name, pattern in CLAUSES.items():
            if not re.search(pattern, bullet):
                out.append("the rule does not state " + name)
    for path, text in texts.items():
        lowered = text.lower()
        for repository in REPOSITORIES:
            if repository in lowered:
                out.append("%s names the bootcamp repository %s"
                           % (path.relative_to(REPO), repository))
    lines = marker_line(texts.get(MARKER_FILE, ""))
    if len(lines) != 1:
        out.append("expected one orchestrator marker in phaseC-multi-source.md, found %d"
                   % len(lines))
        return out
    line = lines[0]
    if 'ground-rules.md → "MCP-first invariant (absolute precedence)"' not in line:
        out.append("the orchestrator marker does not point at the ground rules' MCP-first section")
    stamp = STAMP.search(line)
    if not stamp:
        out.append("the orchestrator marker carries no server stamp")
        return out
    for key in SLOT_KEYS:
        record = slots.get(key)
        if record is None:
            out.append("no evidence slot for %r" % (key,))
        elif (record["server"], record["measured"]) != stamp.groups():
            out.append("evidence slot %r is stamped %s, %s; the marker %s, %s"
                       % (key, record["server"], record["measured"], *stamp.groups()))
    return out


class TheShippedTextIsClean(unittest.TestCase):
    def test_no_problems(self):
        self.assertEqual(problems(shipped(), prescribed.VERIFIED_QUERIES), [])


class EachCheckReportsItsCase(unittest.TestCase):
    """Negative controls on in-memory copies; nothing on disk changes."""

    def setUp(self):
        self.texts = shipped()
        self.slots = dict(prescribed.VERIFIED_QUERIES)
        self.rule = self.texts[RULE_FILE]

    def assertReported(self, texts, fragment, slots=None):
        found = problems(texts, self.slots if slots is None else slots)
        self.assertTrue(any(fragment in p for p in found),
                        "expected a problem containing %r, got %r" % (fragment, found))

    def with_rule(self, rule_text):
        texts = dict(self.texts)
        texts[RULE_FILE] = rule_text
        return texts

    def test_a_missing_rule_is_reported(self):
        self.assertReported(self.with_rule(self.rule.replace(RULE_LABEL, "**Something else")),
                            "no shipped file states the rule")

    def test_a_second_copy_elsewhere_is_reported(self):
        texts = dict(self.texts)
        texts[MARKER_FILE] = texts[MARKER_FILE] + "\n- ⛔ " + RULE_LABEL + ".**\n"
        self.assertReported(texts, "nowhere else")

    def test_a_rule_outside_the_section_is_reported(self):
        start = self.rule.find(SECTION)
        moved = self.rule[:start] + "## Somewhere else\n\n" + self.rule[start + len(SECTION):]
        self.assertReported(self.with_rule(moved), "is not in the section")

    def test_each_clause_is_required(self):
        bullet = rule_bullet(self.rule)
        collapsed = flat(bullet)
        for name, pattern in CLAUSES.items():
            with self.subTest(clause=name):
                self.assertIsNotNone(re.search(pattern, collapsed), name)
                stripped = re.sub(pattern, "", collapsed)
                self.assertReported(self.with_rule(self.rule.replace(bullet, stripped + "\n")),
                                    "the rule does not state " + name)

    def test_a_named_repository_is_reported_in_any_case(self):
        for repository in REPOSITORIES:
            with self.subTest(repository=repository):
                self.assertReported(self.with_rule(self.rule + "\n" + repository.upper() + "\n"),
                                    "names the bootcamp repository " + repository)

    def test_a_marker_without_the_pointer_is_reported(self):
        texts = dict(self.texts)
        texts[MARKER_FILE] = texts[MARKER_FILE].replace(
            '"MCP-first invariant (absolute precedence)"', '"Elsewhere"')
        self.assertReported(texts, "does not point at the ground rules")

    def test_a_slot_on_another_stamp_is_reported(self):
        slots = dict(self.slots)
        record = dict(slots[SLOT_KEYS[0]])
        record["measured"] = "2026-10-15"
        slots[SLOT_KEYS[0]] = record
        self.assertReported(self.texts, "evidence slot", slots=slots)

    def test_a_missing_marker_is_reported(self):
        texts = dict(self.texts)
        texts[MARKER_FILE] = texts[MARKER_FILE].replace(MARKER_OPENING, TOKEN + " other")
        self.assertReported(texts, "expected one orchestrator marker")


if __name__ == "__main__":
    unittest.main()
