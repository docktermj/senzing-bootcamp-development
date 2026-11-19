"""Each assistant's install page covers what its package names (#43).

Enforces **INV-443** and **INV-444** (both registered 2026-11-18); it cannot establish that
steps a page or a tip gives were ever followed.

An assistant's package and its install page are written in different files, and three gaps had
opened between them (findings 13, 25 and 27 of `production-readiness-audit-2026-11-17`):

- A package named an interface its page never mentioned. The GitHub Copilot package names
  VS Code and the ChatGPT package names the Codex CLI
  (`hosts/<assistant>/fragments/interface-naming.md`), so a reader in that interface found
  nothing on the page that said whether its steps were for them.
- Two pages gave steps to update and to uninstall, one gave steps to update only, and two
  gave neither.
- The GitHub Copilot package's own naming table requires "the GitHub Copilot app", and two of
  its own sentences said "the Copilot app".

What must hold, on every assistant:

- ⛔ **(INV-443) An install page names every interface its assistant's package names.**
  The names are the "Say" column of the assistant's naming table, without a leading article:
  "the Codex desktop app" is looked for as "Codex desktop app". The page is read as the build
  writes it and as a reader sees it, because a page may name its one interface in text that
  comes from the assistant's profile and not from a fragment (the Kiro page does).
- ⛔ **(INV-443) An install page that has no steps for an interface says the bootcamp has not been run there and that the page has no verified install steps for it.**
  It does not say the bootcamp supports the interface. Held for the two such interfaces
  recorded on 2026-11-17: VS Code on the GitHub Copilot page and the Codex CLI on the ChatGPT
  page.
- ⛔ **(INV-444) Every install page has one tip with the id `update-uninstall`, headed "Update or uninstall", whose text speaks of both updating and uninstalling.**
  It gives the steps, or says the page has no verified steps. The id is the same on every page
  because other text links to it.
- ⛔ **Text written for GitHub Copilot calls its desktop application "the GitHub Copilot app".**
  "Copilot app" without "GitHub " in front of it is reported, in any file under
  `hosts/copilot/`, in the built GitHub Copilot package and on its built install page.

⚠️ **What these checks cannot establish.** That a page's steps for an interface work, or were
ever followed: only a recorded run on that assistant shows that
(`hosts/<assistant>/checks.json`), and this module reads none. The first check finds a name; it
does not tell steps from a disclaimer, so the second check names the two interfaces it holds.
An interface added to a naming table must still be named on the page, but nothing here decides
whether the page then covers it honestly. The third check finds the words "update" and
"uninstall" in a tip; it does not judge the steps.

The assistants come from the build's own list (INV-246), every check fails when it finds
nothing to read, and each has a negative control that runs on every pass (INV-265). Text is
matched with whitespace collapsed, so a re-wrapped sentence is still found (INV-346).

Standard library only (INV-108). Paths are built with `pathlib` and files are read as UTF-8,
so the module does not depend on the platform (INV-001).

Run:  python3 -m unittest discover -s tests
"""
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from _built import built  # one assistant's package, built from the current files

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_declaration, load_hosts  # noqa: E402
from tools.bootcamp_build.site import build_site  # noqa: E402

HOSTS = REPO_ROOT / "hosts"
SITE_DIR = REPO_ROOT / "site"

TIP_ID = "update-uninstall"
TIP_HEADING = "Update or uninstall"

#: An interface a page has no steps for, by assistant: the name, and the `id` of the paragraph
#: that says so. Recorded on 2026-11-17 (#43).
WITHOUT_STEPS = {
    "copilot": ("VS Code", "vs-code"),
    "chatgpt": ("Codex CLI", "codex-cli"),
}

#: "Copilot app" with no "GitHub " in front of it. Read on whitespace-collapsed text.
BARE_COPILOT_APP = re.compile(r"(?<!GitHub )Copilot app")


def read(path):
    return Path(path).read_text(encoding="utf-8")


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


class _Visible(HTMLParser):
    """The text a reader sees: nothing from the head, a script or a style block."""

    HIDDEN = ("head", "script", "style", "template")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.HIDDEN:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in self.HIDDEN and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def visible(markup):
    """An HTML text as a reader sees it: tags dropped, entities decoded, whitespace collapsed."""
    parser = _Visible()
    parser.feed(markup)
    parser.close()
    return collapse(" ".join(parser.parts))


def said_names(table_markdown):
    """The "Say" column of a naming table, each name without its bold marks and leading article."""
    table = re.search(r"(?m)^\|\s*Say\s*\|\s*For\s*\|[^\n]*\n\|[-:| ]+\|[^\n]*\n((?:\|[^\n]*(?:\n|\Z))+)",
                      table_markdown)
    if not table:
        return []
    names = []
    for cell in re.findall(r"(?m)^\|([^|\n]*)\|", table.group(1)):
        name = collapse(cell.replace("*", ""))
        names.append(re.sub(r"(?i)^(?:the|an|a)\s+", "", name))
    return [name for name in names if name]


def missing_names(names, page_markup):
    """The names a reader of ``page_markup`` never sees."""
    text = visible(page_markup)
    return [name for name in names if name not in text]


def element(markup, element_id):
    """The inner markup of the `<p>` whose `id` is ``element_id``, or None."""
    found = re.search(r'<p\b[^>]*\bid="%s"[^>]*>(.*?)</p>' % re.escape(element_id), markup, re.S)
    return found.group(1) if found else None


def disclaimer_problems(markup, name):
    """What is wrong with the paragraph that says a page has no steps for ``name``."""
    if markup is None:
        return ["the paragraph is missing"]
    text = visible(markup)
    problems = []
    if name not in text:
        problems.append("does not name %s" % name)
    if not re.search(r"has not been run in (?:the )?%s\b" % re.escape(name), text):
        problems.append("does not say the bootcamp has not been run there")
    if "no verified install steps" not in text:
        problems.append("does not say the page has no verified install steps")
    if re.search(r"(?i)\bsupport", text):
        problems.append("speaks of support")
    return problems


class _Tips(HTMLParser):
    """Each `<div class="tip">` of a tips fragment: its id, its heading and the rest of its text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tips = []
        self.depth = 0  # how many <div>s deep inside the current tip, 0 outside one
        self.in_heading = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "div":
            if self.depth:
                self.depth += 1
            elif "tip" in (attributes.get("class") or "").split():
                self.depth = 1
                self.tips.append({"id": attributes.get("id"), "heading": [], "body": []})
        elif tag == "h3" and self.depth:
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == "div" and self.depth:
            self.depth -= 1
        elif tag == "h3":
            self.in_heading = False

    def handle_data(self, data):
        if self.depth:
            self.tips[-1]["heading" if self.in_heading else "body"].append(data)


def tips(fragment_markup):
    """[(id, heading, body text)] for every tip in a tips fragment."""
    parser = _Tips()
    parser.feed(fragment_markup)
    parser.close()
    return [(tip["id"], collapse(" ".join(tip["heading"])), collapse(" ".join(tip["body"])))
            for tip in parser.tips]


def tip_problems(fragment_markup):
    """What is wrong with a tips fragment's update and uninstall tip. Empty when nothing is."""
    found = [(heading, body) for tip_id, heading, body in tips(fragment_markup) if tip_id == TIP_ID]
    if not found:
        return ['no tip with the id "%s"' % TIP_ID]
    if len(found) > 1:
        return ['%d tips with the id "%s"' % (len(found), TIP_ID)]
    heading, body = found[0]
    problems = []
    if heading != TIP_HEADING:
        problems.append('headed "%s", not "%s"' % (heading, TIP_HEADING))
    if not re.search(r"(?i)\bupdat(?:e|es|ed|ing)\b", body):
        problems.append("its text does not speak of updating")
    if not re.search(r"(?i)\buninstall", body):
        problems.append("its text does not speak of uninstalling")
    return problems


def bare_copilot_app(text):
    """Each "Copilot app" in ``text`` with no "GitHub " in front of it, with the words around it."""
    flat = collapse(text)
    return [flat[max(0, match.start() - 40): match.end() + 20] for match in BARE_COPILOT_APP.finditer(flat)]


def text_files(root):
    """(path relative to ``root``, text) for every file under ``root`` that is text."""
    found = []
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file():
            continue
        try:
            found.append((path.relative_to(root).as_posix(), path.read_bytes().decode("utf-8")))
        except UnicodeDecodeError:
            continue
    return found


_pages = {}


def built_pages():
    """{assistant: its install page as the build writes it}, built once for the module."""
    if not _pages:
        with tempfile.TemporaryDirectory() as scratch:
            out = Path(scratch) / "site"
            build_site(SITE_DIR, load_hosts(), load_declaration(SOURCE_DIR), out)
            _pages.update({host: read(out / host / "index.html") for host in host_ids()})
    return _pages


class BuiltPages(unittest.TestCase):
    """What every class below reads: the assistants, their built pages and their naming tables."""

    @classmethod
    def setUpClass(cls):
        cls.hosts = host_ids()
        cls.pages = built_pages()

    def names(self, host):
        return said_names(read(HOSTS / host / "fragments" / "interface-naming.md"))


class EveryNamedInterfaceIsOnThePage(BuiltPages):
    def test_every_assistant_has_a_naming_table_that_names_an_interface(self):
        """Without this the check below would pass on a table it could not read (INV-265)."""
        self.assertGreaterEqual(len(self.hosts), 5)
        for host in self.hosts:
            with self.subTest(host=host):
                self.assertTrue(self.names(host), "no name read from the naming table")

    def test_names_are_read_as_the_table_gives_them(self):
        """Bold marks and the leading article go; nothing else does."""
        self.assertEqual(["Claude Desktop", "Claude Code CLI", "Claude web app", "Claude IDE extension"],
                         self.names("claude"))
        self.assertEqual(["GitHub Copilot app", "Copilot CLI", "VS Code"], self.names("copilot"))
        self.assertEqual(["Codex desktop app", "Codex CLI"], self.names("chatgpt"))
        self.assertEqual(["Antigravity CLI"], self.names("gemini"))
        self.assertEqual(["Kiro IDE"], self.names("kiro"))
        self.assertEqual(
            ["Desktop app", "IDE extension", "Thing"],
            said_names("intro\n\n| Say | For |\n| --- | --- |\n| **the Desktop app** | One. |\n"
                       "| **an IDE extension** | Two. |\n| **A Thing** | Three. |\n\n- after\n"))
        self.assertEqual([], said_names("| Name | For |\n| --- | --- |\n| **the Desktop app** | One. |\n"))

    def test_each_built_page_names_every_interface_its_package_names(self):
        for host in self.hosts:
            with self.subTest(host=host):
                self.assertEqual([], missing_names(self.names(host), self.pages[host]))

    def test_a_name_only_in_the_head_or_a_tag_is_not_on_the_page(self):
        """Negative control: what a reader cannot see does not count."""
        page = ('<html><head><title>Kiro IDE</title><meta name="description" content="Kiro IDE"></head>'
                '<body><p title="Kiro IDE">Install it.</p><script>var name = "Kiro IDE";</script></body></html>')
        self.assertEqual(["Kiro IDE"], missing_names(["Kiro IDE"], page))
        self.assertEqual([], missing_names(["Kiro IDE"], page.replace("Install it.", "In the Kiro\n IDE.")))

    def test_a_page_that_stops_naming_an_interface_is_reported(self):
        """Negative control on the real pages: take each name off its page in turn."""
        checked = 0
        for host in self.hosts:
            for name in self.names(host):
                with self.subTest(host=host, name=name):
                    # The words of a name may be split by a tag, as in a linked product name.
                    words = r"(?:\s|<[^>]+>)+".join(re.escape(word) for word in name.split())
                    without = re.sub(words, "it", self.pages[host])
                    self.assertNotEqual(self.pages[host], without)
                    self.assertIn(name, missing_names(self.names(host), without))
                    checked += 1
        self.assertGreaterEqual(checked, 11)


class AnInterfaceWithoutStepsIsDisclaimed(BuiltPages):
    def test_the_two_pages_say_the_bootcamp_has_not_been_run_there(self):
        for host, (name, element_id) in sorted(WITHOUT_STEPS.items()):
            with self.subTest(host=host, name=name):
                self.assertIn(name, self.names(host), "the naming table no longer names it")
                self.assertEqual([], disclaimer_problems(element(self.pages[host], element_id), name))

    def test_the_paragraph_is_reached_by_its_id_once(self):
        for host, (name, element_id) in sorted(WITHOUT_STEPS.items()):
            with self.subTest(host=host):
                self.assertEqual(1, self.pages[host].count('id="%s"' % element_id))

    def test_a_weaker_or_a_stronger_statement_is_reported(self):
        """Negative controls: each part of the statement, and a claim of support."""
        good = "Codex also runs in a terminal, as the Codex CLI. The bootcamp has not been run in " \
               "the Codex CLI, and this page has no verified install steps for it."
        self.assertEqual([], disclaimer_problems(good, "Codex CLI"))
        self.assertEqual([], disclaimer_problems(good.replace("in the Codex", "in\n   the  Codex"), "Codex CLI"))
        self.assertEqual(["the paragraph is missing"], disclaimer_problems(None, "Codex CLI"))
        self.assertEqual(["does not say the bootcamp has not been run there"], disclaimer_problems(
            good.replace("has not been run in", "may run in"), "Codex CLI"))
        self.assertEqual(["does not say the page has no verified install steps"], disclaimer_problems(
            good.replace("no verified install steps", "no steps"), "Codex CLI"))
        self.assertEqual(["speaks of support"], disclaimer_problems(
            good + " The bootcamp supports it.", "Codex CLI"))
        self.assertIn("does not name VS Code", disclaimer_problems(good, "VS Code"))
        for host, (name, element_id) in sorted(WITHOUT_STEPS.items()):
            with self.subTest(host=host):
                self.assertIsNone(element(self.pages[host].replace('id="%s"' % element_id, ""), element_id))


class EveryPageSaysHowToUpdateOrUninstall(BuiltPages):
    def fragment(self, host):
        return read(HOSTS / host / "fragments" / "site-tips.html")

    def test_every_tips_fragment_has_the_tip(self):
        self.assertGreaterEqual(len(self.hosts), 5)
        for host in self.hosts:
            with self.subTest(host=host):
                self.assertEqual([], tip_problems(self.fragment(host)))

    def test_every_built_page_carries_the_id_once(self):
        """A link to `#update-uninstall` lands on one place, on every page."""
        for host in self.hosts:
            with self.subTest(host=host):
                self.assertEqual(1, self.pages[host].count('id="%s"' % TIP_ID))

    def test_a_missing_misheaded_or_one_sided_tip_is_reported(self):
        """Negative controls, on fixtures and on every real fragment."""
        other = '<div class="tip" id="model"><h3>Model</h3><p>Update nothing. Uninstall nothing.</p></div>\n'
        wanted = ('<div class="tip" id="update-uninstall">\n  <h3>%s</h3>\n  <p>%s</p>\n'
                  '  <div class="cmd"><pre><code>tool plugin install x</code></pre></div>\n  <p>%s</p>\n</div>\n')
        tip = other + wanted
        self.assertEqual([], tip_problems(tip % (TIP_HEADING, "Update the plugin:", "Uninstall it in the panel.")))
        self.assertEqual(['headed "Update", not "Update or uninstall"', "its text does not speak of uninstalling"],
                         tip_problems(tip % ("Update", "Pull the latest download, then update:", "Done.")))
        self.assertEqual(["its text does not speak of updating"],
                         tip_problems(tip % (TIP_HEADING, "Pull the latest download.", "No uninstall steps.")))
        self.assertEqual(["its text does not speak of uninstalling"],
                         tip_problems(tip % (TIP_HEADING, "Update the plugin:", "Done.")))
        self.assertEqual(['no tip with the id "update-uninstall"'],
                         tip_problems('<div class="tip" id="model"><h3>Update or uninstall</h3>'
                                      "<p>Update. Uninstall.</p></div>"))
        self.assertEqual(['2 tips with the id "update-uninstall"'],
                         tip_problems(tip % (TIP_HEADING, "Update.", "Uninstall.")
                                      + wanted % (TIP_HEADING, "Update.", "Uninstall.")))
        for host in self.hosts:
            with self.subTest(host=host):
                fragment = self.fragment(host)
                self.assertEqual(['no tip with the id "update-uninstall"'],
                                 tip_problems(fragment.replace('id="%s"' % TIP_ID, 'id="update"')))
                self.assertIn('headed "Update", not "Update or uninstall"',
                              tip_problems(fragment.replace("<h3>%s</h3>" % TIP_HEADING, "<h3>Update</h3>")))
                one_sided = (re.sub(r"(?i)uninstall", "remove", fragment)
                             .replace('id="update-remove"', 'id="%s"' % TIP_ID)
                             .replace("<h3>Update or remove</h3>", "<h3>%s</h3>" % TIP_HEADING))
                self.assertEqual(["its text does not speak of uninstalling"], tip_problems(one_sided))


class TheCopilotPackageFollowsItsOwnNamingRule(BuiltPages):
    HOST = "copilot"

    def test_the_naming_table_requires_the_full_name(self):
        """The rule this class holds the package to is the package's own."""
        self.assertIn("GitHub Copilot app", self.names(self.HOST))

    def test_no_file_under_the_host_directory_shortens_the_name(self):
        files = text_files(HOSTS / self.HOST)
        self.assertTrue(any("GitHub Copilot app" in text for _, text in files),
                        "no file under hosts/%s names the app, so nothing was checked" % self.HOST)
        for relative, text in files:
            with self.subTest(file="hosts/%s/%s" % (self.HOST, relative)):
                self.assertEqual([], bare_copilot_app(text))

    def test_neither_the_built_package_nor_the_built_page_shortens_the_name(self):
        files = text_files(built(self.HOST))
        self.assertTrue(any("GitHub Copilot app" in collapse(text) for _, text in files),
                        "no file in the built package names the app, so nothing was checked")
        for relative, text in files:
            with self.subTest(file=relative):
                self.assertEqual([], bare_copilot_app(text))
        self.assertIn("GitHub Copilot app", visible(self.pages[self.HOST]))
        self.assertEqual([], bare_copilot_app(self.pages[self.HOST]))

    def test_the_short_name_is_reported_and_the_full_name_is_not(self):
        """Negative controls: the two sentences #43 corrected, and a name wrapped over two lines."""
        self.assertEqual(1, len(bare_copilot_app(
            "what a hook may tell the assistant differs between the Copilot app and the Copilot CLI.")))
        self.assertEqual(1, len(bare_copilot_app("<p>In the Copilot app, open <strong>Customize</strong>")))
        self.assertEqual(1, len(bare_copilot_app("the Copilot\napp")))
        self.assertEqual(2, len(bare_copilot_app("The Copilot app. The GitHub Copilot app. The Copilot app.")))
        self.assertEqual([], bare_copilot_app("differs between the GitHub Copilot app and the Copilot CLI."))
        self.assertEqual([], bare_copilot_app("in the GitHub\n  Copilot app, open"))
        self.assertEqual([], bare_copilot_app("GitHub Copilot in a terminal is the Copilot CLI."))


if __name__ == "__main__":
    unittest.main()
