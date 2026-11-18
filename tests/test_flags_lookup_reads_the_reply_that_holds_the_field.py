"""A method's flags lookup reads each thing from the reply that holds it (issue #36).

Enforces **INV-435** (registered 2026-11-18). It reads Markdown and calls no server, so it
cannot establish that a live guide tells the two reply shapes apart before reading one.

`get_sdk_reference(topic='flags', filter='<method>')` used to return every flag as an entry
with fields. On server 1.46.1 (asked 2026-11-17 and again 2026-11-18) it returns, for most
method names, a **compact list**: lines of text under group headers, with a `detail` field that
names a `flag_details` topic. The fields the shipped steps read (`applies_to`, `source_file`,
`depends_on`, `composite_members`, `response_paths`) are in the **row form**, which a flag-name
filter and `topic='flag_details'` return. Until #36 no shipped file named `flag_details`, one
step read `source_file` from the compact list, and another sent the guide to that list for a
flag's dependency, where the list prints "depends on" and "member of" with the same `=` it
prints a composite with.

What this file holds, all of it read from `source/`, so it holds for every assistant:

- **The rule is in one file.** The bold label "Reading a flags reply" opens a passage in
  `ground-rules.md` and nowhere else. The passage says to choose flags from the compact list
  and to call the row form before reading a field or a full description, by flag name for one
  flag or by `topic='flag_details'` for a method.
- **The fallback.** The same passage says what to do when the compact list carries no `detail`
  pointer or `topic='flag_details'` fails: the flag-name row, and saying which route produced
  what is presented (INV-125).
- **Every site points at the rule.** Each Markdown file that makes a method-filter
  `topic='flags'` call either holds the rule or names it with a `ground-rules.md` → "Reading a
  flags reply" pointer. The sites are found by scanning, never listed (INV-246).
- **No site reads a field from the compact list.** A list item or paragraph that makes a
  method-filter call and names one of the five fields also names the route the field comes
  from: the row form, `flag_details`, or a flag-name filter.
- **The dependency lookup and the dated note.** In Module 7's flags section the sentence that
  looks up `SZ_INCLUDE_MATCH_KEY_DETAILS`'s dependency names that flag's own row and its
  `description`. The paragraph beside it is a dated note saying that `=` in the compact list
  also marks "depends on" and "member of", so `A = B` is not proof that `A` is a composite.
- **The Module 6 marker agrees with its sentence.** The dated marker for the method-filter call
  in `phaseD-validation.md` carries a version and date the prose beside it states, and the two
  name the same origin token.

Proposed as a dated correction to **INV-132**, which says flag entries under a method filter
carry `composite_members`, `depends_on` and `response_paths`. The block is in the
`specs/IMPLEMENTED.md` entry for this issue; registering it is the maintainer's.

**Properties, not wording (INV-219).** Nothing here pins what the server returns: no flag
line, group header or description is asserted. A later correction that keeps the routing
passes. The checks on the rule's own sentences are co-occurrence checks within one sentence.

**Negative controls.** Every check is one function, `problems(texts)`, run on the shipped
files and on in-memory copies with one thing taken out. Each copy must be reported, and the
retired Module 6 sentence is kept below as a fixture.

**What this cannot establish.** It reads Markdown. It does not call the server, so it does not
show which shape any filter returns now, or that `flag_details` still exists (INV-108). The
field check is a co-occurrence check on one list item or paragraph: it cannot tell which reply
a sentence reads a field from, and a field read in a different paragraph from its call is not
seen. A call written with no `filter='…'` argument is not a site.

Prose is read through `_wrapped_text`, with whitespace collapsed (INV-346). Stdlib only;
nothing under ``source/`` is imported (INV-108).

Source issue: #36.

Run:  python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

import _corpus
from _wrapped_text import collapsed_blocks, collapsed_items

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "source" / "skills"
RULE_FILE = SKILLS / "bootcamp-onboarding" / "ground-rules.md"
MODULE_7 = SKILLS / "module-07-query-visualize-discover"
NOTE_FILE = MODULE_7 / "phase1-query-visualize.md"
PHASE_2B = MODULE_7 / "phase2b-discover.md"
PHASE_D = SKILLS / "module-06-data-processing" / "phaseD-validation.md"

RULE_NAME = "Reading a flags reply"
RULE_LABEL = "**" + RULE_NAME + ".**"
POINTER = '→ "' + RULE_NAME + '"'
#: The fields a flag's row carries and the compact list does not.
FIELDS = ("applies_to", "source_file", "depends_on", "composite_members", "response_paths")
ROW_BY_NAME = "get_sdk_reference(topic='flags', filter='<flag name>')"
DETAILS = "topic='flag_details'"
DEPENDENT_FLAG = "SZ_INCLUDE_MATCH_KEY_DETAILS"
#: Built, not written, so this file never carries a bare marker token of its own.
TOKEN = "MCP-" + "NEGATIVE:"

#: A `topic='flags'` call and its filter. A flag name or the flag-name placeholder is the row
#: form's own call; anything else is a method filter.
FLAGS_CALL = re.compile(r"topic='flags',\s*filter='([^']+)'")
#: The routes that return a flag's fields.
ROW_ROUTE = re.compile(
    r"row form|flag_details|topic='flags',\s*filter='(?:SZ_[A-Z_]+|<flag name>)'")
STAMP = re.compile(r"server (\d+\.\d+\.\d+)[,)]? \(?(\d{4}-\d{2}-\d{2})")
COMMENT = re.compile(r"<!--.*?-->", re.S)
ORIGIN = re.compile(r"fallback:[\w-]+")


def shipped():
    """Every Markdown file under `source/`, by path."""
    return {path: path.read_text(encoding="utf-8")
            for path in _corpus.corpus_files("source", suffixes={".md"})}


def flat(text):
    return " ".join(text.split())


def sentences(text):
    return re.split(r"(?<=[.!?])\s+", text)


def is_method_filter(value):
    return not value.startswith("SZ_") and value != "<flag name>"


def method_filters(text):
    """The method filters of the `topic='flags'` calls in ``text`` (already collapsed)."""
    return [m.group(1) for m in FLAGS_CALL.finditer(text) if is_method_filter(m.group(1))]


def shown(path):
    try:
        return Path(path).relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def rule_passage(text):
    """The rule, from its bold label to the next top-level list item, comments removed."""
    start = text.find(RULE_LABEL)
    if start < 0:
        return ""
    following = re.search(r"\n- ", text[start:])
    end = start + following.start() if following else len(text)
    return flat(COMMENT.sub(" ", text[start:end]))


def rule_problems(texts):
    owners = [path for path, text in texts.items() if RULE_LABEL in text]
    if owners != [RULE_FILE]:
        return ["the rule %r is held by %s, not by ground-rules.md alone"
                % (RULE_NAME, [shown(p) for p in owners] or "no file")]
    passage, found = rule_passage(texts[RULE_FILE]), []
    said = sentences(passage)
    if not any("compact list" in s and re.search(r"(?i)\b(?:choose|pick|select)\b", s)
               for s in said):
        found.append("the rule does not say to choose flags from the compact list")
    if not any("row form" in s and "field" in s and "full description" in s
               and "flag name" in s and "flag_details" in s for s in said):
        found.append("the rule does not say to call the row form, by flag name or by "
                     "topic='flag_details', before reading a field or a full description")
    if ROW_BY_NAME not in passage:
        found.append("the rule does not write out the flag-name row call")
    if DETAILS not in passage:
        found.append("the rule does not name topic='flag_details'")
    if not any("`detail`" in s and "flag_details" in s and ROW_BY_NAME in s
               and re.search(r"(?i)\bfalls? back\b|\bfallback\b", s)
               and "which route" in s and "INV-125" in s for s in said):
        found.append("the rule states no fallback for a missing `detail` pointer or a failed "
                     "topic='flag_details' call: the flag-name row, and which route produced "
                     "what is presented (INV-125)")
    return found


def pointer_problems(texts):
    """A file that makes a method-filter flags call holds the rule or points at it."""
    found = []
    for path, text in sorted(texts.items()):
        if path == RULE_FILE or not method_filters(flat(text)):
            continue
        if POINTER not in flat(text):
            found.append("%s makes a method-filter topic='flags' call and never points at "
                         "ground-rules.md %s" % (shown(path), POINTER))
    return found


def field_problems(texts):
    """A unit that makes a method-filter call and names a field names the row route too."""
    found = []
    for path, text in sorted(texts.items()):
        for unit, origin in collapsed_items(text):
            if not method_filters(unit):
                continue
            named = [field for field in FIELDS if "`%s`" % field in unit or " %s " % field in unit]
            if named and not ROW_ROUTE.search(unit):
                found.append("%s:%d reads %s beside a method-filter topic='flags' call and "
                             "names no row-form route" % (shown(path), origin[0], named))
    return found


def is_the_note(unit):
    """The paragraph that says what `=` marks, by the two terms it names in quotes."""
    return ("compact list" in unit and "`=`" in unit
            and '"depends on"' in unit and '"member of"' in unit)


def note_problems(texts):
    """The dependency lookup names the flag's own row; a dated note about `=` sits beside it."""
    text = texts.get(NOTE_FILE, "")
    units = [COMMENT.sub(" ", unit) for unit, _origin in collapsed_blocks(text)]
    notes = [i for i, unit in enumerate(units) if is_the_note(unit)]
    if not notes:
        return ['%s has no note saying that `=` in the compact list also marks "depends on" '
                'and "member of"' % shown(NOTE_FILE)]
    at, found = notes[0], []
    note = units[at]
    if not STAMP.search(note):
        found.append("the `=` note carries no server version and date")
    if not re.search(r"not proof that `A` is a composite", note):
        found.append("the `=` note does not say that `A = B` is not proof that `A` is a composite")
    row_call = "get_sdk_reference(topic='flags', filter='%s')" % DEPENDENT_FLAG
    beside = [units[i] for i in (at - 1, at + 1) if 0 <= i < len(units)]
    if not any(row_call in s and "description" in s for unit in beside for s in sentences(unit)):
        found.append("no sentence beside the `=` note sends the guide to %s's own row and its "
                     "description for the dependency" % DEPENDENT_FLAG)
    return found


def marker_problems(texts):
    """Module 6's marker for the method-filter call agrees with the prose it dates."""
    found, seen = [], 0
    for unit, origin in collapsed_blocks(texts.get(PHASE_D, "")):
        prose = COMMENT.sub(" ", unit)
        for comment in COMMENT.findall(unit):
            if TOKEN not in comment or not method_filters(comment):
                continue
            seen += 1
            where = "%s:%d" % (shown(PHASE_D), origin[0])
            stamp = STAMP.search(comment)
            if not stamp or stamp.groups() not in [m.groups() for m in STAMP.finditer(prose)]:
                found.append("%s: the marker's version and date are not the ones its "
                             "paragraph states" % where)
            if set(ORIGIN.findall(comment)) != set(ORIGIN.findall(prose)):
                found.append("%s: the marker and its paragraph name different origins" % where)
    if not seen:
        found.append("%s has no marker for a method-filter topic='flags' call"
                     % shown(PHASE_D))
    return found


def problems(texts):
    return (rule_problems(texts) + pointer_problems(texts) + field_problems(texts)
            + note_problems(texts) + marker_problems(texts))


# --- Negative controls ---------------------------------------------------------------------------

#: The Module 6 paragraph as it shipped until issue #36: it reads `source_file` from the reply
#: to a method-filter call, which no longer carries it, and names no other route for it.
RETIRED_PARAGRAPH = (
    "`get_sdk_reference(topic='flags', filter='<method>', language='<chosen_language>')` lists "
    "the\nflags documented for the method, but it does not narrow that list by binding: with\n"
    "`language='python'` it still returns `SZ_EXPORT_ALL_FLAGS`, and only its `source_file`\n"
    "(`fallback:java-sdk-SzFlag-enum`) shows the Java origin (MCP server 1.37.16, 2026-09-30).\n"
)
FIXTURE = SKILLS / "fixture-for-issue-36" / "SKILL.md"


def changed(texts, path, old, new):
    """A copy of ``texts`` with ``old`` replaced in ``path``; fails when ``old`` is not there."""
    if old not in texts[path]:
        raise AssertionError("the control's target text is gone from %s: %r" % (shown(path), old))
    out = dict(texts)
    out[path] = texts[path].replace(old, new)
    return out


class TheShippedTextRoutesEachRead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = shipped()

    def test_the_scan_finds_the_sites(self):
        # Vacuity floor: five files made a method-filter call when #36 landed.
        sites = [path for path, text in self.texts.items() if method_filters(flat(text))]
        self.assertGreaterEqual(len(sites), 4, [shown(p) for p in sites])
        self.assertIn(RULE_FILE, sites)

    def test_the_rule_is_in_one_file_and_says_which_reply_holds_what(self):
        self.assertEqual([], rule_problems(self.texts))

    def test_every_file_that_makes_the_call_points_at_the_rule(self):
        self.assertEqual([], pointer_problems(self.texts))

    def test_no_site_reads_a_field_without_naming_the_row_form(self):
        self.assertEqual([], field_problems(self.texts))

    def test_the_dependency_lookup_and_the_dated_note_sit_together(self):
        self.assertEqual([], note_problems(self.texts))

    def test_the_module_6_marker_agrees_with_its_sentence(self):
        self.assertEqual([], marker_problems(self.texts))

    def test_nothing_is_reported_on_the_shipped_files(self):
        self.assertEqual([], problems(self.texts))


class EachCheckFires(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = shipped()

    def reported(self, texts, fragment):
        found = problems(texts)
        self.assertTrue(any(fragment in problem for problem in found),
                        "expected a problem naming %r, got %r" % (fragment, found))

    def test_a_second_copy_of_the_rule_is_reported(self):
        texts = dict(self.texts)
        texts[FIXTURE] = RULE_LABEL + " A copy.\n"
        self.reported(texts, "not by ground-rules.md alone")

    def test_a_rule_without_flag_details_is_reported(self):
        texts = changed(self.texts, RULE_FILE, DETAILS, "topic='flags'")
        self.reported(texts, "does not name topic='flag_details'")

    def test_a_rule_without_the_fallback_citation_is_reported(self):
        passage = rule_passage(self.texts[RULE_FILE])
        self.assertIn("INV-125", passage)
        texts = changed(self.texts, RULE_FILE, "produced what you present (INV-125)",
                        "produced what you present")
        self.reported(texts, "states no fallback")

    def test_a_rule_that_does_not_send_the_reader_to_the_row_form_is_reported(self):
        texts = changed(self.texts, RULE_FILE, "Choose flags from the compact list.",
                        "Read everything from the compact list.")
        self.reported(texts, "does not say to choose flags from the compact list")

    def test_a_site_with_no_pointer_is_reported(self):
        texts = changed(self.texts, PHASE_2B, POINTER, '→ "Flags"')
        self.reported(texts, "phase2b-discover.md makes a method-filter")

    def test_the_retired_module_6_sentence_is_reported(self):
        texts = dict(self.texts)
        texts[FIXTURE] = RETIRED_PARAGRAPH
        self.reported(texts, "fixture-for-issue-36/SKILL.md:1 reads ['source_file']")
        self.reported(texts, "fixture-for-issue-36/SKILL.md makes a method-filter")

    def test_the_same_sentence_with_its_row_named_is_not_reported(self):
        texts = dict(self.texts)
        texts[FIXTURE] = (RETIRED_PARAGRAPH + "The flag's own row,\n"
                          "`get_sdk_reference(topic='flags', filter='SZ_EXPORT_ALL_FLAGS')`, "
                          "carries it (`ground-rules.md` " + POINTER + ").\n")
        self.assertEqual([], field_problems(texts))
        self.assertEqual([], pointer_problems(texts))

    def test_a_note_that_drops_member_of_is_reported(self):
        texts = changed(self.texts, NOTE_FILE, '"member of".**', '"part of".**')
        self.reported(texts, "has no note saying")

    def test_an_undated_note_is_reported(self):
        note = next(unit for unit, _ in collapsed_blocks(self.texts[NOTE_FILE])
                    if is_the_note(unit))
        stamp = STAMP.search(COMMENT.sub(" ", note)).group(0)
        texts = changed(self.texts, NOTE_FILE, "⚠️ **Dated note (MCP " + stamp + ")",
                        "⚠️ **Note (")
        self.reported(texts, "carries no server version and date")

    def test_a_dependency_lookup_that_names_no_row_is_reported(self):
        row = "`get_sdk_reference(topic='flags', filter='%s')`: the row's" % DEPENDENT_FLAG
        texts = changed(self.texts, NOTE_FILE, row, "the compact list: the row's")
        self.reported(texts, "no sentence beside the `=` note")

    def test_a_marker_dated_apart_from_its_sentence_is_reported(self):
        marker = next(comment for comment in COMMENT.findall(self.texts[PHASE_D])
                      if TOKEN in comment and method_filters(comment))
        stamp = STAMP.search(marker)
        redated = marker.replace(stamp.group(2), "2001-01-01")
        self.reported(changed(self.texts, PHASE_D, marker, redated),
                      "version and date are not the ones its paragraph states")

    def test_a_marker_naming_another_origin_is_reported(self):
        marker = next(comment for comment in COMMENT.findall(self.texts[PHASE_D])
                      if TOKEN in comment and method_filters(comment))
        other = marker.replace("-->", "(fallback:some-other-origin) -->")
        self.reported(changed(self.texts, PHASE_D, marker, other), "name different origins")


if __name__ == "__main__":
    unittest.main()
