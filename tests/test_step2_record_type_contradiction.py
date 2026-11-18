"""Step 10's `record_type` guidance, and the note that was retired under its own condition.

`mapping_workflow`'s step-2 response used to contradict itself about `record_type`: its
instructions said *"set record_type to `MIXED`"* on a discriminated source, while the **same
response's** `advance_schema` declared `record_type` as
`enum: ["PERSON", "ORGANIZATION", "VESSEL", "AIRCRAFT"]`. Sending `MIXED` was accepted and warned.
Reproduced live on **MCP server 1.33.0, 2026-08-21** by running `mapping_workflow` start ->
step 1 -> step 2 with an 8-field mixed-type source:

    warnings: ["schema_plan[0] (watchlist_pep): record_type 'MIXED' is non-standard —
               expected one of: PERSON, ORGANIZATION, VESSEL, AIRCRAFT"]

So the plugin pre-empted it with an enum-valid type and step 3's `type_discriminator`, and the
note carried, in shipped text, the condition under which it should be removed: "Retire this note
once step 2's prose and its `advance_schema` agree." Nothing in an offline suite (INV-108) can
notice the server has been fixed, so the condition was the only route to retiring it.

**Retired under that condition (#38).** Re-read live on **server 1.46.1, 2026-11-18**: the step-2
prose now says *"set record_type to the DOMINANT type (e.g. PERSON or ORGANIZATION — do NOT send
"MIXED": it is not a type, only a literal string here)"*, and its `advance_schema` declares
`record_type` as free text (*"The usual values are PERSON, ORGANIZATION, VESSEL and AIRCRAFT; any
other value (e.g. VEHICLE) is accepted"*). Prose and schema agree, so the contradiction note and
its warning paragraph are gone, and the instruction stays, cited to what the server now says.
Sending `MIXED` now returns an advisory warning ("any value is accepted, so this is advisory
only"). These tests pin that state, and each check has a negative control that restores a retired
sentence or removes a kept one.

Source spec: `specs/step-2-prose-prescribes-a-record-type-its-own-schema-rejects.md`.

Run:  python3 -m unittest discover -s tests
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE2 = (REPO_ROOT / "source" / "skills"
          / "module-05-data-quality-mapping" / "phase2-data-mapping.md")

#: What step 10 must still say, each with the reason its absence is a defect.
KEPT = (
    ("send the source's dominant type as `record_type`",
     "step 10 does not tell the guide what to send on a mixed-type source"),
    ("never `MIXED`",
     "step 10 does not rule out sending `MIXED`"),
    ("set record_type to the DOMINANT type",
     "the server's own instruction is not quoted, so the rule cites nothing the server says"),
    ("declares `record_type` as free text",
     "the note does not say the schema is free text, which is why the note could retire"),
    ("prose and its schema now agree",
     "the note does not say the prose and the schema agree"),
    ("VESSEL and AIRCRAFT",
     "a guide will not know VESSEL and AIRCRAFT are usual values, which a watchlist needs"),
    ("server **1.46.1, 2026-11-18**",
     "the instruction is not dated, so a later reader cannot tell it was re-read"),
)
#: What the retired note said, each with the reason its return is a defect.
RETIRED = (
    ('set record_type to `"MIXED"`',
     "the step-2 prose no longer says to send MIXED (server 1.46.1, 2026-11-18)"),
    ('enum: ["PERSON"',
     "the step-2 advance_schema no longer declares record_type as an enum"),
    ("its own schema rejects",
     "the contradiction this note described is fixed upstream"),
    ("Retire this note once step 2's prose and its `advance_schema` agree",
     "the retirement condition was met; a note still carrying it was not retired"),
    ("not your error and not a mapping defect",
     "the MIXED-warning paragraph was retired with the note"),
    ("is non-standard",
     "the server's MIXED warning no longer says non-standard"),
)


def plan_step(text=None):
    """The step-10 (Plan) section, where the step-2 advance is committed, whitespace-collapsed."""
    text = PHASE2.read_text(encoding="utf-8") if text is None else text
    start = text.index("### 10. Plan")
    end = text.index("### 11. Map", start)
    return re.sub(r"\s+", " ", text[start:end])


def plan_problems(plan):
    problems = [why for needle, why in KEPT if needle not in plan]
    problems += [why for needle, why in RETIRED if needle in plan]
    return problems


class TheScanIsNotVacuous(unittest.TestCase):
    def test_the_file_exists(self):
        self.assertTrue(PHASE2.is_file(), "phase2-data-mapping.md moved")

    def test_the_plan_step_is_locatable(self):
        self.assertIn("record_id_source", plan_step(),
                      "the Plan step was not located, so every check below is vacuous")


class TheContradictionIsPreEmptedAtTheStepThatHitsIt(unittest.TestCase):
    """The instruction stays at step 10, cited to the server's own words (#38)."""

    def setUp(self):
        self.plan = plan_step()

    def test_the_shipped_step_is_clean(self):
        self.assertEqual([], plan_problems(self.plan))

    def test_it_prescribes_the_dominant_type(self):
        for needle, why in KEPT[:2]:
            with self.subTest(kept=needle):
                self.assertIn(why, plan_problems(self.plan.replace(needle, "")))

    def test_it_quotes_the_servers_instruction_and_schema(self):
        for needle, why in KEPT[2:5]:
            with self.subTest(kept=needle):
                self.assertIn(why, plan_problems(self.plan.replace(needle, "")))

    def test_it_names_vessel_and_aircraft(self):
        needle, why = KEPT[5]
        self.assertIn(why, plan_problems(self.plan.replace(needle, "")))

    def test_restoring_a_retired_quote_fails(self):
        for needle, why in RETIRED[:3]:
            with self.subTest(retired=needle):
                self.assertIn(why, plan_problems(self.plan + " " + needle))

    def test_restoring_the_warning_paragraph_fails(self):
        for needle, why in RETIRED[4:]:
            with self.subTest(retired=needle):
                self.assertIn(why, plan_problems(self.plan + " " + needle))


class TheNoteCarriesItsOwnRetirementCondition(unittest.TestCase):
    """The condition the note carried was met, and the note is gone (#38).

    Negative-controlled by restoring the retirement sentence and by dropping the date.
    """

    def setUp(self):
        self.plan = plan_step()

    def test_the_retirement_condition_was_met_and_the_note_is_gone(self):
        needle, why = RETIRED[3]
        self.assertNotIn(needle, self.plan)
        self.assertIn(why, plan_problems(self.plan + " " + needle))

    def test_the_claim_is_dated_and_versioned(self):
        needle, why = KEPT[6]
        self.assertIn(needle, self.plan)
        self.assertIn(why, plan_problems(self.plan.replace(needle, "server 1.33.0")))


if __name__ == "__main__":
    unittest.main()
