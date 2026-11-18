"""Module 2 Step 5 says of `search_docs` only that its results are ranked.

Step 5's fallback branch fills `{record limit}` from `sdk_guide(topic='load',
record_count=<above the limit>)`, and names that tool rather than "a Senzing MCP tool". The
reason it gives for the choice has been wrong about `search_docs` twice, each time because the
docs index was rebuilt and the passage described one build of it:

- Until #150 it said `search_docs` "does **not** answer this" and "returns EULA and pricing
  prose with no figure". On server 1.37.13 (docs index 2026-09-24 18:45 UTC) the result set
  carried an FAQ, "What is the 500 record limit and how do I work around SENZ9000", that states
  the figure. #150 rescoped the claim to a ranking: the top-ranked hits state no figure and the
  FAQ ranks lower. This file was then `test_record_limit_negative_is_rescoped.py` and held the
  passage, its `MCP-NEGATIVE` marker and its `VERIFIED_QUERIES` record to that ranking claim.
- On server 1.46.1 (docs index 2026-11-14 17:44 UTC, asked 2026-11-17 and again 2026-11-18) the
  FAQ is the top hit, so the ranking claim was false too (issue #35 of this repository).

The route never stopped working. What failed both times was the description of `search_docs`.
So the passage now gives a reason no rebuild can change: `sdk_guide` states the figure in a
fixed field, `compatibility_notes`, while `search_docs` results are ranked. It says nothing
else about `search_docs`.

⛔ **Step 5's record-limit fallback says of `search_docs` only that its results are ranked: it never says which hit ranks where, never says that a query lacks the figure, and carries no `MCP-NEGATIVE` marker for a record-limit query.**

This file fails when any of the three comes back in Step 5, or when the query the retired
marker named is prescribed again or recorded in `VERIFIED_QUERIES`. It also holds what #150
established and this change keeps: the fill route, the fixed-field reason, no figure and no
date in the prose (INV-080), and no claim that `sdk_guide` reports the active license (it
reports the documented default; the active license is measured in Step 5a).

**The guard is rescoped, not deleted (INV-219).** It asserts properties of the passage, never
its wording, so a later rewording that keeps them passes.

**Negative controls.** The two retired passages are kept below as fixtures and run
on every pass: each must be reported, by the same function that reads the shipped text.

**What this cannot establish.** It reads Markdown. It does not call the server, so it does not
show that `sdk_guide` still states the figure, or what any `search_docs` query returns now.

Prose is matched with whitespace collapsed (INV-346). Stdlib only; nothing under ``source/`` is
imported (INV-108).
"""

import ast
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "source"
SKILL = SOURCE / "skills" / "module-02-sdk-setup" / "SKILL.md"
ALLOWLIST = REPO / "tests" / "test_prescribed_search_queries.py"

#: The query the retired marker named. No shipped file prescribes it now.
QUERY = "evaluation license record limit how many records without a license"
#: Built, not written, so this file never carries a bare marker token of its own.
TOKEN = "MCP-NEGATIVE" + ":"
#: Step 5's fallback instruction: from the fill rule to the assumption text it fills.
BLOCK_START = "Fill `{record limit}` below from the MCP server"
BLOCK_END = "\"I couldn't read your license from the SDK just now"

#: Which hit ranks where. "ranked" alone is not in it: that is the one thing the passage says.
RANK_CLAIM = re.compile(
    r"(?i)\b(?:top|lower|higher|highest|lowest|first|second|third|last)[- ]ranked\b"
    r"|\b(?:top|first|second|third|last|leading)\s+(?:\w+\s+)?(?:hits?|results?)\b"
    r"|\branks?\s+(?:above|below|ahead|behind|higher|lower|first|second|third|last|just|\d)"
    r"|\branked\s+(?:above|below|ahead|behind|higher|lower|first|second|third|last|\d)"
    r"|\boutranks?\b"
    r"|\brank\s+\d"
    r"|\bhits?\s+\d"
)
#: The query lacks the figure, or the tool does not answer.
ABSENCE_CLAIM = re.compile(
    r"(?i)does\s+(?:\*\*)?not(?:\*\*)?\s+(?:answer|give|return|state|carry|have)"
    r"|\b(?:cannot|can't|doesn't|never)\s+(?:answer|give|return|state|carry)"
    r"|\bno\s+figure\b"
    r"|\b(?:without|lacks?|omits?|misses)\s+(?:it|the\s+figure|a\s+figure|the\s+limit)\b"
)


def find(text, start, end):
    begin = text.find(start)
    stop = text.find(end, begin)
    if begin < 0 or stop < 0:
        raise AssertionError("Step 5's {record limit} fill instruction was not found")
    return text[begin:stop]


def step5_block():
    return find(SKILL.read_text(encoding="utf-8"), BLOCK_START, BLOCK_END)


def prose(block):
    """Comment-stripped, fence-stripped, whitespace-collapsed visible prose."""
    block = re.sub(r"<!--.*?-->", " ", block, flags=re.S)
    block = re.sub(r"```.*?```", " ", block, flags=re.S)
    return " ".join(block.split())


def sentences_naming_search_docs(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if "search_docs" in s]


def record_limit_markers(block):
    """Marker lines in the block that name `search_docs`.

    Line-scoped by design (#35): INV-209 requires an `MCP-NEGATIVE` marker on ONE line, so a
    marker is found by its line.
    """
    return [line for line in block.split("\n") if TOKEN in line and "search_docs" in line]


def problems(block):
    """Every way `block` says more about `search_docs` than that its results are ranked."""
    found = []
    visible = prose(block)
    named = sentences_naming_search_docs(visible)
    if not named:
        found.append("no sentence names search_docs, so the reason for naming sdk_guide is gone")
    for sentence in named:
        if not re.search(r"(?i)\branked\b", sentence):
            found.append("a search_docs sentence does not say its results are ranked: %r"
                         % sentence)
        match = ABSENCE_CLAIM.search(sentence)
        if match:
            found.append("absence claim %r in: %r" % (match.group(0), sentence))
    # A rank claim is read over the whole passage: the retired one ran across three sentences.
    for match in RANK_CLAIM.finditer(visible):
        found.append("rank claim %r" % match.group(0))
    for line in record_limit_markers(block):
        found.append("marker for a search_docs query: %r" % line[:90])
    if QUERY in block:
        found.append("the retired record-limit query is named")
    return found


def verified_queries():
    """The allowlist dict, read with `ast` so the other test module is never executed here."""
    tree = ast.parse(ALLOWLIST.read_text(encoding="utf-8"))
    for node in tree.body:
        if (isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "VERIFIED_QUERIES"
                        for t in node.targets)):
            return ast.literal_eval(node.value)
    raise AssertionError("VERIFIED_QUERIES not found in %s" % ALLOWLIST.name)


# --- The retired passages, kept as negative controls ------------------------------------------

_FRAME_HEAD = (
    "Fill `{record limit}` below from the MCP server before presenting this. The route that "
    "answers it is `sdk_guide` with a\n`record_count` above the default limit, whose "
    "`compatibility_notes` name the limit outright:\n\n```text\nsdk_guide(topic='load', "
    "language='<chosen_language>', platform='<user_platform>', record_count=1000)\n```\n\n"
)
_FRAME_TAIL = (
    " Present exactly what the server returns (waiting up to 30 seconds). If it\nreturns no "
    "figure, drop the parenthetical entirely and say the current limit is unavailable from\n"
    "the MCP server. Never substitute a hardcoded or remembered figure (INV-080).\n\n"
)

#: Step 5 as #150 left it, and as it shipped until issue #35: a ranking claim with its marker.
RETIRED_RANKING_PASSAGE = (
    _FRAME_HEAD
    + "<!-- " + TOKEN + " search_docs(query='" + QUERY + "') — the top-ranked hits are EULA "
    "grant-of-license prose that states no figure; the figure appears only in a lower-ranked "
    "FAQ, so a guide reading the top hit comes away without it — owner: sdk_guide(topic='load', "
    "record_count=<above the limit>) states the figure in a fixed field, compatibility_notes "
    "(routing negative — the figure exists, go there) — server 1.37.13, 2026-09-24 -->\n"
    "The tool is named here, rather than left as \"a Senzing MCP tool\", because `sdk_guide` "
    "states the\nfigure in a fixed field, `compatibility_notes`. `search_docs` ranks its results "
    "instead: asked for\nthe evaluation license's record limit, its top-ranked hits are EULA "
    "grant-of-license prose that\nstates no figure, and the figure sits in a lower-ranked FAQ, so "
    "a guide reading the top hit comes\naway without it."
    + _FRAME_TAIL
)

#: Step 5 before #150: an absence claim about the whole result set.
RETIRED_ABSENCE_PASSAGE = (
    _FRAME_HEAD
    + "The tool is named here, rather than left as \"a Senzing MCP tool\", because `search_docs` "
    "does **not** answer this —\nasked for the evaluation license's record limit it returns EULA "
    "and pricing prose with no\nfigure (re-checked 2026-08-13)."
    + _FRAME_TAIL
)

#: The passage as issue #35 corrected it, so the controls have a clean case to stand against.
CORRECTED_PASSAGE = (
    _FRAME_HEAD
    + "The tool is named here, rather than left as \"a Senzing MCP tool\", because `sdk_guide` "
    "states the\nfigure in a fixed field, `compatibility_notes`, while `search_docs` results are "
    "ranked."
    + _FRAME_TAIL
)


def problems_input(passage):
    """A fixture passage, cut the way the shipped block is cut."""
    return find(passage + BLOCK_END, BLOCK_START, BLOCK_END)


class StepFiveSaysOnlyThatSearchDocsIsRanked(unittest.TestCase):
    """The shipped passage: the fixed-field reason, and nothing about `search_docs` but ranking."""

    def setUp(self):
        self.block = step5_block()
        self.prose = prose(self.block)

    def test_the_passage_makes_no_rank_claim_no_absence_claim_and_carries_no_marker(self):
        self.assertEqual(
            [], problems(self.block),
            "Step 5's record-limit fallback says more about search_docs than that its results "
            "are ranked. A statement of which hit ranks where, or of what a query lacks, is "
            "true of one build of the docs index and has been made false by a rebuild twice "
            "(2026-09-24 and by 2026-11-17)")

    def test_the_reason_sdk_guide_is_named_is_the_fixed_field(self):
        self.assertIn("`sdk_guide` states the figure in a fixed field, `compatibility_notes`",
                      self.prose,
                      "the reason sdk_guide is named is that it states the figure in a fixed "
                      "field, compatibility_notes")

    def test_the_fill_route_is_unchanged(self):
        self.assertIn("sdk_guide(topic='load'", self.block)
        self.assertRegex(self.block, r"record_count=\d+")
        self.assertIn("Never substitute a hardcoded or remembered figure", self.prose)
        self.assertIn("INV-080", self.prose)

    def test_it_does_not_claim_sdk_guide_reports_the_active_license(self):
        self.assertNotRegex(
            self.prose, r"(?i)\bactive\s+licen[cs]e",
            "sdk_guide is static guidance and reports the documented DEFAULT limit; the active "
            "license is measured in Step 5a with SzProduct.getLicense(). The 'active license' "
            "rationale is false and must not be written (#150)")

    def test_the_prose_carries_no_figure_and_no_date(self):
        visible = re.sub(r"INV-\d{3}", " ", self.prose)
        self.assertIsNone(re.search(r"\b\d{3,}\b", visible),
                          "Step 5's fallback prose states a number; the record limit must come "
                          "from the server, never from this file (INV-080)")
        self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\d\b", visible),
                          "Step 5's fallback prose carries a date; it states nothing that was "
                          "measured on one day")


class TheRetiredQueryIsNeitherPrescribedNorRecorded(unittest.TestCase):
    """The marker was the query's only shipped site, so the query and its record went with it."""

    def test_no_shipped_file_names_the_query(self):
        named = [path.relative_to(REPO).as_posix()
                 for path in sorted(SOURCE.rglob("*.md"))
                 if QUERY in " ".join(path.read_text(encoding="utf-8").split())]
        self.assertEqual([], named,
                         "the record-limit search_docs query is back in shipped text; Step 5 "
                         "fills the figure from sdk_guide and names no search_docs query")

    def test_the_scan_reads_shipped_markdown(self):
        """Anti-vacuity (INV-265): the file the query was removed from is among those read."""
        self.assertIn(SKILL, list(SOURCE.rglob("*.md")))

    def test_the_allowlist_holds_no_record_for_it(self):
        keys = [key for key in verified_queries() if key[1] == QUERY]
        self.assertEqual([], keys,
                         "VERIFIED_QUERIES records the record-limit query again, with no shipped "
                         "site to account for")


class TheRetiredPassagesAreReported(unittest.TestCase):
    """Negative controls: `problems()` reports each retired passage, and passes the corrected one."""

    def test_the_corrected_passage_is_clean(self):
        self.assertEqual([], problems(problems_input(CORRECTED_PASSAGE)))

    def test_the_ranking_passage_is_reported_for_its_rank_claim(self):
        found = problems(problems_input(RETIRED_RANKING_PASSAGE))
        self.assertTrue([p for p in found if p.startswith("rank claim")], found)

    def test_the_ranking_passage_is_reported_for_its_absence_claim(self):
        found = problems(problems_input(RETIRED_RANKING_PASSAGE))
        self.assertTrue([p for p in found if p.startswith("absence claim")], found)

    def test_the_ranking_passage_is_reported_for_its_marker(self):
        found = problems(problems_input(RETIRED_RANKING_PASSAGE))
        self.assertTrue([p for p in found if p.startswith("marker for")], found)
        self.assertIn("the retired record-limit query is named", found)

    def test_a_marker_alone_is_reported(self):
        """The corrected prose with the marker put back fails on the marker."""
        marker = "<!-- " + TOKEN + " search_docs(query='a new record limit query') — x -->\n"
        found = problems(problems_input(CORRECTED_PASSAGE.replace(
            "The tool is named here", marker + "The tool is named here")))
        self.assertEqual(1, len(found), found)
        self.assertTrue(found[0].startswith("marker for"), found)

    def test_the_absence_passage_is_reported(self):
        found = problems(problems_input(RETIRED_ABSENCE_PASSAGE))
        self.assertTrue([p for p in found if p.startswith("absence claim")], found)
        self.assertTrue([p for p in found if "does not say its results are ranked" in p], found)

    def test_a_rank_claim_in_another_sentence_is_reported(self):
        """A rank claim is caught wherever it sits, not only beside the tool's name."""
        text = CORRECTED_PASSAGE.replace(
            "results are ranked.", "results are ranked. The FAQ that has it ranks below the EULA.")
        found = problems(problems_input(text))
        self.assertEqual(["rank claim 'ranks below'"], found)

    def test_dropping_the_reason_is_reported(self):
        """Deleting the search_docs half cannot pass by leaving nothing to read."""
        text = CORRECTED_PASSAGE.replace(", while `search_docs` results are ranked", "")
        found = problems(problems_input(text))
        self.assertEqual(1, len(found), found)
        self.assertIn("no sentence names search_docs", found[0])


if __name__ == "__main__":
    unittest.main()
