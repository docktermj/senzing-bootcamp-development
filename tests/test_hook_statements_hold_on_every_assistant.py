"""What the bootcamp says about a hook is true on every assistant (#29).

The 2026-11-17 production-readiness audit found two texts stating opposite facts about the
same hooks. In the four packages that carry `host-rules.md` safeguards, a fallback said
"Nothing checks a write before it happens", while `ground-rules.md` said, with no condition,
that a hook enforces the write gate, folds the recap and stops containers. Each side was false
somewhere: the build gives every fallback to every assistant whose hooks are not guaranteed,
so "Nothing checks a write" was also said where the assistant has an event for the write gate,
and the ground rules said the hook acts on assistants where it does not run. The shared text
also named one assistant's hook events.

Issue #29 settled three things, and this file holds a test for each:

1. **Fallback wording follows the mapping.** "The mapping" is `hooks.events` in
   `hosts/<assistant>/host.json`, with `hooks.advisory` beside it. A fallback that says whether
   a hook does its job has two wordings: *nothing does this* where the assistant has no event
   for the hook or lists the event as advisory, and *a hook does this when it runs, but it may
   not run here* where it has one. Both end in the same instruction. The wording is chosen in
   `source/hooks/fallbacks/` by a `host:only` block and a `host:except` block naming the same
   assistants; the build tool is unchanged. So nothing but this file keeps a marker and a
   mapping in step: `FallbackWordingFollowsTheMapping` builds each package and compares what
   its `host-rules.md` says with that assistant's mapping, and `TheMarkersNameTheMappedAssistants`
   does the same for the marker lists, for every assistant including one whose package
   carries no fallback today.
2. **Shared text states no hook action without a condition.** Every passage under
   `source/skills/` that said what a hook does now holds whether or not a hook backs it.
   `NoRetiredSentenceIsBack` pins the sentences the issue listed, and
   `NoUnconditionalHookStatement` scans every skill file for a hook stated as acting with no
   condition in the same sentence.
3. **Event names are an assistant's own or none.** Shared text names a hook by what it does or
   by its script. `SharedTextNamesNoHookEvent` scans `source/skills/` and
   `source/hooks/fallbacks/` for every event name in any assistant's mapping, and
   `APackageNamesOnlyItsOwnEvents` scans each built package for a name that is not in its own.

The three rules, one line each:

⛔ **(INV-450) A fallback says that nothing does a hook's job only where the assistant's mapping has no event for the hook or lists it as advisory, and says that the hook may not run where the mapping has one.**

⛔ **(INV-451) No file under `source/skills/` says without a condition that a hook does something.**

⛔ **Shared text names no hook event, and the Markdown of a built package names a hook event only when the event is in that assistant's own mapping.**

Each line is queued as a `DEFERRED INVARIANT` block in this issue's entry of
`specs/IMPLEMENTED.md`, awaiting the maintainer's sign-off. Until then only this file holds
them.

Every check is a pure function that returns a list of problems, so each one also runs on a
changed copy of the real text or the real mapping as its negative control, and the control
asserts the check reports it.

Phrase checks collapse whitespace (INV-346), so a phrase wrapped across lines still matches.
The sites are found by scanning (INV-246): every fallback the declaration lists, every
Markdown file under `source/skills/`, every Markdown file in each built package.

What this cannot establish:

- That a hook runs on a real assistant. What is true for an assistant is taken from its
  mapping; nothing here runs one, and nothing is recorded in `hosts/<assistant>/checks.json`.
- Event names outside Markdown. The package scan reads the Markdown a guide reads. The hook
  scripts and the hook adapter carry the canonical event names as protocol values in every
  package, and a hook configuration file carries its own assistant's names by design.
- An unconditional statement worded in a way `HOOK_ACTS` does not know. It is a closed list of
  shapes taken from the sentences the audit found, to extend when a new shape appears.
- The event name `Stop` used as an ordinary word. It is counted only in backticks or directly
  before "hook", as the issue decided.

Stdlib only; packages are built by `_built.built` (INV-108).

Source issue: #29. Invariant: INV-003.

Run:  python3 -m unittest discover -s tests
"""
import copy
import dataclasses
import re
import unittest
from pathlib import Path

from _built import SOURCE_DIR, built, host_ids, load_declaration, load_host
from tools.bootcamp_build.emit import FALLBACK_DIR, HOST_RULES, fallback_scripts
from tools.bootcamp_build.render import RenderStats, render_text

SKILLS = SOURCE_DIR / "skills"
FALLBACKS = SOURCE_DIR / FALLBACK_DIR
ONBOARDING = "bootcamp-onboarding/"

#: Every assistant the bootcamp is built for, from ``hosts/``.
HOSTS = tuple(host_ids())
DECLARATION = load_declaration(SOURCE_DIR)

#: The three things a fallback can say about its hook.
NOTHING = "nothing does this"
MAY_NOT_RUN = "the hook may not run"
SILENT = "no statement"

#: The fallbacks that state whether a hook does their job (#29). The other fallbacks say
#: nothing about it and keep their text; one that starts to is checked like these.
STATEMENT_FALLBACKS = ("write-gate", "stop-nudge", "precompact-recap", "session-end")

#: "Nothing checks a write before it happens." A sentence that opens with "Nothing".
SAYS_NOTHING = re.compile(r"(?:^|(?<=[.:!?]) )Nothing\b")
#: "When it runs, a hook checks a write before it happens, but it may not run here."
SAYS_MAY_NOT_RUN = re.compile(r"\ba hook\b[^.]*\bmay not run\b")


def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    """``text`` with every run of whitespace collapsed, so a wrapped phrase still matches."""
    return " ".join(text.split())


# --- 1. Fallback wording follows the mapping -----------------------------------------------

def hook_events(declaration):
    """``{fallback name: [canonical events]}`` for every declared hook script, in order."""
    events = {}
    for hook in declaration["hooks"]:
        events.setdefault(Path(hook["script"]).stem, []).append(hook["event"])
    return events


def expected_wording(hooks, events):
    """What a fallback may say where the mapping is ``hooks``, for a hook declared on ``events``.

    The assistant has an event for the hook when any of the hook's events is named in the
    mapping and is not advisory. A hook declared on more than one event has none only when
    every one of them is null or advisory.
    """
    advisory = set(hooks.get("advisory", ()))
    mapped = [event for event in events
              if hooks["events"][event] is not None and event not in advisory]
    return MAY_NOT_RUN if mapped else NOTHING


def wordings(text):
    """Every statement ``text`` makes about whether its hook runs (a set; empty when silent)."""
    body = flat("\n".join(line for line in text.splitlines() if not line.startswith("#")))
    said = set()
    if SAYS_NOTHING.search(body):
        said.add(NOTHING)
    if SAYS_MAY_NOT_RUN.search(body):
        said.add(MAY_NOT_RUN)
    return said


def heading(name):
    """The heading a fallback's section carries in ``host-rules.md``: its file's first line."""
    return read(FALLBACKS / (name + ".md")).splitlines()[0]


def sections(host_rules):
    """``{heading line: section text}`` for every ``## `` section of a ``host-rules.md``."""
    found, current = {}, None
    for line in host_rules.splitlines():
        if line.startswith("## "):
            current = line
            found[current] = []
        elif current is not None:
            found[current].append(line)
    return {title: "\n".join(lines) for title, lines in found.items()}


def wording_problems(host_rules, hooks, declaration=DECLARATION):
    """Where a ``host-rules.md`` and the ``hooks`` mapping of its assistant disagree."""
    problems = []
    carried = sections(host_rules)
    for name, events in hook_events(declaration).items():
        section = carried.get(heading(name))
        if section is None:
            if name in STATEMENT_FALLBACKS:
                problems.append("%s: its section is missing" % name)
            continue
        said = wordings(section)
        want = expected_wording(hooks, events)
        if len(said) > 1:
            problems.append("%s: says both that nothing does this and that a hook may not run"
                            % name)
        elif not said:
            if name in STATEMENT_FALLBACKS:
                problems.append("%s: no longer says whether a hook does this" % name)
        elif said != {want}:
            problems.append("%s: says %r, and the mapping for %s gives %r"
                            % (name, said.pop(), "/".join(events), want))
    return problems


def host_rules(host_id):
    """The text of ``host_id``'s built ``host-rules.md``."""
    return read(built(host_id) / load_host(host_id).layout["skills"] / HOST_RULES)


def carries_fallbacks(host_id):
    return bool(fallback_scripts(DECLARATION, load_host(host_id)))


def render_fallback(name, host, known=None, stats=None):
    return render_text(read(FALLBACKS / (name + ".md")), host, name + ".md",
                       directives=True, known_hosts=known, stats=stats)


class FallbackWordingFollowsTheMapping(unittest.TestCase):
    """Each built ``host-rules.md`` against its own assistant's mapping."""

    def test_some_package_carries_the_fallbacks(self):
        """Anti-vacuity: with no such package, every loop below would check nothing."""
        self.assertTrue([host for host in HOSTS if carries_fallbacks(host)])

    def test_each_package_says_what_its_mapping_gives(self):
        for host in HOSTS:
            if not carries_fallbacks(host):
                continue
            with self.subTest(host=host):
                text = host_rules(host)
                self.assertEqual([], wording_problems(text, load_host(host).hooks))
                self.assertNotIn("host:", text, "a marker line reached the package")

    def test_each_statement_fallback_makes_one_statement_in_each_package(self):
        """The comparison above skips a silent section, so these four may not be silent."""
        for host in HOSTS:
            if not carries_fallbacks(host):
                continue
            carried = sections(host_rules(host))
            for name in STATEMENT_FALLBACKS:
                with self.subTest(host=host, fallback=name):
                    self.assertIn(heading(name), carried)
                    self.assertEqual(1, len(wordings(carried[heading(name)])))

    def test_a_package_whose_hooks_are_guaranteed_makes_neither_statement(self):
        """Such a package carries no fallback, so it has no statement to get wrong."""
        for host in HOSTS:
            if carries_fallbacks(host):
                continue
            with self.subTest(host=host):
                text = host_rules(host)
                self.assertEqual({}, sections(text))
                self.assertEqual(set(), wordings(text))
                self.assertIn("runs by itself", text)

    def test_control_a_mapping_that_loses_an_event_is_reported(self):
        """The wording stays, the mapping changes: every "may not run" becomes a problem."""
        for host in HOSTS:
            if not carries_fallbacks(host):
                continue
            text = host_rules(host)
            for name, events in hook_events(DECLARATION).items():
                if name not in STATEMENT_FALLBACKS:
                    continue
                hooks = copy.deepcopy(load_host(host).hooks)
                if expected_wording(hooks, events) != MAY_NOT_RUN:
                    continue
                for event in events:
                    hooks["events"][event] = None
                with self.subTest(host=host, fallback=name):
                    self.assertTrue([p for p in wording_problems(text, hooks)
                                     if p.startswith(name + ":")])

    def test_control_a_mapping_that_gains_an_event_is_reported(self):
        """An event that stops being advisory, or stops being null, needs the other wording."""
        seen = 0
        for host in HOSTS:
            if not carries_fallbacks(host):
                continue
            text = host_rules(host)
            for name, events in hook_events(DECLARATION).items():
                hooks = copy.deepcopy(load_host(host).hooks)
                if name not in STATEMENT_FALLBACKS or expected_wording(hooks, events) != NOTHING:
                    continue
                hooks["advisory"] = []
                for event in events:
                    hooks["events"][event] = hooks["events"][event] or "AnEvent"
                seen += 1
                with self.subTest(host=host, fallback=name):
                    self.assertTrue([p for p in wording_problems(text, hooks)
                                     if p.startswith(name + ":")])
        if not seen:
            self.skipTest("every assistant has an event for every statement fallback today")

    def test_control_a_wording_that_changes_is_reported(self):
        """The mapping stays, the wording changes: both directions, both at once, and neither."""
        for host in HOSTS:
            if not carries_fallbacks(host):
                continue
            hooks = load_host(host).hooks
            text = host_rules(host)
            for name in STATEMENT_FALLBACKS:
                body = sections(text)[heading(name)]
                statement = _statement_of(body)
                self.assertTrue(statement.strip(), "no statement before the instruction")
                other = ("Nothing does this." if wordings(body) == {MAY_NOT_RUN}
                         else "When it runs, a hook does this, but it may not run here.")
                changes = (("the other wording", "\n" + other),
                           ("both wordings", statement + "\n" + other),
                           ("no statement", ""))
                for label, changed in changes:
                    with self.subTest(host=host, fallback=name, change=label):
                        mutated = text.replace(body, body.replace(statement, changed, 1), 1)
                        self.assertNotEqual(text, mutated)
                        self.assertTrue([p for p in wording_problems(mutated, hooks)
                                         if p.startswith(name + ":")])


def _statement_of(body):
    """The statement paragraph of a fallback section: everything before its "So" instruction."""
    lines = []
    for line in body.splitlines():
        if line.startswith("So "):
            break
        lines.append(line)
    return "\n".join(lines)


class TheWordingRule(unittest.TestCase):
    """``expected_wording`` on made-up mappings: the cases the issue names."""

    @staticmethod
    def hooks(advisory=(), **events):
        return {"events": events, "advisory": list(advisory)}

    def test_no_event_means_nothing_does_this(self):
        self.assertEqual(NOTHING, expected_wording(self.hooks(stop=None), ["stop"]))

    def test_an_advisory_event_means_nothing_does_this(self):
        self.assertEqual(NOTHING,
                         expected_wording(self.hooks(advisory=["stop"], stop="Stop"), ["stop"]))

    def test_an_event_means_the_hook_may_not_run(self):
        self.assertEqual(MAY_NOT_RUN, expected_wording(self.hooks(stop="Stop"), ["stop"]))

    def test_a_hook_on_two_events_has_none_only_when_both_are_missing(self):
        both = ["post_tool_use", "post_tool_use_failure"]
        one = self.hooks(post_tool_use="After", post_tool_use_failure=None)
        none = self.hooks(post_tool_use=None, post_tool_use_failure=None)
        self.assertEqual(MAY_NOT_RUN, expected_wording(one, both))
        self.assertEqual(NOTHING, expected_wording(none, both))

    def test_the_declaration_has_a_hook_on_two_events(self):
        """Anti-vacuity for the case above: the declaration really holds such a hook."""
        self.assertTrue([name for name, events in hook_events(DECLARATION).items()
                         if len(events) > 1])


class TheMarkersNameTheMappedAssistants(unittest.TestCase):
    """The marker lists in ``source/hooks/fallbacks/``, for every assistant in ``hosts/``."""

    def test_every_declared_hook_has_a_fallback_file(self):
        for name in hook_events(DECLARATION):
            self.assertTrue((FALLBACKS / (name + ".md")).is_file(), name)
        for name in STATEMENT_FALLBACKS:
            self.assertIn(name, hook_events(DECLARATION))

    def test_each_statement_fallback_lists_the_assistants_that_have_an_event(self):
        """One ``host:only`` block and one ``host:except`` block, naming the same assistants:
        exactly those whose mapping has an event for the hook that is not advisory."""
        events = hook_events(DECLARATION)
        for name in STATEMENT_FALLBACKS:
            stats = RenderStats()
            render_fallback(name, load_host(HOSTS[0]), known=set(HOSTS), stats=stats)
            mapped = sorted(host for host in HOSTS
                            if expected_wording(load_host(host).hooks, events[name]) == MAY_NOT_RUN)
            with self.subTest(fallback=name):
                self.assertEqual(["only", "except"], [kind for kind, _, _ in stats.blocks])
                for kind, names, _ in stats.blocks:
                    self.assertEqual(mapped, sorted(names),
                                     "the host:%s list and the hooks mappings disagree" % kind)

    def test_every_fallback_renders_to_what_each_mapping_gives(self):
        """Every fallback for every assistant, whether or not its package carries it today."""
        for name, events in hook_events(DECLARATION).items():
            for host_id in HOSTS:
                host = load_host(host_id)
                said = wordings(render_fallback(name, host, known=set(HOSTS)))
                with self.subTest(fallback=name, host=host_id):
                    if name in STATEMENT_FALLBACKS or said:
                        self.assertEqual({expected_wording(host.hooks, events)}, said)

    def test_both_wordings_exist_and_end_in_the_same_instruction(self):
        """An assistant no list names gets "nothing does this"; a listed one gets "may not
        run"; and the two texts differ in that statement only."""
        for name in STATEMENT_FALLBACKS:
            stats = RenderStats()
            render_fallback(name, load_host(HOSTS[0]), known=set(HOSTS), stats=stats)
            listed = load_host(sorted(stats.blocks[0][1])[0])
            unlisted = dataclasses.replace(listed, id="an-assistant-no-list-names")
            with_event, without = render_fallback(name, listed), render_fallback(name, unlisted)
            with self.subTest(fallback=name):
                self.assertEqual({MAY_NOT_RUN}, wordings(with_event))
                self.assertEqual({NOTHING}, wordings(without))
                rest_a = [line for line in with_event.splitlines()
                          if line not in without.splitlines()]
                rest_b = [line for line in without.splitlines()
                          if line not in with_event.splitlines()]
                self.assertEqual(_statement_of(_body(with_event)).strip(), "\n".join(rest_a))
                self.assertEqual(_statement_of(_body(without)).strip(), "\n".join(rest_b))
                shared = [line for line in without.splitlines() if line.startswith("So ")]
                self.assertEqual(1, len(shared), "the shared instruction opens with 'So'")
                self.assertIn(shared[0], with_event.splitlines())


def _body(fallback_text):
    """A rendered fallback without its heading line."""
    return "\n".join(fallback_text.splitlines()[1:])


# --- 2. Shared text states no hook action without a condition -------------------------------

#: Each sentence #29 retired, by file and by the passage the issue listed it under. Matched
#: with whitespace collapsed. ``{{`` is the source's own token spelling.
RETIRED = (
    (ONBOARDING + "ground-rules.md", "worked steers",
     "is caught by a hook, `failed-run-net.py`, which reminds the guide when it happens"),
    (ONBOARDING + "ground-rules.md", "all files stay inside the working directory",
     "The `PreToolUse` write-gate enforces the write half and will block you."),
    (ONBOARDING + "ground-rules.md", "file placement",
     "The plugin's PreToolUse write-gate blocks every write outside the project"),
    (ONBOARDING + "ground-rules.md", "recap checkpoint, the fold",
     "the plugin's `PreCompact`, `SessionEnd`, and `SessionStart` hooks fold it into"),
    (ONBOARDING + "ground-rules.md", "recap checkpoint, the scaffold",
     "(`UserPromptSubmit`) lays down an empty scaffold within a turn of the bootcamp starting, "
     "so the path always exists and you never have to create it"),
    (ONBOARDING + "ground-rules.md", "recap checkpoint, the skip",
     "the fold hooks skip it and say so on stderr"),
    (ONBOARDING + "ground-rules.md", "feedback and notes at any time",
     "(The plugin's `UserPromptSubmit` hook surfaces this automatically during a bootcamp.)"),
    (ONBOARDING + "ground-rules.md", "closing questions",
     "The plugin's `Stop` hook is a safety net that fires only if you forget"),
    (ONBOARDING + "notes.md", "what triggers the flow",
     "Triggered by the plugin's `UserPromptSubmit` hook"),
    (ONBOARDING + "feedback.md", "what triggers the flow",
     "triggered by the plugin's `UserPromptSubmit` hook"),
    (ONBOARDING + "packaging.md", "no hook for this flow",
     "whose `UserPromptSubmit` clause is real, nothing intercepts prompts"),
    (ONBOARDING + "module-completion.md", "step 2d, the fold",
     "the plugin's durability hooks may have folded it"),
    (ONBOARDING + "module-completion.md", "step 2d, the scaffold",
     "lays a fresh empty scaffold back down on the next turn if you delete it"),
    (ONBOARDING + "module-completion.md", "step 2d, the skip",
     "the fold hooks skip both"),
    ("graduation/SKILL.md", "the terminal step, its title",
     "Stand down the Stop-hook nudge"),
    ("graduation/SKILL.md", "the terminal step, the flag",
     "The `Stop` hook (`{{host.scripts_relative}}/stop-nudge.py`) reads the flag and will not nudge"),
    ("module-02-sdk-setup/SKILL.md", "recording a container, the runtime",
     "the hooks stop and report each container"),
    ("module-02-sdk-setup/SKILL.md", "recording a container, the lifecycle",
     "The `SessionEnd` hook stops recorded containers on exit (`<runtime> stop`, not remove) "
     "and `SessionStart` surfaces them on resume"),
    ("module-02-sdk-setup/SKILL.md", "naming a container",
     "the lifecycle hooks find containers by exact name, so one project's `SessionEnd` would "
     "stop, and its `SessionStart` would report, the other's container"),
    ("module-02-sdk-setup/SKILL.md", "recording the database container",
     "so the SessionEnd hook stops it on exit and SessionStart offers to restart it"),
    ("module-05-data-quality-mapping/phase2-data-mapping.md", "file placement",
     "The plugin's PreToolUse write-gate blocks every write outside the project"),
)

#: A hook as the subject of an action: "the write-gate blocks", "hooks fold it",
#: "the `X` hook (`script.py`) reads the flag".
HOOK_VERBS = ("blocks?|enforces?|folds?|stops?|surfaces?|finds?|skips?|fires?|reads?|catch(?:es)?"
              "|reports?|intercepts?|reminds?|nudges?|checks?|re-opens?|creates?|lays?|closes?"
              "|offers?|routes?")
HOOK_ACTS = re.compile(
    r"(?i)(?:\bhooks?|\bwrite-gate)(?: \([^)]*\))? (?:%s)\b"      # the hook does something
    r"|\bby (?:a|the)(?: plugin's)?(?: `[^`]+`)? hooks?\b"        # something is done by a hook
    r"|\bplugin's (?:[`\w-]+,? (?:and )?){0,4}(?:hooks?\b|write-gate\b)"  # the plugin's … hook
    % HOOK_VERBS)
#: The condition a hook statement carries. The first form is the one
#: `module-05-data-quality-mapping/phase3-test-load.md` used before #29.
CONDITION = re.compile(
    r"(?i)\bwhether or not a hook backs\b"
    r"|\bwhere (?:a hook|it|one) runs\b"
    r"|\bif (?:a|the)(?: plugin)? (?:hook|write-gate)\b")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`(*\"⛔⚠])")


def retired_problems(texts, retired=RETIRED):
    """Every retired sentence that ``texts`` (``{relative path: text}``) holds again."""
    problems = []
    for relative, passage, sentence in retired:
        if flat(sentence) in flat(texts[relative]):
            problems.append("%s (%s): %r is back" % (relative, passage, sentence))
    return problems


def unconditional_statements(text):
    """Each sentence of ``text`` that says a hook acts and carries no condition."""
    return [sentence for sentence in SENTENCE_END.split(flat(text))
            if HOOK_ACTS.search(sentence) and not CONDITION.search(sentence)]


def skill_texts():
    """``{path relative to source/skills: text}`` for every Markdown file there."""
    return {path.relative_to(SKILLS).as_posix(): read(path)
            for path in sorted(SKILLS.rglob("*.md"))}


class NoRetiredSentenceIsBack(unittest.TestCase):

    def test_no_file_holds_a_sentence_the_issue_retired(self):
        self.assertEqual([], retired_problems(skill_texts()))

    def test_every_file_the_issue_listed_is_covered(self):
        """Anti-vacuity: the eight files of the issue's scope, each with a sentence pinned."""
        listed = {relative for relative, _, _ in RETIRED}
        self.assertEqual(8, len(listed))
        for relative in listed:
            self.assertTrue((SKILLS / relative).is_file(), relative)

    def test_control_each_retired_sentence_is_reported_when_put_back(self):
        texts = skill_texts()
        for relative, passage, sentence in RETIRED:
            with self.subTest(file=relative, passage=passage):
                changed = dict(texts)
                changed[relative] = texts[relative] + "\n" + sentence + "\n"
                problems = retired_problems(changed)
                self.assertTrue([p for p in problems if p.startswith(relative)], problems)


class NoUnconditionalHookStatement(unittest.TestCase):

    def test_no_skill_file_says_a_hook_acts_without_a_condition(self):
        problems = ["%s: %s" % (relative, sentence)
                    for relative, text in skill_texts().items()
                    for sentence in unconditional_statements(text)]
        self.assertEqual([], problems)

    def test_the_scan_reads_sentences_that_name_a_hook(self):
        """Anti-vacuity: the skills still speak of hooks, and still in the conditional form."""
        texts = skill_texts()
        self.assertTrue([r for r, text in texts.items() if HOOK_ACTS.search(flat(text))])
        self.assertGreaterEqual(
            sum(len(re.findall(r"(?i)whether or not a hook backs it on this assistant",
                               flat(text))) for text in texts.values()), 2)

    def test_control_the_unconditional_shapes_are_reported(self):
        for sentence in (
            "The `PreToolUse` write-gate enforces the write half and will block you.",
            "The plugin's PreToolUse write-gate blocks every write outside the project.",
            "The plugin's `PreCompact`, `SessionEnd`, and `SessionStart` hooks fold it in.",
            "A scaffold holds no narrative, and the fold hooks skip it and say so on stderr.",
            "(The plugin's `UserPromptSubmit` hook surfaces this automatically.)",
            "The plugin's `Stop` hook is a safety net that fires only if you forget.",
            "Triggered by the plugin's `UserPromptSubmit` hook, by the command, or by a phrase.",
            "A failure repaired without a record is caught by a hook, `failed-run-net.py`.",
            "The plugin's durability hooks may have folded it into the recap.",
            "The `Stop` hook (`scripts/stop-nudge.py`) reads the flag and will not nudge.",
            "The hooks stop and report each container with the CLI named there.",
            "The lifecycle hooks find containers by exact name.",
            "So the SessionEnd hook stops it on exit.",
        ):
            with self.subTest(sentence=sentence):
                self.assertEqual([sentence], unconditional_statements("Before. " + sentence))

    def test_control_the_conditional_shapes_are_not_reported(self):
        for sentence in (
            "Whether or not a hook backs it on this assistant, you own the closing question.",
            "No write leaves the project: where it runs, the write-gate blocks such a write.",
            "If the plugin write-gate blocks a write, leave the file in the workspace.",
            "Recognizing them is the guide's job, not a hook's.",
            "Writing the narrative is the half no hook can do for you.",
        ):
            with self.subTest(sentence=sentence):
                self.assertEqual([], unconditional_statements(sentence))


# --- 3. Event names are an assistant's own or none ------------------------------------------

def own_event_names(host_id):
    """The event names in ``host_id``'s mapping (an event it has none for contributes nothing)."""
    return {name for name in load_host(host_id).hooks["events"].values() if name}


ALL_EVENT_NAMES = frozenset().union(*(own_event_names(host) for host in HOSTS))

#: The event name that is also an ordinary word: counted in backticks or directly before "hook".
STOP_AS_AN_EVENT = re.compile(r"`Stop`|\bStop[ -]hooks?\b")


def event_names_in(text, names):
    """``(line number, name)`` for every use of an event name from ``names`` in ``text``."""
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        for name in sorted(names):
            pattern = (STOP_AS_AN_EVENT if name == "Stop"
                       else re.compile(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(name)))
            if pattern.search(line):
                found.append((number, name))
    return found


def shared_texts():
    """``{path relative to source/: text}`` for the shared text #29 covers."""
    return {path.relative_to(SOURCE_DIR).as_posix(): read(path)
            for root in (SKILLS, FALLBACKS) for path in sorted(root.rglob("*.md"))}


def package_markdown(host_id):
    """``{relative path: text}`` for every Markdown file in ``host_id``'s built package."""
    root = built(host_id)
    return {path.relative_to(root).as_posix(): read(path)
            for path in sorted(root.rglob("*.md")) if path.is_file()}


def foreign_event_names(texts, host_id):
    """Uses, in ``texts``, of an event name that is in some mapping and not in ``host_id``'s."""
    foreign = ALL_EVENT_NAMES - own_event_names(host_id)
    return ["%s:%d: %s" % (relative, number, name)
            for relative, text in texts.items()
            for number, name in event_names_in(text, foreign)]


class SharedTextNamesNoHookEvent(unittest.TestCase):

    def test_the_mappings_name_events(self):
        """Anti-vacuity: the name set comes from the mappings and holds the known names."""
        for name in ("UserPromptSubmit", "Stop", "userPromptSubmitted"):
            self.assertIn(name, ALL_EVENT_NAMES)
        self.assertGreaterEqual(len(shared_texts()), 20)

    def test_no_shared_file_holds_an_event_name_from_any_mapping(self):
        problems = ["source/%s:%d: %s" % (relative, number, name)
                    for relative, text in shared_texts().items()
                    for number, name in event_names_in(text, ALL_EVENT_NAMES)]
        self.assertEqual([], problems)

    def test_control_every_event_name_is_reported(self):
        for name in sorted(ALL_EVENT_NAMES):
            with self.subTest(name=name):
                line = "The `%s` hook stops recorded containers." % name
                self.assertEqual([(2, name)], event_names_in("Before.\n" + line, {name}))

    def test_stop_is_an_event_only_in_backticks_or_before_hook(self):
        for line in ("The `Stop` hook is a safety net.", "Stand down the Stop-hook nudge.",
                     "The Stop hook reads the flag.", "Named `Stop` in the configuration."):
            with self.subTest(line=line):
                self.assertEqual([(1, "Stop")], event_names_in(line, {"Stop"}))
        for line in ("Stop and ask before writing.", "Run `<runtime> stop`, not remove.",
                     "Stop the container, then hook it up again."):
            with self.subTest(line=line):
                self.assertEqual([], event_names_in(line, {"Stop"}))

    def test_a_longer_word_is_not_an_event_name(self):
        self.assertEqual([], event_names_in("See PreToolUseful and MySessionStart.",
                                            {"PreToolUse", "SessionStart"}))


class APackageNamesOnlyItsOwnEvents(unittest.TestCase):
    """The Markdown of each built package: an event name there is in that package's mapping."""

    def test_no_package_holds_another_mappings_event_name(self):
        for host in HOSTS:
            with self.subTest(host=host):
                texts = package_markdown(host)
                self.assertGreaterEqual(len(texts), 20)
                self.assertEqual([], foreign_event_names(texts, host))

    def test_control_one_packages_event_names_are_foreign_in_another(self):
        """Markdown that names its own package's events, read as if another package held it."""
        named = 0
        for host in HOSTS:
            texts = package_markdown(host)
            used = {name for text in texts.values()
                    for _, name in event_names_in(text, own_event_names(host))}
            for other in HOSTS:
                if not used - own_event_names(other):
                    continue
                named += 1
                with self.subTest(written_for=host, read_as=other):
                    self.assertTrue(foreign_event_names(texts, other))
        self.assertTrue(named, "no package's Markdown names a hook event another assistant "
                               "lacks, so this control has nothing to read")


if __name__ == "__main__":
    unittest.main()
