"""A payload routing answer must be honored in effect, not only in form.

MCP-NEGATIVE-SCAN: ignore-file — this file asserts the marker FORMAT (that the shipped
marker names its owning route and carries a server version and date). The token below is a
`startswith` needle in a test body, not a dated claim about the current server, and the
scanner would otherwise report it as a malformed marker. Since #323 the needle finds the
marker inside its `<!-- … -->` wrapper.

A Bootcamper was asked how to route a field and answered **payload**. The mapper kept the
key under its own name at the record root — where that name is a *registered feature
attribute* — so Senzing extracted it as a feature anyway. Their explicit answer was
silently not honored. The same field also went through a list-joining payload route, so
**13,803 of 19,050 records** carried `"XXX; VGB; GBR"` as one literal value.

⛔ **Every static gate passed.** The analyzer, the verbatim check and the routing report each
confirm the output matches the plan and the plan is faithful to the source. None of them
confirms the plan does what the Bootcamper asked, so an answer selecting a *behavior*
rather than a *value* is unverified by construction. That general shape is the finding; the
collision is one instance of it.

⚠️ **The analyzer already knew** — its SCHEMA warning fired and cleared on the rename. The
check was in the wrong place in the flow, not missing, which is why the remedy moves it to
the mapping gate rather than inventing a new instrument.

⛔ **The prohibition is documented, and since #38 so is its consequence; these tests pin which
route carries which**, not just the guidance. `mapping_workflow` step 2's inline *SENZING
MAPPING REFERENCE* serves the prohibition itself — a root-level payload attribute "must NOT
be a registered feature attribute" (server 1.37.16, 2026-10-01, #322) — so the guidance cites
that step for the rule. What breaking it does (the key is extracted as a feature) is still
one run, one SDK build, the analyzer as corroborating instrument, and until #38 neither that
step nor any indexed `search_docs` section stated it. Re-asked on server 1.46.1, 2026-11-18, the
consequence is stated by `analyze_record` (`validation_guidance.valid_shapes`: "feature
attributes at the record root — flat, still supported") and by `sdk_guide(topic='load')`'s
compatibility note, so the observation-only label is gone and the text cites those routes. The
`search_docs` query still returns no section stating it, so the marker stays, as a ROUTING
negative naming those two routes as the owner (INV-080/INV-194/INV-213).

Source spec: `specs/routing-a-registered-feature-attribute-to-payload-is-silently-a-no-op.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE5 = (REPO_ROOT / "source" / "skills" /
           "module-05-data-quality-mapping")
PHASE2 = MODULE5 / "phase2-data-mapping.md"
PHASE3 = MODULE5 / "phase3-test-load.md"


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def collision_markers():
    """`(raw line, marker text)` for each wrapped marker whose claim is this collision.

    #323 — the marker is a single-line HTML comment, `<!-- MCP-NEGATIVE: … -->`, so it is
    found inside its wrapper and returned without it. The file also carries an unrelated
    wrapped marker (step 2's `embedded_in` key), so the collision marker is the one whose
    claim, before ` — owner: `, names a registered feature attribute.

    Line-scoped by design (#424): INV-209 requires the marker on ONE line, and #323 wraps it
    in a single-line HTML comment.
    """
    opener, closer = "<!-- ", " -->"
    found = []
    for line in PHASE2.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if raw.startswith(opener + "MCP-NEGATIVE:") and raw.endswith(closer):
            marker = raw[len(opener):-len(closer)]
            if "registered feature attribute" in marker.partition(" — owner: ")[0]:
                found.append((raw, marker))
    return found


class TheCollisionIsCaughtAtTheMappingGate(unittest.TestCase):

    def test_the_rule_is_stated_at_the_mapping_step(self):
        self.assertIn(
            "a root-level `payload` key MUST NOT be a registered feature attribute name",
            flat(PHASE2))

    def test_it_runs_before_the_plan_is_accepted(self):
        text = flat(PHASE2)
        self.assertIn("Before accepting the plan", text)
        self.assertIn("not after the output is analyzed", text)

    def test_it_reuses_the_catalog_lookup_the_module_already_makes(self):
        self.assertIn("the same lookup, asked of the other disposition", flat(PHASE2))


class TheBootcampersAnswerIsNotOverridden(unittest.TestCase):
    """INV-006 — their intent is achievable; only the key name is wrong."""

    def test_silent_re_routing_is_forbidden(self):
        self.assertIn("do NOT silently re-route or override the answer", flat(PHASE2))

    def test_the_collision_renames_the_key_without_a_question(self):
        """#488 — the rename carries out their "payload" answer, so it is not asked.

        Until #488 a pinned yes/no 👉 asked "Shall I store it as `{KEY}_PAYLOAD` instead…?",
        a question with one sensible answer. `test_confirmations_with_one_sensible_answer.py`
        pins its absence with a negative control.
        """
        text = flat(PHASE2)
        self.assertIn("**Emit `{KEY}_PAYLOAD`** in place of `{KEY}`", text)
        self.assertIn("**Say so in one line, as a statement**, naming the field and why", text)
        self.assertIn("**Ask no question for it.**", text)
        self.assertNotIn("Shall I store it as", text)

    def test_it_says_what_senzing_will_actually_do(self):
        self.assertIn("Senzing will resolve on it anyway", flat(PHASE2))

    def test_the_rename_and_a_reversal_are_recorded(self):
        text = flat(PHASE2)
        self.assertIn("**Record the rename in the mapping table's reasoning column**, so the "
                      "collision is never left unrecorded", text)
        self.assertIn("Record that they accept the field being matched on", text)


class AListValuedPayloadRouteIsWarned(unittest.TestCase):

    def test_the_join_behavior_is_stated_with_its_signature(self):
        text = flat(PHASE2)
        self.assertIn("joined into ONE literal value", text)
        self.assertIn("13,803 of 19,050 records", text)


class TheAnalyzerWarningMovesForward(unittest.TestCase):

    def test_phase_two_reads_the_schema_warnings_at_the_gate(self):
        self.assertIn("Surface the analyzer's SCHEMA warnings here", flat(PHASE2))

    def test_phase_three_routes_this_finding_back_rather_than_absorbing_it(self):
        """⛔ It must not be filed under the recommended-vs-flat conformance split."""
        text = flat(PHASE3)
        self.assertIn("One SCHEMA finding is NOT a conformance notice", text)
        self.assertIn("step 11's collision check did not run", text)


class TheGeneralShapeIsNamed(unittest.TestCase):
    """What the gates structurally cannot see."""

    def test_it_says_the_gates_check_the_plan_not_the_request(self):
        text = flat(PHASE2)
        self.assertIn("None of them confirms the plan does what the Bootcamper **asked "
                      "for**", text)

    def test_it_generalizes_to_any_behavior_selecting_answer(self):
        self.assertIn("Wherever a question's answer chooses a behavior", flat(PHASE2))


#: #38: the consequence is now stated by these routes (server 1.46.1, 2026-11-18). What the
#: paragraph must say, and the observation-only wording it must no longer carry.
CONSEQUENCE_KEPT = (
    "The consequence is documented too",
    "2026-08-17",
    "analyzer's own SCHEMA warning as the corroborating instrument",
    "`analyze_record`'s `validation_guidance.valid_shapes`",
    "feature attributes at the record root — flat, still supported",
    "the compatibility note of `sdk_guide`'s `load` topic",
    "**1.46.1, 2026-11-18**",
)
CONSEQUENCE_RETIRED = (
    "This mechanism is OBSERVATION-ONLY",
    "re-confirm before relying on it",
    "Treat the extracted-as-feature consequence as a strong local observation",
)


def consequence_problems(text):
    problems = ["the consequence paragraph no longer says %r" % k
                for k in CONSEQUENCE_KEPT if k not in text]
    problems += ["the consequence paragraph still says %r, which the 2026-11-18 re-ask retired" % r
                 for r in CONSEQUENCE_RETIRED if r in text]
    return problems


class ThePrecedenceMechanismIsMarkedObservationOnly(unittest.TestCase):
    """⛔ INV-080 — the consequence is cited to the routes that now state it (#38).

    Named for what it guarded before server 1.46.1 documented the consequence, and kept so its
    history stays readable: until 2026-11-18 it pinned the observation-only label.
    """

    def test_it_is_cited_to_the_routes_with_its_first_observation(self):
        self.assertEqual([], consequence_problems(flat(PHASE2)))

    def test_dropping_a_cited_route_fails(self):
        text = flat(PHASE2)
        for kept in CONSEQUENCE_KEPT[3:6]:
            with self.subTest(kept=kept):
                self.assertTrue(consequence_problems(text.replace(kept, "")))

    def test_restoring_the_observation_only_label_fails(self):
        text = flat(PHASE2)
        for retired in CONSEQUENCE_RETIRED:
            with self.subTest(retired=retired):
                self.assertTrue(consequence_problems(text + " " + retired))

    def test_the_absence_carries_a_well_formed_negative_marker(self):
        """INV-194 — a negative with no owning route does not parse and is not evidence.

        #323 — rescoped to the wrapped form: the marker is an HTML comment, so the date is
        anchored before the closing ` -->` rather than at the end of the line.
        """
        lines = collision_markers()
        self.assertEqual(1, len(lines), "expected exactly one marker in this file")
        raw, marker = lines[0]
        self.assertIn("owner:", marker, "the marker names no owning route")
        self.assertIn("routing negative", marker)
        self.assertRegex(raw, r"server \d+\.\d+\.\d+, \d{4}-\d{2}-\d{2} -->$")

    def test_the_marker_is_not_left_as_bare_prose(self):
        """#323 — dated maintainer metadata must not render inside the skill.

        Line-scoped by design (#424): a marker is bare when it opens a line outside a comment.
        """
        bare = [n for n, l in enumerate(PHASE2.read_text(encoding="utf-8").splitlines(), 1)
                if l.lstrip().startswith("MCP-NEGATIVE:")]
        self.assertEqual([], bare, "a bare MCP-NEGATIVE marker renders as body text")

    def test_the_rule_is_not_claimed_as_documented(self):
        """#322 — rescoped: the prohibition is cited to its route; the consequence is not.

        Named for what it guarded before the server documented the rule, and kept so its
        history stays readable: what it now refuses is the CONSEQUENCE being claimed as
        documented.
        """
        text = flat(PHASE2)
        self.assertIn("This prohibition is documented: `mapping_workflow` step 2's inline "
                      "*SENZING MAPPING REFERENCE*", text)
        self.assertIn('"must NOT be a registered feature attribute"', text)
        self.assertIn("server **1.37.16, 2026-10-01**", text)
        # #38: the consequence is now documented too, by other routes; see
        # `ThePrecedenceMechanismIsMarkedObservationOnly`.
        self.assertIn("`mapping_workflow` step 2 states only the prohibition", text)

    def test_the_prohibition_is_not_called_undocumented_again(self):
        """#322 — the old framing contradicted the tool the guide is already calling."""
        self.assertNotIn("not as a documented rule", flat(PHASE2))

    def test_the_marker_is_rescoped_to_the_consequence(self):
        """#322 / INV-213 — the claim is the consequence; the owner names the routes that carry it.

        #38: re-asked on server 1.46.1, 2026-11-18. The claim still holds; the owner moved from
        the Entity Specification's *Attribute reference* section (no longer among the query's
        hits) to `analyze_record` and `sdk_guide(topic='load')`, which state the consequence, so
        the marker is now a routing negative.
        """
        lines = collision_markers()
        self.assertEqual(1, len(lines), "expected exactly one marker in this file")
        _, marker = lines[0]
        self.assertEqual([], marker_owner_problems(marker))

    def test_the_old_owner_restored_fails(self):
        _, marker = collision_markers()[0]
        claim, _, _ = marker.partition(" — owner: ")
        old = (claim + " — owner: mapping_workflow step 2's inline SENZING MAPPING REFERENCE "
               "carries the prohibition (\"must NOT be a registered feature attribute\") but "
               "states no consequence of breaking it, so search_docs over the Entity "
               "Specification IS the route that would carry the consequence (absence negative) "
               "— server 1.37.16, 2026-10-01")
        self.assertTrue(marker_owner_problems(old))
        self.assertTrue(marker.startswith(
            "MCP-NEGATIVE: search_docs(query='payload attribute versus registered feature "
            "attribute record root extracted as feature precedence', "
            "category='data_mapping') — "),
            "the marker's query string or route changed")


def marker_owner_problems(marker):
    """What is wrong with the collision marker's claim and owner (#322, #38)."""
    problems = []
    if not marker.startswith(
            "MCP-NEGATIVE: search_docs(query='payload attribute versus registered feature "
            "attribute record root extracted as feature precedence', "
            "category='data_mapping') — "):
        problems.append("the marker's query string or route changed")
    claim, _, rest = marker.partition(" — owner: ")
    if ("no indexed section states that a root-level key named after a registered feature "
            "attribute is extracted as a feature") not in claim:
        problems.append("the claim is no longer the consequence")
    for needle in ("analyze_record(workspace_dir=", "validation_guidance.valid_shapes",
                   "sdk_guide's load topic",
                   "mapping_workflow step 2's inline SENZING MAPPING REFERENCE carries only "
                   "the prohibition", "(routing negative)"):
        if needle not in rest:
            problems.append("the owner clause does not name %r" % needle)
    for retired in ("states no consequence", "search_docs over the Entity Specification IS",
                    "(absence negative)"):
        if retired in rest:
            problems.append("the owner clause still says %r, retired on 2026-11-18" % retired)
    return problems


class TheCheckIsNotABlanketObjectionToPayload(unittest.TestCase):
    """Negative control: payload routing itself must stay ordinary and unobstructed."""

    def test_the_rule_is_scoped_to_registered_attribute_names(self):
        """A payload key that is not a registered attribute is untouched by the rule."""
        text = flat(PHASE2)
        self.assertIn("MUST NOT be a registered feature attribute name", text)
        self.assertNotIn("payload routing is discouraged", text)
        self.assertNotIn("avoid payload", text)

    def test_payload_remains_an_offered_disposition(self):
        self.assertIn("`feature`, `payload`, `ignore`, `derived`, or `extract`",
                      flat(PHASE2))

    def test_the_existing_rule_against_downgrading_to_payload_survives(self):
        self.assertIn("Never silently downgrade a bootcamper's choice to `payload`",
                      flat(PHASE2))


class TheGuidanceIsBehaviorNotAHelper(unittest.TestCase):
    """INV-002 — the catalog lookup is a data question, not a Python one."""

    def test_the_new_block_names_no_language_specific_helper(self):
        text = PHASE2.read_text(encoding="utf-8")
        start = text.index("Before accepting the plan")
        end = text.index("something must check the behavior was actually obtained.", start)
        block = text[start:end]
        for token in ("def ", "import ", "python3 "):
            with self.subTest(token=token):
                self.assertNotIn(token, block,
                                 "the rule is stated as code rather than as behavior")


if __name__ == "__main__":
    unittest.main()
