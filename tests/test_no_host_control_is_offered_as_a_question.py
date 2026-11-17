"""No 👉 question offers a session- or host-level control, and the rule that says so ships.

Twice on 2026-08-15, a bootcamper on plugin 0.5.0 was interrupted during the onboarding
preface -- with `👉 Do you have any questions before we get started?` pending and unanswered --
by the Claude Code host prompt "Set up auto mode for your environment?", the harness's own
dialog offering "Set it up" / "Not now" / "Don't show again".

⚠️ **That prompt is HOST-RENDERED, and this docstring said otherwise until 2026-08-15.** It
read "a bootcamper was asked about auto-mode", which frames it as the guide putting a question
to them. The second report quoted the dialog with its three native options -- UI chrome a model
cannot emit -- establishing that the guide originated nothing. No run has yet shown a guide
improvising a host-control question. INV-247 is prophylaxis against a hazard the reports
demonstrate (a bootcamper cannot tell an interface question from bootcamp content), not a
repair of an observed guide defect, and this file must not imply otherwise
(`specs/host-rendered-control-prompt-interrupts-a-pending-question.md`).

The rule is still worth having, and nothing on the books forbade the improvised case: the 👉
protocol governed a question's count (INV-251 since 2026-08-15; INV-005 at the time), shape (INV-008/INV-009/INV-051), placement
(INV-211/INV-224) and, for pinned gates, verbatim wording (INV-056) -- never its provenance. A
repo-wide search for `auto-mode`, `auto mode`, `auto-accept`, `permission mode`, `plan mode`,
`fast mode` and `bypass permissions` across `source/`, `hosts/`, `.claude/` and `tests/` matches
five files on 2026-11-16, and no match is a question the bootcamp asks: the rule text; the
Claude host value that text takes its examples from since issue #14; the Claude-only `host` row
of the feedback routing table, which quotes the observed prompt; `.claude/CLAUDE.md`, which
names the auto mode classifier; and this guard.

One thing also made such a question look native. Until issue #4 the bootcamp asked the
bootcamper to operate `/model` and `/effort` at module start, and INV-247 named that switch
as the one exception. ⚠️ **Issue #4 removed it (2026-11-16): the bootcamp now asks the
bootcamper to operate no interface control at all,** so this guard has no sanctioned slash
command left to allow, and the test that required the exception to survive now requires it
to stay gone. INV-247's registered wording still names the exception; it is superseded
separately, and `specs/INVARIANTS.md` is not read here.

Issue #14 (2026-11-16) moved the list of controls out of the rule's source text and out of this
file. Both rules now name the control by kind (a mode, a permission setting, a conversation
command) on every assistant, and name examples only from that assistant's own host values in
`hosts/<assistant>/host.json`: ``session_control_examples`` for the controls and
``dismissal_control_example`` for the dismissal affordance. Claude's are filled. An assistant
whose controls have not been verified declares both empty, and its rules still read as complete
sentences. Filling a value later changes no file under `source/`; the last two test classes here
check that on every assistant's built package, and on the source rendered with the values
emptied and with them filled.

Enforces **INV-247** — every 👉 question traces to a step in a shipped skill file, and no
session- or host-level control is presented as a bootcamp question.

⛔ **THIS GUARD HAS TWO LIMITS. BOTH ARE STATED HERE BECAUSE ONE DISCLOSURE READS AS ALL OF
THEM**, and a guard whose caveat looks complete is the pattern
`specs/coverage-reports-count-known-non-defects-as-hits.md` exists to stop.

1. **It cannot detect a runtime-improvised question.** The reported defect was a question that
   exists in **no file**; this test reads files. A clean run is not evidence the bootcamp can
   no longer ask about auto mode — that half is unreachable from a static check and belongs to
   `dry-run` phase 3.
2. **Its vocabulary check is a closed, dated list.** ``HOST_CONTROL`` is built from every
   assistant's ``session_control_examples`` host value (issue #14), and only Claude's is filled:
   nine literals naming the Claude Code CLI's affordances **as of 2026-08-15**. A control
   phrased in words absent from that list passes it, and so does every control of an assistant
   whose value is empty. The CLI ships independently of this plugin and an offline suite
   (INV-108) cannot notice a new one, so the list is a snapshot to extend, never a guarantee.

``test_no_pinned_question_offers_an_unsanctioned_slash_command`` exists because of limit 2 and
does not share it: it matches slash commands **structurally** and allows none, so a future
``/thinking`` or ``/verbose`` offered in a pinned question fails
without anyone having added it to a list. It is the assertion to prefer; the vocabulary check
survives only to catch non-slash phrasings ("auto mode", "permission mode").

Per **INV-246** the site set is derived by scanning every shipped Markdown file under
`source/`, never from a hardcoded list — a listed guard would certify the
files the author already thought of and miss a module added later, which is the only site
that matters.

Source spec: `specs/a-question-with-no-origin-in-a-skill-file-reached-the-bootcamper.md`.

Run:  python3 -m unittest discover -s tests
"""
import dataclasses
import json
import re
import unittest
from pathlib import Path

from _wrapped_text import blocks, match_lines
from _built import SOURCE_DIR, built, host_ids, load_host  # a package per assistant, from source/
from tools.bootcamp_build.render import render_text

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = built("claude")
GROUND_RULES_FILE = Path("skills") / "bootcamp-onboarding" / "ground-rules.md"
GROUND_RULES = PLUGIN / GROUND_RULES_FILE

#: Every assistant the bootcamp is built for, from `hosts/`.
HOSTS = tuple(host_ids())

#: The two host values issue #14 added to `vars` in every `hosts/<assistant>/host.json`: the
#: assistant's example controls, and the dismissal affordance its rule names. Each is text the
#: build places into the ground rules as written, so each is either empty or begins with the
#: space that separates it from the sentence it joins.
CONTROLS_VALUE = "session_control_examples"
DISMISSAL_VALUE = "dismissal_control_example"

#: A filled CONTROLS_VALUE: one space, then the controls in parentheses, separated by ", ".
CONTROLS_SHAPE = re.compile(r" \(([^()]+)\)")

# A pinned 👉 question: the pointer immediately followed by the bold question text. Prose that
# *talks about* 👉 questions (including the rule below) does not match, because there the
# pointer sits inside a sentence rather than ahead of a bolded question.
PINNED_QUESTION = re.compile("\U0001F449" + r"\s*\*\*")

# A slash command offered inside a pinned question. Structural, so it needs no vocabulary and
# does not expire: any new host command the CLI ships is caught the day it appears in a
# question. This is the assertion that actually enforces INV-247's class.
SLASH_COMMAND = re.compile(r"(?<![\w/])/([a-z][a-z0-9-]{1,20})\b")

#: The Claude-interface controls the bootcamp asks the bootcamper to operate: none. It held
#: `model` and `effort` until issue #4 removed the module-start switch.
SANCTIONED_SLASH = frozenset()


def named_controls(host_id):
    """The controls ``host_id``'s host value names, as written there; none when it is empty."""
    value = load_host(host_id).vars[CONTROLS_VALUE]
    if not value:
        return ()
    shape = CONTROLS_SHAPE.fullmatch(value)
    assert shape, ("hosts/%s/host.json: %s must be empty, or one space and then the controls in "
                   "parentheses separated by ', '; it is %r" % (host_id, CONTROLS_VALUE, value))
    return tuple(shape.group(1).split(", "))


def control_pattern(control):
    """The regex source that catches one control, from the way a host value writes it.

    A conversation command (a leading slash, in backticks or not) is matched whole. Any other
    control is matched by its first two words, joined by a hyphen, a space or nothing, without
    a plural's final "s" and with nothing required after them: `auto-accept edits` is caught as
    "auto accept" and `background tasks` as "background-task". That is every form the list
    this replaced matched, and no narrower.
    """
    control = control.strip("`")
    if control.startswith("/"):
        return re.escape(control) + r"\b"
    head = re.split(r"[-\s]+", control)[:2]
    if len(head[-1]) > 3:
        head[-1] = re.sub(r"(?<=[^s])s$", "", head[-1])
    return r"[-\s]?".join(re.escape(word) for word in head)


def host_control(controls):
    """One pattern, in any letter case, for ``controls``. An empty list would match everything."""
    sources = list(dict.fromkeys(control_pattern(control) for control in controls))
    assert sources, "no assistant's %s names a control, so the pattern would be empty" % CONTROLS_VALUE
    return re.compile("(?i)" + "|".join(sources))


# Session- or host-level controls: the bootcamper's assistant interface, not the bootcamp's to
# offer. The list is not held here (issue #14): it is built from every assistant's
# `session_control_examples` host value, so each assistant's list has one home, and today only
# Claude's is filled. `/model` and `/effort` are not listed because SLASH_COMMAND catches both
# structurally, and `test_no_question_offers_the_model_or_the_effort` names them.
#
# ⚠️ SNAPSHOT, NOT A CLOSED SET — dated 2026-08-15, the Claude Code CLI's affordances at that
# date. The CLI ships independently of this plugin, so this list expires silently and an
# offline suite cannot notice. EXTEND it in `hosts/claude/host.json` when a new control appears,
# and do not read a pass here as "no host control is offered" — SLASH_COMMAND above is the
# check that generalizes.
HOST_CONTROL = host_control(control for host in HOSTS for control in named_controls(host))

#: What HOST_CONTROL matched while it held its own list, kept as probes and not as the list
#: (issue #14): each control written with a space, with a hyphen, and in the shorter forms the
#: old pattern accepted. `bypass permissions` was in the guard only; the rule now names it too.
MATCHED_BEFORE_THE_LIST_MOVED = (
    "auto mode", "auto-mode", "automode",
    "auto-accept edits", "auto accept edits", "auto-accept", "autoaccept",
    "permission mode", "permission-mode",
    "plan mode", "plan-mode",
    "fast mode", "fast-mode",
    "bypass permissions", "bypass-permissions", "bypass permission",
    "background tasks", "background-tasks", "background task",
    "/compact", "/loop",
)

#: Each rule's sentence about the kinds of control, with the place the assistant's own value
#: goes (issue #14). With an empty value each is still a complete sentence.
RULE_1_SENTENCE = (
    "**never present a session- or host-level control as a bootcamp question** — a mode, a "
    "permission setting or a conversation command<examples>. Those belong to the bootcamper's "
    "<assistant> session, not to the bootcamp")
RULE_2_SENTENCE = (
    "whether they **ask about** a mode, a permission setting, a conversation command<examples> "
    "or any other setting belonging to their <assistant> session rather than to the bootcamp")
DISMISSAL_SENTENCE = (
    "**Do not name a dismissal affordance either**<example> — because directing them to a "
    "control that silences a host prompt is directing them to operate a <assistant>-interface "
    "control, and the bootcamp asks them to operate none (INV-247).")

#: What an example clause with nothing in it leaves behind: empty parentheses, a space before
#: closing punctuation, two dashes with nothing between, or a lead-in with nothing after it.
EMPTY_CLAUSE = re.compile(
    r"\(\s*\)|\(\s|\s[.,;:)]|—\s*—"
    r"|\b(?:such as|for example|for instance|including|e\.g\.|i\.e\.)[\s,]*[.;:)]")

# An affirmative claim that the plugin removes a host control. It cannot: a plugin ships
# skills, hooks and commands, and none of those reach the host's own affordances. Writing the
# claim anyway would paper over the scope change this spec had to make.
SUPPRESSION_CLAIM = re.compile(
    r"(?i)\b(?:the\s+)?(?:bootcamp|plugin|we)\s+(?:can\s+)?"
    r"(?:suppress(?:es)?|disable[sd]?|turn(?:s)?\s+off|hide[sd]?|override[sd]?)\s+"
    r"(?:the\s+)?(?:auto|permission|plan|fast|host)"
)


def shipped_markdown():
    """Every shipped Markdown file, discovered rather than listed (INV-246)."""
    return sorted(PLUGIN.rglob("*.md"))


def read(path):
    return path.read_text(encoding="utf-8")


def squash(text):
    return re.sub(r"\s+", " ", text)


def pinned_questions(text):
    """[(lineno, question)] for each pinned 👉 question, read across line wraps (#424).

    A question runs from its 👉 to the next 👉 in its Markdown block, or to the end of the
    block, with whitespace collapsed, and is reported at the line its 👉 is on. The line that
    holds the 👉 is added whole, as before #424, so nothing the line check saw is lost; what a
    wrap adds is the rest of a question that runs onto the next line.
    """
    spans = []
    for block in blocks(text):
        flat = " ".join(" ".join(line for _n, line in block).split())
        starts = [m.start() for m in PINNED_QUESTION.finditer(flat)]
        for a, b in zip(starts, starts[1:] + [len(flat)]):
            nxt = flat.find("\U0001F449", a + 1)
            spans.append(flat[a:nxt if a < nxt < b else b])
    lines = match_lines(text, PINNED_QUESTION)
    assert len(lines) == len(spans), "match_lines and the block scan disagree"
    raw = text.split("\n")
    return [(n, raw[n - 1] + " " + span) for n, span in zip(lines, spans)]


def the_two_rules(text):
    """(the 👉 provenance rule, the any-time host-control entry), each collapsed to one line."""
    flat = squash(text)
    first = re.search(r"⛔ \*\*Every \S+ question traces to a step in a shipped skill file.*?"
                      r"the settings it never asks about\.", flat)
    second = re.search(r"\*\*A host control the bootcamper raises — in any form:\*\*.*?"
                       r"\(INV-247\)\.", flat)
    assert first and second, "the two INV-247 rules were not found in ground-rules.md"
    return first.group(0), second.group(0)


def sentence(template, assistant, value):
    """``template`` as one assistant's package words it, with ``value`` as its host value."""
    return (template.replace("<examples>", value).replace("<example>", value)
            .replace("<assistant>", assistant))


def section(text, heading):
    """The body of one `## ` section, so a rule can be required WHERE it binds."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == heading:
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    return squash("\n".join(lines[i:j]))
            return squash("\n".join(lines[i:]))
    raise AssertionError("heading not found in ground-rules.md: %r" % heading)


class NoShippedQuestionOffersAHostControl(unittest.TestCase):
    def test_the_corpus_is_actually_being_scanned(self):
        """A guard that silently matched nothing would pass forever."""
        files = shipped_markdown()
        self.assertGreater(len(files), 20,
                           "the shipped Markdown sweep found almost nothing — the corpus "
                           "moved and this guard is now inspecting an empty set")
        questions = [(p, n, line)
                     for p in files
                     for n, line in enumerate(read(p).splitlines(), 1)
                     if PINNED_QUESTION.search(line)]
        self.assertGreater(len(questions), 50,
                           "the pinned-question pattern matched almost nothing — the 👉 "
                           "question form changed and this guard no longer sees questions")

    def test_no_pinned_question_names_a_session_or_host_control(self):
        offenders = []
        for path in shipped_markdown():
            for n, question in pinned_questions(read(path)):
                if HOST_CONTROL.search(question):
                    rel = path.relative_to(REPO_ROOT)
                    offenders.append("%s:%d: %s" % (rel, n, question.strip()[:140]))
        self.assertEqual(
            [], offenders,
            "a 👉 question offers a control that belongs to the bootcamper's Claude session, "
            "not to the bootcamp (INV-247). The bootcamp asks them to operate no "
            "Claude-interface control:\n  "
            + "\n  ".join(offenders))

    def test_no_pinned_question_offers_an_unsanctioned_slash_command(self):
        """The open-ended half of INV-247 — no vocabulary list, so it does not expire.

        INV-247 governs a CLASS ("a session- or host-level control"); a literal list can only
        ever be a snapshot of a CLI that ships separately from this plugin. Slash commands are
        that class's structural signature, so reject every one — a control this repo has
        never heard of fails the day it appears in a question.
        """
        offenders = []
        for path in shipped_markdown():
            for n, question in pinned_questions(read(path)):
                # The question from its 👉 on, as before #424: text ahead of the 👉 on its line
                # is not the question.
                question = question[PINNED_QUESTION.search(question).start():]
                for cmd in SLASH_COMMAND.findall(question):
                    if cmd not in SANCTIONED_SLASH:
                        offenders.append(
                            "%s:%d: /%s — %s"
                            % (path.relative_to(REPO_ROOT), n, cmd, question.strip()[:110]))
        self.assertEqual(
            [], offenders,
            "a 👉 question offers a slash command. The bootcamp asks the bootcamper to "
            "operate no Claude-interface control (INV-247, #4); every one belongs to their "
            "session:\n  "
            + "\n  ".join(offenders))

    def test_no_question_offers_the_model_or_the_effort(self):
        """The former exception stays gone (#4): no 👉 question is about either setting.

        This test used to require the opposite, so that the guard could not pass by deleting
        the rule's subject. Issue #4 deleted the subject on purpose, on every assistant.
        """
        asked = ["%s:%d: %s" % (path.relative_to(REPO_ROOT), n, question.strip()[:110])
                 for path in shipped_markdown()
                 for n, question in pinned_questions(read(path))
                 if re.search(r"(?i)/model|/effort|reasoning effort|\bmodel and effort\b",
                              question[PINNED_QUESTION.search(question).start():])]
        self.assertEqual([], asked,
                         "a 👉 question offers a model or effort change. The bootcamp never "
                         "asks for one (#4):\n  " + "\n  ".join(asked))

    def test_a_question_offering_the_model_or_the_effort_is_caught(self):
        """Negative control (INV-265): the pinned question issue #4 removed, wrapped."""
        retired = ("👉 **Would you like to switch to `/model opus` +\n`/effort high` for this "
                   "module?** (Recommended for best value.)\n")
        (n, question), = pinned_questions(retired)
        self.assertEqual(1, n)
        self.assertEqual({"model", "effort"}, set(SLASH_COMMAND.findall(question)))
        self.assertFalse(set(SLASH_COMMAND.findall(question)) & SANCTIONED_SLASH)

    def test_a_wrapped_question_offering_a_host_control_is_caught(self):
        """Negative control (#424): the control is named on the line the question wraps onto."""
        wrapped = ("👉 **Before we load, would you like to switch on\nauto mode, or "
                   "run `/compact` first?**\n")
        (n, question), = pinned_questions(wrapped)
        self.assertEqual(1, n)
        self.assertTrue(HOST_CONTROL.search(question))
        self.assertIn("compact", SLASH_COMMAND.findall(question))
        # The old line-at-a-time check, kept only to show the fixture is the hard case.
        first = wrapped.split("\n")[0]
        self.assertFalse(HOST_CONTROL.search(first))
        self.assertEqual([], SLASH_COMMAND.findall(first))

    def test_a_question_followed_by_prose_about_the_host_is_not_flagged(self):
        """Must-not-flag (INV-282): the next block is not the question."""
        text = ("👉 **Shall we load the sample now?**\n\n"
                "(Auto mode belongs to your Claude session; the bootcamp never offers it.)\n")
        self.assertEqual([], [n for n, q in pinned_questions(text) if HOST_CONTROL.search(q)])

    def test_a_wrapped_suppression_claim_is_caught(self):
        """Negative control (#424): "the plugin" ends line 1 and "disables auto" begins line 2."""
        wrapped = "During the bootcamp the plugin\ndisables auto mode for you.\n"
        self.assertEqual([1], match_lines(wrapped, SUPPRESSION_CLAIM))
        self.assertFalse(any(SUPPRESSION_CLAIM.search(l) for l in wrapped.split("\n")))

    def test_no_shipped_file_claims_the_plugin_suppresses_a_host_control(self):
        offenders = []
        for path in shipped_markdown():
            text = read(path)
            for n in match_lines(text, SUPPRESSION_CLAIM):
                rel = path.relative_to(REPO_ROOT)
                offenders.append("%s:%d: %s" % (rel, n, text.split("\n")[n - 1].strip()[:140]))
        self.assertEqual(
            [], offenders,
            "a shipped file claims the bootcamp removes a host control. It cannot — a plugin "
            "ships skills, hooks and commands, none of which reach the host's own "
            "affordances — and the claim would hide the scope this spec had to narrow to:\n  "
            + "\n  ".join(offenders))


class ThisGuardDisclosesWhatItCannotSee(unittest.TestCase):
    """A guard that over-claims certifies what it never tested.

    Both limits are asserted because the file previously stated one of them emphatically and
    was silent on the other, which reads as completeness — the reader meets a ⛔ caveat and
    reasonably concludes it is *the* caveat.
    """

    #: ⛔ Assert against the module DOCSTRING, never this file's source text.
    #:
    #: An earlier version read `Path(__file__)` and three mutations ESCAPED: each assertion's
    #: own regex literal lives in that source, so every check matched its own pattern string
    #: and passed with the docstring gutted. A guard that greps the file it is written in
    #: certifies itself. `__doc__` contains the prose and not the patterns, so the needle can
    #: only come from the disclosure. The snapshot-date check below still reads source — it
    #: must, since that marker is a `#` comment — but its pattern uses `\d{4}` escapes and so
    #: cannot match itself.
    def setUp(self):
        self.doc = __doc__ or ""

    def test_the_runtime_limit_is_disclosed(self):
        self.assertRegex(
            self.doc, r"(?i)cannot detect a runtime-improvised question",
            "the docstring no longer says this guard cannot see a question improvised at "
            "runtime — the reported defect existed in no file, so a clean run would read as "
            "proof of something never tested")

    def test_the_vocabulary_limit_is_disclosed(self):
        self.assertRegex(
            self.doc, r"(?i)vocabulary check is a closed, dated list",
            "the docstring no longer says the HOST_CONTROL match is a closed list, so a "
            "control phrased outside it passes while the guard reads as enforcing the class "
            "INV-247 actually governs")

    def test_the_snapshot_list_carries_its_date(self):
        self.assertRegex(
            read(Path(__file__)), r"SNAPSHOT, NOT A CLOSED SET — dated \d{4}-\d{2}-\d{2}",
            "HOST_CONTROL lost its dated snapshot marker; an undated list of a third party's "
            "vocabulary cannot be told from a complete one")

    def test_the_open_ended_check_is_named_as_the_one_to_prefer(self):
        self.assertRegex(
            self.doc, r"(?i)It is the assertion to prefer",
            "the docstring no longer points the reader from the expiring vocabulary check to "
            "the structural one, so a maintainer extending the list would not learn there is "
            "a check that needs no extending")


class TheRuleShipsWhereItBinds(unittest.TestCase):
    def setUp(self):
        self.text = read(GROUND_RULES)

    def test_the_protocol_closes_the_question_set(self):
        protocol = section(self.text, "## Conversation protocol (the 👉 rules)")
        self.assertRegex(
            protocol, r"(?i)traces to a step in a shipped skill file",
            "the 👉 protocol still governs only a question's count, shape and placement — "
            "nothing requires a question to come from a step in a skill file (INV-247)")
        self.assertRegex(
            protocol, r"(?i)never present a session- or host-level control as a bootcamp question",
            "the protocol does not name the class of question that produced this defect")
        self.assertRegex(
            protocol, r"INV-247",
            "the closed-question-set rule ships without its invariant ID, so a later editor "
            "cannot look up why it is there (INV-183)")

    def test_the_protocol_says_answering_a_bootcamper_question_is_not_originating_one(self):
        protocol = section(self.text, "## Conversation protocol (the 👉 rules)")
        self.assertRegex(
            protocol, r"(?i)answering a question the bootcamper asks is not originating one",
            "the rule reads as forbidding the guide to respond when a bootcamper raises a "
            "host control, which would strand them at a pending gate")

    def test_the_two_turn_shapes_are_stated_as_alternatives(self):
        """One sentence said re-present, the next called a counter-question the turn's single 👉.

        Nothing said they were alternatives, so following both ends the turn on TWO 👉 — the
        violation this file itself calls the #1 bootcamper complaint, fourteen lines above.
        """
        protocol = section(self.text, "## Conversation protocol (the 👉 rules)")
        self.assertRegex(
            protocol, r"(?i)ends one of \*\*two\*\* ways, never both",
            "the host-control handling clause does not state that re-presenting the pending "
            "question and asking a clarifying counter-question are alternatives, so a guide "
            "following both ends the turn on two 👉 (INV-251)")
        self.assertRegex(
            protocol, r"(?i)doing both ends the turn on two .{0,4}, which INV-251 forbids",
            "the clause does not name the consequence of doing both, so the alternation reads "
            "as a stylistic preference rather than a rule")
        self.assertRegex(
            protocol, r"(?i)the pending question waits for the turn \*\*after\*\* it",
            "nothing says where the pending question goes when a counter-question takes the "
            "turn's 👉 — a deferral with no destination is a deletion (INV-007)")

    def test_the_any_time_controls_preamble_does_not_read_as_an_INV_005_exemption(self):
        """"Never count against the one-question-per-turn rule" compounded the ambiguity."""
        controls = section(self.text, "## Any-time bootcamper controls")
        self.assertRegex(
            controls, r"(?i)invoking\*\* one is not a bootcamp question",
            "the preamble does not distinguish the bootcamper INVOKING a control from the "
            "turn's 👉 budget, so it reads as a blanket exemption from INV-251's count")
        self.assertRegex(
            controls, r"(?i)the turn still ends on \*\*exactly one\*\*",
            "the preamble does not restate that INV-251 still binds, which is the reading that "
            "let a host-control detour carry a second 👉")

    def test_the_rule_states_that_it_has_no_exception(self):
        """The module-start switch was the one exception until issue #4 removed it."""
        protocol = section(self.text, "## Conversation protocol (the 👉 rules)")
        self.assertRegex(
            protocol, r"(?i)\*\*There is no exception:\*\* the bootcamp asks the bootcamper to "
                      r"operate no Claude-interface control at all",
            "the closed-question-set rule no longer says it has no exception, so a reader "
            "adding an interface question never meets the limit (INV-247)")
        self.assertNotRegex(
            squash(self.text), r"(?i)the single exception is|ONLY Claude-interface control "
                               r"the bootcamp asks",
            "ground-rules still names an interface control the bootcamp asks the bootcamper "
            "to operate; issue #4 left none")

    def test_a_bootcamper_question_about_a_host_control_has_a_stated_answer(self):
        controls = section(self.text, "## Any-time bootcamper controls")
        self.assertRegex(
            controls, r"(?i)a host control the bootcamper raises",
            "the any-time controls have no entry for a bootcamper raising a host "
            "control, which is what happened here — at a pending gate (INV-247)")
        self.assertRegex(
            controls, r"(?i)one sentence",
            "the handling line does not bound the answer, so a session setting can grow into "
            "a detour of its own")
        self.assertRegex(
            controls, r"(?i)re-present the pending .{0,4} question verbatim",
            "the handling line does not return the bootcamper to the pending question, which "
            "is the half the reported run actually lost")

    def test_the_entry_fires_when_a_host_prompt_merely_APPEARS(self):
        """The reported runs were not a bootcamper ASKING — a dialog appeared at them.

        Scoped `if the bootcamper asks`, the entry misses the case that actually happened
        twice on 2026-08-15: the host drew its own prompt over a pending 👉 and nobody asked
        anything (`specs/host-rendered-control-prompt-interrupts-a-pending-question.md`).
        """
        controls = section(self.text, "## Any-time bootcamper controls")
        self.assertRegex(
            controls, r"(?i)prompt for one appeared over the bootcamp",
            "the host-control entry still fires only when the bootcamper ASKS about a "
            "control; a host-rendered prompt appearing unbidden — the observed case — "
            "reaches no branch (INV-247)")

    def test_the_answer_does_not_name_a_dismissal_affordance(self):
        """Maintainer decision, 2026-08-15: the answer stays silent on how to dismiss.

        The dialog offers "Don't show again". Naming it would direct the bootcamper to
        operate a Claude-interface control, and the bootcamp asks them to operate none
        (INV-247, #4). The prohibition must ship, not merely be honored today.
        """
        controls = section(self.text, "## Any-time bootcamper controls")
        self.assertRegex(
            controls, r"(?i)do not name a dismissal affordance",
            "the handling line no longer forbids naming a dismissal control, so a guide may "
            "point the bootcamper at “Don't show again” — an interface control "
            "the bootcamp is not permitted to direct (INV-247)")

    def test_the_interruption_list_names_a_host_rendered_prompt(self):
        """A four-item list of conversational interruptions is read as the set.

        The recovery rule says "any interruption", then enumerates a compaction, a session
        boundary, the feedback detour and a tangent — all conversational, all visible to the
        guide. A host dialog is neither, and INV-205's own maintenance note records what
        happens to an enumeration generalized from the instances its author had seen.
        """
        controls = section(self.text, "## Any-time bootcamper controls")
        self.assertRegex(
            controls, r"(?i)host-rendered prompt from their Claude interface",
            "the interruption list does not name a host-rendered prompt, leaving the observed "
            "case to a reader's generalization from four conversational examples (INV-007)")

    def test_no_shipped_text_claims_the_GUIDE_asked_about_auto_mode(self):
        """No run has shown that. INV-247 is prophylaxis, not a repair of an observed defect.

        Both 2026-08-15 reports describe a host-rendered dialog; the second quoted its three
        native options, which a model cannot emit. Text implying the guide asked overstates
        the evidence for a rule that stands perfectly well without it.
        """
        self.assertNotRegex(
            squash(self.text), r"(?i)bootcamper was asked about .{0,4}auto.?mode",
            "ground-rules.md again states that a bootcamper WAS ASKED about auto mode, "
            "implying the guide originated it — the prompt is host-rendered "
            "(`specs/host-rendered-control-prompt-interrupts-a-pending-question.md`)")
        self.assertRegex(
            squash(self.text), r"(?i)that prompt is host-rendered",
            "ground-rules.md no longer records that the observed prompt was host-rendered, "
            "so the next editor re-derives it as a guide defect")


class TheCorrectedAttributionIsDisclosed(unittest.TestCase):
    """This guard asserted the wrong attribution for hours; the correction must stick.

    Asserted against the module ``__doc__`` for the reason the sibling disclosure class
    documents at length: this file's own regex literals live in its source, so a check that
    read ``Path(__file__)`` would match its own pattern and pass with the prose gutted.
    """

    #: Squashed, unlike the sibling class: these needles are phrases rather than single
    #: tokens, so a rewrap of the docstring would otherwise break the assertion without
    #: the disclosure having changed at all.
    def setUp(self):
        self.doc = squash(__doc__ or "")

    def test_the_docstring_records_the_prompt_as_host_rendered(self):
        #: ⛔ Anchored to the CLAIM ("that prompt is host-rendered"), not the bare token.
        #: A mutation escaped this assertion during negative-control: the docstring also
        #: cites `specs/host-rendered-control-prompt-…md`, so `host-rendered` alone still
        #: matched with the claim gutted — the filename certified the sentence.
        self.assertRegex(
            self.doc, r"(?i)that prompt is host-rendered",
            "the docstring no longer says the observed prompt was host-rendered — it "
            "previously read “a bootcamper was asked”, which frames a harness dialog "
            "as a question the guide put to them")

    def test_the_docstring_says_no_guide_defect_has_been_OBSERVED(self):
        self.assertRegex(
            self.doc, r"(?i)no run has yet shown a guide improvising",
            "the docstring no longer distinguishes the rule (prophylaxis against a real "
            "hazard) from an observed guide defect (none recorded), which is the "
            "over-claim `coverage-reports-count-known-non-defects-as-hits` exists to stop")


class TheWordListComesFromTheHostValues(unittest.TestCase):
    """``HOST_CONTROL`` holds no list of its own (issue #14) and lost nothing in the move."""

    def test_it_still_matches_everything_its_own_list_matched(self):
        for phrase in MATCHED_BEFORE_THE_LIST_MOVED:
            for form in (phrase, phrase.upper(), phrase.title()):
                with self.subTest(form=form):
                    question = "\U0001F449 **Shall I switch on %s before we load?**" % form
                    self.assertRegex(
                        question, HOST_CONTROL,
                        "the guard matched this while it held its own list, and no longer "
                        "does: a control left hosts/claude/host.json, or the pattern built "
                        "from the host values is narrower than the one it replaced")

    def test_it_is_built_from_every_assistants_value_and_nothing_else(self):
        named = [control for host in HOSTS for control in named_controls(host)]
        self.assertEqual(host_control(named).pattern, HOST_CONTROL.pattern)
        for control in named:
            with self.subTest(control=control):
                self.assertRegex(control.strip("`"), HOST_CONTROL)

    def test_a_control_added_to_a_value_is_matched_without_a_change_here(self):
        """The builder knows no control: two invented ones are caught, a real one is not."""
        invented = host_control(["turbo mode", "`/zoom`"])
        for form in ("turbo mode", "Turbo-Mode", "TURBOMODE", "/zoom", "run `/ZOOM` first"):
            with self.subTest(form=form):
                self.assertRegex(form, invented)
        for form in ("auto mode", "/compact", "/zoomed", "turbo"):
            with self.subTest(form=form):
                self.assertNotRegex(form, invented)

    def test_a_lookalike_is_not_matched(self):
        """Must-not-flag (INV-282): a command's longer neighbor, and the words apart."""
        for text in ("/compaction", "/loops", "a plan for this mode", "permission to use the mode",
                     "tasks that run in the background", "accept the automatic mapping"):
            with self.subTest(text=text):
                self.assertNotRegex(text, HOST_CONTROL)

    def test_an_empty_word_list_is_refused(self):
        """An alternation of nothing matches every question, and a guard that did would fail
        every question for the wrong reason."""
        with self.assertRaises(AssertionError):
            host_control([])


class EachPackageNamesOnlyItsOwnAssistantsControls(unittest.TestCase):
    """Issue #14, on what each assistant installs: the rule by kind everywhere, examples only
    from that assistant's own host value."""

    @classmethod
    def setUpClass(cls):
        cls.text, cls.rules, cls.assistant, cls.values = {}, {}, {}, {}
        for host in HOSTS:
            raw = read(built(host) / GROUND_RULES_FILE)
            cls.text[host] = squash(raw)
            cls.rules[host] = the_two_rules(raw)
            variables = load_host(host).vars
            cls.assistant[host] = variables["assistant"]
            cls.values[host] = (variables[CONTROLS_VALUE], variables[DISMISSAL_VALUE])

    def test_every_assistant_declares_both_values_in_the_shape_the_rules_need(self):
        self.assertEqual(5, len(HOSTS))
        for host in HOSTS:
            with self.subTest(host=host):
                path = REPO_ROOT / "hosts" / host / "host.json"
                variables = json.loads(path.read_text(encoding="utf-8"))["vars"]
                for name in (CONTROLS_VALUE, DISMISSAL_VALUE):
                    self.assertIn(name, variables, "%s does not declare %s" % (path, name))
                    self.assertIsInstance(variables[name], str)
                controls = named_controls(host)  # refuses a filled value in any other shape
                self.assertEqual(bool(variables[CONTROLS_VALUE]), bool(controls))
                for control in controls:
                    self.assertEqual(control.strip(), control)
                    self.assertTrue(control.strip("`"), "an empty control in %s" % path)
                self.assertEqual(len(set(controls)), len(controls), "a control is listed twice")
                dismissal = variables[DISMISSAL_VALUE]
                if dismissal:
                    self.assertRegex(
                        dismissal, r"\A \S(?:.*\S)?\Z",
                        "%s must be empty, or begin with the one space that separates it from "
                        "the sentence it joins and end without one" % DISMISSAL_VALUE)

    def test_both_rules_name_the_three_kinds_of_control_in_every_package(self):
        for host in HOSTS:
            with self.subTest(host=host):
                first, second = self.rules[host]
                self.assertIn("a mode, a permission setting or a conversation command", first)
                self.assertIn("a mode, a permission setting, a conversation command", second)
                self.assertIn("or any other setting belonging to their %s session"
                              % self.assistant[host], second)

    def test_each_rule_is_a_complete_sentence_around_the_assistants_own_value(self):
        """Empty or filled, the value sits in a sentence that reads whole on that assistant."""
        for host in HOSTS:
            with self.subTest(host=host):
                first, second = self.rules[host]
                controls, dismissal = self.values[host]
                assistant = self.assistant[host]
                self.assertIn(sentence(RULE_1_SENTENCE, assistant, controls), first)
                self.assertIn(sentence(RULE_2_SENTENCE, assistant, controls), second)
                self.assertIn(sentence(DISMISSAL_SENTENCE, assistant, dismissal), second)
                for rule in (first, second):
                    self.assertNotRegex(rule, EMPTY_CLAUSE,
                                        "a rule in the %s package has an empty clause" % host)

    def test_a_package_with_no_examples_states_the_kinds_and_names_nothing(self):
        """The four assistants whose controls are not verified, today; any empty value, later."""
        every = [control for host in HOSTS for control in named_controls(host)]
        for host in HOSTS:
            if any(self.values[host]):
                continue
            with self.subTest(host=host):
                first, second = self.rules[host]
                self.assertIn("or a conversation command. Those belong to the bootcamper's", first)
                self.assertIn("a conversation command or any other setting belonging to", second)
                self.assertIn("**Do not name a dismissal affordance either** — because", second)
                for control in every:
                    self.assertNotRegex(first + " " + second, "(?i)" + control_pattern(control))

    def test_a_package_names_every_control_in_its_own_value_in_both_rules(self):
        for host in HOSTS:
            for control in named_controls(host):
                with self.subTest(host=host, control=control):
                    first, second = self.rules[host]
                    self.assertIn(control, first)
                    self.assertIn(control, second)

    def test_the_claude_package_keeps_its_examples_and_the_dismissal_affordance(self):
        """True of the Claude rendering alone: its values are the ones that are verified."""
        controls = named_controls("claude")
        self.assertTrue(controls, "hosts/claude/host.json names no control")
        first, second = self.rules["claude"]
        for control in controls:
            with self.subTest(control=control):
                self.assertIn(control, first)
                self.assertIn(control, second)
        self.assertIn("**Do not name a dismissal affordance either** — not \"Don't show again\", "
                      "not any other — because", second)

    def test_a_control_is_named_only_in_a_package_whose_own_value_lists_it(self):
        """Nothing is inferred from another assistant's list, anywhere in the ground rules."""
        checked = 0
        for host in HOSTS:
            own = {control_pattern(control) for control in named_controls(host)}
            for other in HOSTS:
                for control in named_controls(other):
                    pattern = control_pattern(control)
                    if pattern in own:
                        continue
                    checked += 1
                    with self.subTest(package=host, control=control, listed_by=other):
                        self.assertNotRegex(
                            self.text[host], "(?i)" + pattern,
                            "the %s package's ground rules name a control only %s's host "
                            "value lists" % (host, other))
        self.assertTrue(checked, "no assistant lists a control another does not, so this "
                                 "compared nothing")

    def test_dont_show_again_ships_only_where_the_dismissal_value_names_it(self):
        affordance = re.compile(r"(?i)don['\u2019]t show again")
        for host in HOSTS:
            with self.subTest(host=host):
                self.assertEqual(bool(affordance.search(self.values[host][1])),
                                 bool(affordance.search(self.text[host])))
        self.assertRegex(self.text["claude"], affordance)
        without = [host for host in HOSTS if not affordance.search(self.text[host])]
        self.assertTrue(without, "every package names the affordance, so nothing was excluded")


class AValueIsFilledOrEmptiedWithoutTouchingTheSource(unittest.TestCase):
    """Issue #14's scope: "Filling an assistant's host value later needs no change to `source/`".

    The source is rendered for every assistant with the two values emptied, then with invented
    ones, so the check holds on all five whichever of them are filled today.
    """

    SOURCE = SOURCE_DIR / GROUND_RULES_FILE

    def rules_with(self, host_id, controls, dismissal):
        host = load_host(host_id)
        host = dataclasses.replace(
            host, vars={**host.vars, CONTROLS_VALUE: controls, DISMISSAL_VALUE: dismissal})
        text = render_text(read(self.SOURCE), host, str(self.SOURCE), directives=True,
                           known_hosts=set(HOSTS))
        return the_two_rules(text), host.vars["assistant"]

    def test_the_source_places_each_value_and_names_no_control_itself(self):
        source = read(self.SOURCE)
        self.assertEqual(2, source.count("{{host.%s}}" % CONTROLS_VALUE))
        self.assertEqual(1, source.count("{{host.%s}}" % DISMISSAL_VALUE))
        first, second = the_two_rules(source)
        self.assertIn("{{host.%s}}" % CONTROLS_VALUE, first)
        self.assertIn("{{host.%s}}" % CONTROLS_VALUE, second)
        self.assertIn("{{host.%s}}" % DISMISSAL_VALUE, second)
        for rule in (first, second):
            self.assertNotRegex(rule, HOST_CONTROL)
            self.assertNotRegex(rule, r"(?i)don['\u2019]t show again")

    def test_with_both_values_empty_every_assistants_rules_are_complete_sentences(self):
        every = [control for host in HOSTS for control in named_controls(host)]
        for host in HOSTS:
            with self.subTest(host=host):
                (first, second), assistant = self.rules_with(host, "", "")
                self.assertIn(sentence(RULE_1_SENTENCE, assistant, ""), first)
                self.assertIn(sentence(RULE_2_SENTENCE, assistant, ""), second)
                self.assertIn(sentence(DISMISSAL_SENTENCE, assistant, ""), second)
                for rule in (first, second):
                    self.assertNotRegex(rule, EMPTY_CLAUSE)
                    self.assertNotRegex(rule, r"(?i)don['\u2019]t show again")
                    for control in every:
                        self.assertNotRegex(rule, "(?i)" + control_pattern(control))

    def test_with_both_values_filled_every_assistants_rules_name_them(self):
        controls = " (turbo mode, `/zoom`)"
        dismissal = " — not \"Never ask me\", not any other"
        for host in HOSTS:
            with self.subTest(host=host):
                (first, second), assistant = self.rules_with(host, controls, dismissal)
                self.assertIn(sentence(RULE_1_SENTENCE, assistant, controls), first)
                self.assertIn(sentence(RULE_2_SENTENCE, assistant, controls), second)
                self.assertIn(sentence(DISMISSAL_SENTENCE, assistant, dismissal), second)
                for rule in (first, second):
                    self.assertNotRegex(rule, EMPTY_CLAUSE)

    def test_an_empty_clause_is_caught(self):
        """Negative control (INV-265): what each rule would read like with the clause left in."""
        for broken in ("or a conversation command (). Those belong",
                       "or a conversation command ( ). Those belong",
                       "or a conversation command . Those belong",
                       "a conversation command , or any other setting",
                       "a conversation command, such as . Those belong",
                       "a conversation command (for example ) or any other setting",
                       "a dismissal affordance either** — — because"):
            with self.subTest(broken=broken):
                self.assertRegex(broken, EMPTY_CLAUSE)


if __name__ == "__main__":
    unittest.main()
