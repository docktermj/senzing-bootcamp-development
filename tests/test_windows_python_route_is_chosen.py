"""Module 2 Step 2 chooses one install route for Python on Windows, and the tail rule agrees.

Routing rule 1 of **Routing rules (apply in order)** in `module-02-sdk-setup/SKILL.md` names two
Linux environments for the Python SDK on Windows, a container (`platform='docker'`) and WSL2
(`platform='linux_apt'`). Before #40 nothing chose between them: Step 2 said "Detect first, do not
ask", no question in the file chose a route, and the "Agent Behavior" bullet at the end of the
file said "Do NOT offer alternatives", which predates the WSL2 branch and read literally forbids
it.

Rule 1 now states the procedure, in order:

1. a route already recorded under step 2 in `config/bootcamp_progress.json` is taken, with no
   probe and no question (INV-006);
2. otherwise the guide checks what is present: a container runtime that answers `docker version`
   or `podman version`, and a distribution running under WSL version 2;
3. exactly one present: take it, say so in one line, ask nothing;
4. both or neither: say what was found and ask one pinned question (INV-056, INV-051), with a
   handling entry for each option (INV-284).

The checkpoint records the route, and the tail bullet defers to the routing rules.

**What this guard holds.** That the shipped text STATES each part, so a test fails when rule 1
loses its decision procedure, when the pinned question loses an option or a handling entry, when
the route is no longer recorded, or when the tail rule again forbids a route the routing rules
resolve. Every check is a function returning problems, and each runs on the shipped text and on
an in-memory mutant that must fail it, so no check is vacuous (INV-265).

**What this cannot establish.** That a live guide runs the probes, reads their output correctly,
or asks the question only in the both-or-neither case: `dry-run` phase 3 observes that. Nothing
about the Senzing MCP server is asserted; the suite is offline (INV-108). Installing a missing
Docker Desktop or WSL2, and running commands inside WSL2 from native Windows, are out of #40's
scope and not asserted here.

Every read collapses whitespace before matching, so a re-flow of the shipped Markdown cannot hide
a clause from it (INV-346).

Stdlib only; shipped files are read as text, never imported (INV-108).

Source issue: #40.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE2 = REPO_ROOT / "source" / "skills" / "module-02-sdk-setup" / "SKILL.md"

QUESTION = ("\U0001f449 **Which Linux environment would you like to run the Senzing SDK in? "
            "Reply with a number:**")
MARKER = "**Handling each answer (INV-284).**"

#: The tail bullet as it stood before #40. Kept as a negative control.
PRE_40_TAIL = ("- Do NOT offer alternatives: install the SDK natively (or via Docker where the "
               "routing rules\n  require it).\n")


def flat(text):
    """Whitespace-collapsed text, so a clause is found however the Markdown is wrapped."""
    return re.sub(r"\s+", " ", text)


def region(text, start, end, what):
    """The collapsed text between two markers, or a failure naming what moved."""
    begin = text.find(start)
    if begin < 0:
        raise AssertionError("%s: the opening marker %r is gone" % (what, start))
    stop = text.find(end, begin + len(start))
    if stop < 0:
        raise AssertionError("%s: the closing marker %r is gone" % (what, end))
    return flat(text[begin:stop])


def rule_one(text):
    return region(text, "1. Chosen language is Python AND OS is macOS or Windows", "2. macOS Intel",
                  "routing rule 1")


def routing_rules(text):
    return region(text, "**Routing rules (apply in order):**", "When a learner lands on Docker",
                  "the routing rules")


def step_two(text):
    return region(text, "## Step 2: Determine Platform", "## Step 3:", "Module 2 Step 2")


def route_question(text):
    """From the route question's lead-in to the checkpoint that ends Step 2."""
    return region(text, "**The route question (rule 1, Windows with Python only).**",
                  "## Step 3:", "the route question")


def agent_behavior(text):
    return region(text, "## Agent Behavior", "## Troubleshooting", "Agent Behavior")


# --- The checks: each returns a list of problems -------------------------------------------------

def rule_one_problems(text):
    """Rule 1 states, in order, how the Windows route is chosen."""
    rule = rule_one(text)
    problems = []
    steps = [
        ("the heading of the procedure", "**Which route, on Windows.**"),
        ("a recorded route is taken first",
         "records a `route` of `container` or `wsl2`, take that route"),
        ("a recorded route probes and asks nothing", "Probe nothing and ask nothing (INV-006)"),
        ("what makes a container present", "`docker version` or `podman version` answers"),
        ("what makes WSL2 present", "`wsl --list --verbose` lists at least one distribution whose "
                                    "VERSION is 2"),
        ("WSL 1 does not count", "a WSL 1 distribution does not count"),
        ("exactly one present takes it", "**Exactly one present:** take that route"),
        ("both or neither asks the route question", "**Both present, or neither:**"),
    ]
    at = 0
    for what, needle in steps:
        found = rule.find(needle, at)
        if found < 0:
            problems.append("rule 1 no longer states %s (%r), in order" % (what, needle))
        else:
            at = found + len(needle)
    exactly_one = region(rule, "**Exactly one present:**", "**Both present, or neither:**",
                         "rule 1's exactly-one branch") if not problems else ""
    if exactly_one and "Ask nothing" not in exactly_one:
        problems.append("rule 1's exactly-one branch no longer says it asks nothing")
    if "Which Linux environment" not in rule:
        problems.append("rule 1's both-or-neither branch does not name the route question")
    if "On macOS nothing is chosen" not in rule:
        problems.append("rule 1 no longer says macOS has no choice, probe or question")
    return problems


def question_problems(text):
    """The pinned question, its two options, and a handling entry for each."""
    problems = []
    if text.count(QUESTION) != 1:
        return ["the route question is not pinned verbatim exactly once in the file (INV-056)"]
    block = route_question(text)
    if QUESTION not in block:
        return ["the route question has left Step 2"]
    if "Asked only when rule 1 finds both Linux environments present, or neither" not in block:
        problems.append("the route question no longer says when it is asked")
    options = block[block.index(QUESTION) + len(QUESTION):]
    if not re.match(r"\s*1\. A container 2\. WSL2 ", options):
        problems.append("the route question's options are not exactly 1. A container, 2. WSL2")
    if MARKER not in block:
        return problems + ["the route question has no %s marker (INV-284)" % MARKER]
    handling = block[block.index(MARKER):]
    if "checkpoint step 2 and continue to Step 3" not in handling:
        problems.append("the handling does not checkpoint step 2 and continue to Step 3")
    entries = {
        1: ('- **1, "A container":** `platform=\'docker\'`', "record `route` as `container`"),
        2: ('- **2, "WSL2":** `platform=\'linux_apt\'`', "record `route` as `wsl2`"),
    }
    for num, (entry, record) in entries.items():
        if entry not in handling:
            problems.append("option %d has no handling entry resolving its platform" % num)
            continue
        rest = handling[handling.index(entry):]
        nxt = rest.find("- **", len(entry))
        if record not in (rest[:nxt] if nxt > 0 else rest):
            problems.append("option %d's handling entry does not record the route" % num)
    return problems


def record_problems(text):
    """The checkpoint records the route under step 2."""
    step = step_two(text)
    needle = ("**Checkpoint:** write step 2 to `config/bootcamp_progress.json`. On Windows with "
              "Python, record rule 1's `route` (`container` or `wsl2`) under step 2")
    if needle not in step:
        return ["Step 2's checkpoint no longer records rule 1's route under step 2"]
    return []


def tail_problems(text):
    """The Agent Behavior bullet defers to the routing rules and forbids only what they don't
    resolve."""
    tail = agent_behavior(text)
    problems = []
    if re.search(r"(?i)do not offer alternatives", tail):
        problems.append("the Agent Behavior bullet again forbids alternatives outright, which "
                        "forbids rule 1's WSL2 route")
    needle = "- Install the SDK on the route Step 2's routing rules resolve"
    if needle not in tail:
        return problems + ["no Agent Behavior bullet defers to Step 2's routing rules"]
    bullet = tail[tail.index(needle):]
    bullet = bullet[:bullet.find(" - ", len(needle))]
    for what, part in (("WSL2 as a resolved route", "WSL2 where rule 1 chooses it"),
                       ("forbidding only unresolved routes",
                        "Offer no route those rules do not resolve"),
                       ("the route question as the one choice left",
                        "rule 1's route question, on Windows with Python")):
        if part not in bullet:
            problems.append("the Agent Behavior bullet no longer names %s" % what)
    return problems


def other_routes_problems(text):
    """No other route gains a question, and the ordinals 1 to 5 stay."""
    rules = routing_rules(text)
    problems = []
    if "\U0001f449" in rules:
        problems.append("a routing rule itself carries a \U0001f449 question")
    at = 0
    for n, lead in ((1, "1. Chosen language is Python"), (2, "2. macOS Intel"),
                    (3, "3. macOS Apple Silicon"), (4, "4. Windows without Scoop"),
                    (5, "5. Linux →")):
        found = rules.find(lead, at)
        if found < 0:
            problems.append("routing rule %d (%r) is gone or out of order; bootcamp preparation "
                            "indexes the list by number" % (n, lead))
        else:
            at = found
    later = region(text, "2. macOS Intel", "When a learner lands on Docker", "routing rules 2-5")
    if "route question" in later:
        problems.append("a routing rule other than rule 1 now leads to the route question")
    if step_two(text).count("\U0001f449") != 2:
        problems.append("Step 2 no longer carries exactly two \U0001f449 questions: the platform "
                        "fallback and rule 1's route question")
    return problems


CHECKS = (rule_one_problems, question_problems, record_problems, tail_problems,
          other_routes_problems)


class TheShippedTextHoldsEveryPart(unittest.TestCase):
    def setUp(self):
        self.text = MODULE2.read_text(encoding="utf-8")

    def test_every_check_passes(self):
        for check in CHECKS:
            with self.subTest(check=check.__name__):
                problems = check(self.text)
                self.assertEqual([], problems, "\n".join(problems))


class EachCheckBites(unittest.TestCase):
    """Negative controls: an in-memory mutant of the shipped file must fail each check."""

    def setUp(self):
        self.text = MODULE2.read_text(encoding="utf-8")

    def mutate(self, old, new):
        self.assertIn(old, self.text, "the mutation's target %r is gone" % old[:60])
        return self.text.replace(old, new, 1)

    def test_rule_one_without_its_detection_fails(self):
        start = self.text.index("   **Which route, on Windows.**")
        end = self.text.index("2. macOS Intel")
        mutant = self.text[:start] + self.text[end:]
        self.assertNotEqual([], rule_one_problems(mutant))

    def test_rule_one_asking_when_one_is_present_fails(self):
        mutant = self.mutate("     wrong.\" Ask nothing.",
                             "     wrong.\" Then ask the route question.")
        self.assertNotEqual([], rule_one_problems(mutant))

    def test_a_lost_handling_entry_fails(self):
        mutant = self.mutate('- **2, "WSL2":**', '- WSL2:')
        self.assertNotEqual([], question_problems(mutant))

    def test_a_reworded_question_fails(self):
        mutant = self.mutate("Which Linux environment would you like",
                             "Would you like a container or WSL2, which Linux environment "
                             "would you like")
        self.assertNotEqual([], question_problems(mutant))

    def test_an_unrecorded_route_fails(self):
        mutant = self.mutate("record `route` as `wsl2`", "carry on")
        self.assertNotEqual([], question_problems(mutant))
        mutant = self.mutate("On Windows with Python, record\nrule 1's `route`",
                             "On Windows with Python, note\nrule 1's `route`")
        self.assertNotEqual([], record_problems(mutant))

    def test_the_pre_40_tail_rule_fails(self):
        start = self.text.index("- Install the SDK on the route Step 2's routing rules resolve")
        end = self.text.index("- Use the `sdk_guide` MCP tool", start)
        mutant = self.text[:start] + PRE_40_TAIL + self.text[end:]
        self.assertNotEqual([], tail_problems(mutant))

    def test_a_question_on_another_route_fails(self):
        mutant = self.mutate("4. Windows without Scoop (non-Python) →",
                             "4. Windows without Scoop (non-Python) → ask the route "
                             "question, then")
        self.assertNotEqual([], other_routes_problems(mutant))


if __name__ == "__main__":
    unittest.main()
