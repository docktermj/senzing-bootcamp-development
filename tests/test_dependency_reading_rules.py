"""The dependency report's reading rules ship, and the constructions that mislead it are pinned.

Amended R8 (#119) requires a dependency review of the open issues, reported before the
maintainer chooses. Since #215 R8 gives that review to **the operation that chooses the issue**
(`/order-github-issues` in this host); `implement-github-issue` invoked with no argument names
no issue. ⛔ **The obvious
implementations of that are worse than not doing it**, which is why the rules are stated in the
rule rather than left to whoever writes the report.

Measured over the seven issues open in this repository on 2026-09-22:

* **Counting cross-references inverted the strongest signal.** Two issues named two others
  inside their `owner-checked:` lines -- *"the open backlog at that date was #106, #105, #79,
  #55, #53, none of which touch `conformance.py`'s corpus"*. That is an INV-213 absence claim
  asserting the issues are **unrelated**; read as an edge it reports the exact opposite.
* **Shared-file coupling made five of seven look ordered**, because five name
  `specs/INVARIANTS.md`. A hub establishes merge risk, not sequence.
* **The one real relation was visible to neither method** -- an issue quoting a figure a later
  change had already altered -- and only by reading content.

So this module does not test a dependency algorithm; there is none, and R8's report is a
procedure an agent follows. It tests that **the reading rules are stated where the procedure
will meet them**, and it pins the two constructions that produced the wrong answers, so a later
edit cannot quietly drop the lesson while leaving the feature.

⚠️ **Re-pointed 2026-09-28 (#215): R8 is now the only surface checked.** The command and the
in-repo skill used to restate the rules; the command is now the repo overlay and the skill a
pointer stub, and neither restates them. `NoOtherSurfaceRestatesTheReview` pins that, so the
rules cannot grow a second home that drifts (INV-300).

⚠️ **The user-level skills carrying the procedure are NOT checked here.**
`~/.claude/skills/order-github-issues/SKILL.md` and
`~/.claude/skills/implement-github-issue/SKILL.md` live outside this repository; CI checks out
only the repo, so asserting on them would fail there and pass only on a maintainer's machine.
They are unguarded, deliberately and with the gap recorded rather than hidden behind a test
that cannot run (INV-308).

⚠️ **What this does NOT establish:** that any particular run's dependency report is correct,
complete, or useful. No offline check reaches that. It establishes that the rules a correct
report must follow are present and have not been silently removed.

⚠️ **Dated note, 2026-11-14 (one-repository migration): the R8 cases are retired.** R8 was
stated in `docs/FAMILY_WORKFLOW.md`, which was not carried into this repository, so the cases
that read its region are gone: that it states each rule, names the choosing operation, and no
longer forbids recommending. What stays is that the repo overlay restates none of the review,
and the two constructions that mislead it.

Source issues: #119; #215 (the review moves to the choosing operation); #239 (the overlay moves
to `.claude/skill-overlays/`, and the stub is removed).

Stdlib only; both surfaces are read as text (INV-108).

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

from _wrapped_text import match_lines

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND = REPO_ROOT / ".claude" / "skill-overlays" / "implement-github-issue.md"
#: The in-repo skill joined this guard at #126 after sitting two amendments behind the
#: user-level copy -- the INV-300 defect ("a rule with two homes will disagree with itself")
#: happening to R8. #215 made it a pointer stub and #239 removed it, so it is no longer read here.

#: A clause forbidding the operation to recommend, which R8 dropped at #119.
RECOMMENDATION_BAN = re.compile(r"(?i)does not recommend|do not recommend")

#: Surfaces that must NOT restate the review: R8 is its one home in this repository.
NOT_A_HOME = {"the repo overlay": COMMAND}

#: A reference that ASSERTS NON-DEPENDENCE. Must never be read as a dependency edge.
NOT_A_DEPENDENCY = [
    "owner-checked: the open backlog at that date was #106, #105, #79, #55, #53, none of which "
    "touch `conformance.py`'s corpus.",
    "the open backlog at that date was #79, #55, #53, none of which touch filing.",
]

#: A reference that IS a dependency. Pinned beside the ones that are not, so the distinction is
#: exercised in both directions rather than only refused in one (INV-282).
IS_A_DEPENDENCY = [
    "This cannot land until #117 removes the stale denominator it measures against.",
    "Blocked by #108: its acceptance criterion measures the corpus this one changes.",
]

#: How a reading rule distinguishes them: the absence-claim construction, not the `#n` itself.
ABSENCE_CLAIM = re.compile(r"(?i)owner-checked|none of which|does not touch|unrelated to")


#: Wordings that restate R8's dependency review (INV-300).
RESTATEMENTS = (r"(?i)review the open issues for dependencies", r"(?i)impl(?:y|ies) no order",
                r"(?i)merge risk")


def restatement_lines(text, pattern):
    """Lines where ``pattern`` starts in ``text``, matched across line wraps (#425).

    "merge\nrisk" restates the rule as surely as "merge risk" does, so a line-at-a-time or
    literal-space search would let a wrapped restatement through.
    """
    return match_lines(text, re.compile(pattern))


class NoOtherSurfaceRestatesTheReview(unittest.TestCase):
    """INV-300 -- the rules have one home; a second copy is how R8 drifted before."""

    def test_neither_the_command_nor_the_stub_restates_it(self):
        for surface, path in sorted(NOT_A_HOME.items()):
            text = path.read_text(encoding="utf-8")
            for pattern in RESTATEMENTS:
                with self.subTest(surface=surface, pattern=pattern):
                    self.assertEqual(
                        [], restatement_lines(text, pattern),
                        "%s restates R8's dependency review at these lines. R8 is its one home "
                        "here; a copy in %s is the two-homes drift #126 and #215 each had to "
                        "repair" % (surface, path))

    def test_a_wrapped_restatement_is_found_at_its_first_line(self):
        """Negative control (#425): "merge" ends line 2 and "risk" begins line 3."""
        wrapped = "Before choosing:\nshared files are merge\nrisk, not order.\n"
        self.assertEqual([2], restatement_lines(wrapped, r"(?i)merge risk"))
        # The old raw-text search, kept only to show the fixture is the hard case.
        self.assertIsNone(re.search(r"(?i)merge risk", wrapped))


def ban_lines(text):
    """Lines where a recommendation ban starts, matched across line wraps (#425)."""
    return match_lines(text, RECOMMENDATION_BAN)


class TheRecommendationBanIsGone(unittest.TestCase):
    """R8 dropped it at #119. A surface still imposing it contradicts the rule it implements."""

    def test_a_wrapped_ban_is_found_at_its_first_line(self):
        """Negative control (#425): "do not" ends line 1 and "recommend" begins line 2."""
        wrapped = "The report lists the issues and do not\nrecommend one of them.\n"
        self.assertEqual([1], ban_lines(wrapped))
        # The old line-at-a-time read, kept only to show the fixture is the hard case.
        self.assertFalse(any(RECOMMENDATION_BAN.search(l) for l in wrapped.split("\n")))

    def test_the_rule_that_replaced_the_ban_is_not_flagged(self):
        """Must not flag (INV-282): naming the issue it suggests is the current rule."""
        self.assertEqual([], ban_lines("The report names the issue it\nsuggests, with its "
                                       "evidence.\n"))


class AbsenceClaimsAreNotEdges(unittest.TestCase):
    """⛔ The measured inversion, pinned in both directions."""

    def test_a_non_dependence_reference_is_recognized_as_one(self):
        for line in NOT_A_DEPENDENCY:
            with self.subTest(line=line[:48]):
                self.assertTrue(
                    ABSENCE_CLAIM.search(line),
                    "a reference that asserts NON-dependence was not recognized as one, so a "
                    "reader counting `#n` would take it as a dependency edge -- the exact "
                    "inversion measured on 2026-09-22")

    def test_a_real_dependency_is_not_mistaken_for_one(self):
        for line in IS_A_DEPENDENCY:
            with self.subTest(line=line[:48]):
                self.assertFalse(
                    ABSENCE_CLAIM.search(line),
                    "a genuine dependency was classified as an absence claim; the rule would "
                    "then discard the relations it exists to find")

    def test_both_fixture_sets_are_populated(self):
        """INV-265 -- one empty side makes the distinction untested in that direction."""
        self.assertTrue(NOT_A_DEPENDENCY)
        self.assertTrue(IS_A_DEPENDENCY)


if __name__ == "__main__":
    unittest.main()
