"""Every assistant gets the same model and effort rules, whichever wording carries them.

Claude's guidance names its commands; the other assistants share one wording that names
controls. The decisions must not differ: the same stages in the same order with the same
tier and effort, the same pinned confirmation gate, and the same invariants cited.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.emit import build_host  # noqa: E402
from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_declaration, load_host  # noqa: E402

GATE = "👉 **Are you done modifying the model and effort?** (Reply yes once you've set your model and effort; reply no if you need more time.)"
ROW = re.compile(r"^\s*\| ([A-Z][^|]+?) \| ([^|]+?), (medium|high) effort \|", re.M)
RULES = ("INV-063", "INV-098", "INV-137", "INV-138", "INV-139", "INV-158", "INV-236", "INV-247", "INV-251")


class ModelGuidanceIsTheSameEverywhere(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory()
        declaration, known = load_declaration(SOURCE_DIR), set(host_ids())
        cls.rules, cls.tiers = {}, {}
        for host_id in host_ids():
            host = load_host(host_id)
            build = build_host(declaration, host, SOURCE_DIR, Path(cls.scratch.name), known)
            cls.rules[host_id] = (build.root / "skills/bootcamp-onboarding/ground-rules.md").read_text(encoding="utf-8")
            cls.tiers[host_id] = {host.vars["model_balanced"]: "balanced", host.vars["model_capable"]: "capable"}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def stages(self, host_id):
        return [(stage, self.tiers[host_id][model], effort) for stage, model, effort in ROW.findall(self.rules[host_id])]

    def test_every_assistant_recommends_the_same_tier_and_effort_per_stage(self):
        reference = self.stages("claude")
        self.assertEqual(len(reference), 12)
        for host_id in host_ids():
            with self.subTest(host=host_id):
                self.assertEqual(self.stages(host_id), reference)

    def test_every_assistant_pins_the_same_confirmation_gate(self):
        for host_id, text in self.rules.items():
            with self.subTest(host=host_id):
                self.assertEqual(text.count(GATE), 1)

    def test_every_assistant_asks_the_switch_as_one_pinned_question(self):
        for host_id, text in self.rules.items():
            with self.subTest(host=host_id):
                self.assertIn("👉 **Would you like to switch to {Model} at {effort} reasoning effort for {this module | graduation}?**", text)

    def test_every_wording_cites_the_same_rules(self):
        for host_id, text in self.rules.items():
            for rule in RULES:
                with self.subTest(host=host_id, rule=rule):
                    self.assertIn(rule, text)

    def test_no_assistant_but_claude_is_told_to_type_a_claude_command(self):
        for host_id, text in self.rules.items():
            if host_id != "claude":
                with self.subTest(host=host_id):
                    self.assertNotRegex(text, r"`/effort\b")


if __name__ == "__main__":
    unittest.main()
