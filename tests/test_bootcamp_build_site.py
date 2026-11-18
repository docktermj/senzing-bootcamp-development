"""The published pages: one landing page, and one install page per assistant from one template.

A host cannot have a package without a page, and no page can point a bootcamper at one of the
retired per-assistant repositories.

⛔ **Every assistant's install page states the Python requirement its package relies on: `python3` on the `PATH`.**

Every package runs the bundled scripts as ``python3``, so a page that accepts another command
name promises a bootcamp that then fails at its first script. Until issue #42 the Kiro page
said "Python 3.10 or later" and "Any command name works (`python3`, `python` or `py`)", while
the Kiro package and the other four pages required ``python3``. The rule is drafted as a
deferred invariant in the ``specs/IMPLEMENTED.md`` entry for issue #42 and awaits the
maintainer. The test reads each page's words. It cannot establish that ``python3`` is on any
bootcamper's ``PATH``, and it states no minimum Python version, because none is recorded for
the bootcamp's own scripts.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_declaration, load_hosts  # noqa: E402
from tools.bootcamp_build.site import build_site, site_hosts  # noqa: E402

SITE_DIR = REPO_ROOT / "site"
RETIRED = re.compile(r"senzing-bootcamp-(?:claude|copilot|chatgpt|gemini)-plugin|senzing-bootcamp-kiro-power")
FRAGMENTS = ("site-before.html", "site-install.html", "site-tips.html")
PYTHON_ON_PATH = "<code>python3</code> on the <code>PATH</code>"
ANY_COMMAND_NAME = "Any command name works"
KIRO_PYTHON_ITEM = (
    "<li><strong>Python 3</strong>, available as <code>python3</code> on the <code>PATH</code>. The "
    "bootcamp's graduation recap and its optional hooks run on it. On Windows, if only <code>python</code> "
    "or <code>py</code> is installed, add a <code>python3</code> entry to the <code>PATH</code>.</li>"
)


class Site(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory()
        cls.out = Path(cls.scratch.name) / "site"
        cls.hosts = load_hosts()
        cls.files = build_site(SITE_DIR, cls.hosts, load_declaration(SOURCE_DIR), cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def page(self, relative):
        return (self.out / relative).read_text(encoding="utf-8")

    def test_every_host_has_a_page_and_its_fragments(self):
        self.assertEqual([host.id for host in site_hosts(self.hosts)] and
                         sorted(host.id for host in site_hosts(self.hosts)), host_ids())
        for host in self.hosts:
            with self.subTest(host=host.id):
                self.assertIn(f"{host.id}/index.html", self.files)
                for name in FRAGMENTS:
                    self.assertTrue(host.fragment_path(name).is_file(), name)

    def test_no_page_keeps_an_unrendered_marker(self):
        for relative in self.files:
            if relative.endswith(".html"):
                with self.subTest(page=relative):
                    text = self.page(relative)
                    self.assertNotIn("{{", text)
                    self.assertNotRegex(text, r"<!--\s*(?:host|site):")

    def test_the_landing_page_links_to_every_assistant_and_counts_them(self):
        landing = self.page("index.html")
        for host in self.hosts:
            with self.subTest(host=host.id):
                self.assertIn(f'id="platform-{host.id}"', landing)
                self.assertIn(f'href="{host.id}/"', landing)
        words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
        self.assertIn(f"Same bootcamp, {words[len(self.hosts)]} AI assistants", landing)

    def test_each_install_page_offers_every_other_assistant(self):
        for host in self.hosts:
            text = self.page(f"{host.id}/index.html")
            for other in self.hosts:
                with self.subTest(page=host.id, other=other.id):
                    link = f'href="../{other.id}/"'
                    (self.assertNotIn if other.id == host.id else self.assertIn)(link, text)

    def test_every_page_installs_from_the_one_public_repository(self):
        for relative in self.files:
            if relative.endswith(".html"):
                with self.subTest(page=relative):
                    self.assertIsNone(RETIRED.search(self.page(relative)))
        for host in self.hosts:
            with self.subTest(host=host.id):
                self.assertRegex(self.page(f"{host.id}/index.html"), r"Senzing/bootcamp")

    def test_every_install_page_has_the_same_sections_in_the_same_order(self):
        outlines = {
            host.id: re.findall(r'<section[^>]*id="([^"]+)"', self.page(f"{host.id}/index.html"))
            for host in self.hosts
        }
        self.assertEqual(len({tuple(outline) for outline in outlines.values()}), 1, outlines)

    def test_the_feedback_file_is_named_the_same_for_every_assistant(self):
        for host in self.hosts:
            with self.subTest(host=host.id):
                self.assertIn("docs/feedback/SENZING_BOOTCAMP_FEEDBACK.md", self.page(f"{host.id}/index.html"))

    def test_every_install_page_states_the_python_requirement_its_package_relies_on(self):
        self.assertTrue(self.hosts, "no assistant was read")
        for host in self.hosts:
            with self.subTest(host=host.id):
                text = self.page(f"{host.id}/index.html")
                self.assertIn(PYTHON_ON_PATH, text)
                self.assertNotIn(ANY_COMMAND_NAME, text)

    def test_the_kiro_page_states_python3_on_the_path_and_no_version_floor(self):
        text = self.page("kiro/index.html")
        self.assertEqual(text.count(KIRO_PYTHON_ITEM), 1)
        self.assertNotIn("3.10 or later", text)
        self.assertNotIn(ANY_COMMAND_NAME, text)


if __name__ == "__main__":
    unittest.main()
