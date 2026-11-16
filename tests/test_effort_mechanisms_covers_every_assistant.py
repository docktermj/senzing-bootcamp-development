"""The effort research names every assistant the bootcamp is built for (issue #5).

``docs/effort-mechanisms.md`` is what issue #4 chooses its mechanism from. An assistant added
under ``hosts/`` with no row there would get that mechanism by default, unexamined.

Line-scoped by design (#5): a Markdown table row is one line, and the rows are what is counted.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "effort-mechanisms.md"
HOSTS = REPO_ROOT / "hosts"


def findings_rows(text):
    """First cells of the table under ``## Findings``, header and rule left out."""
    section = text.split("## Findings", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in section.splitlines() if line.startswith("|")]
    return [row.split("|")[1].strip() for row in rows[2:]]


class EffortMechanismsCoverEveryAssistant(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")

    def test_every_assistant_has_exactly_one_row(self):
        rows = findings_rows(self.text)
        products = []
        for host in sorted(path for path in HOSTS.iterdir() if (path / "host.json").is_file()):
            products.append(json.loads((host / "host.json").read_text(encoding="utf-8"))["vars"]["product"])
        self.assertTrue(products)
        for product in products:
            with self.subTest(product=product):
                self.assertEqual(sum(1 for row in rows if product in row), 1, rows)
        self.assertEqual(len(rows), len(products), rows)

    def test_every_row_says_how_it_was_verified(self):
        section = self.text.split("## Findings", 1)[1].split("\n## ", 1)[0]
        for row in [line for line in section.splitlines() if line.startswith("|")][2:]:
            with self.subTest(row=row[:40]):
                self.assertRegex(row.split("|")[-2], r"Live, .+ \d{4}-\d{2}-\d{2}|Documentation only")

    def test_it_says_what_was_not_verified_and_recommends(self):
        self.assertIn("## What was not verified", self.text)
        recommendation = self.text.split("## Recommendation for issue #4", 1)
        self.assertEqual(len(recommendation), 2)
        self.assertIn("**Use ", recommendation[1])


if __name__ == "__main__":
    unittest.main()
