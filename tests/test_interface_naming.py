"""Every reference to a Claude user interface names which one (INV-158).

Claude Code — which this plugin plugs into — runs in more than one interface, and
Claude Desktop runs Claude Code too. So "Claude Code" does not distinguish the terminal
from the desktop application, and "the Claude app" distinguishes nothing at all: a
bootcamper told to "set it with your Claude app's model and effort controls" has to guess
which controls are meant. The install instructions had the same problem from the other
side, offering "Claude Desktop (desktop)" beside "Claude Code (command line)" as though
they were different products.

`tests/test_retired_vocabulary.py` owns the negative half — "Claude app" may appear only
on a line that frames it as retired. This file owns the positive half, which a ban cannot
express: that both interfaces are actually documented, that the model/effort nudge names
each interface it adapts to, and that the two install paths point at each other with links
that resolve. The cross-document link is pinned because renaming a heading silently breaks
an anchor: nothing in a Markdown repo fails when `#using-claude-code` no longer exists.

⚠️ **Dated note, 2026-11-14 (one-repository migration): the install half reads the Claude install
fragment.** The root `README.md` is now the developer readme and `docs/README.md` is a carry-over
of the old Claude pages. The Claude walkthrough, with both paths on one page, is
`hosts/claude/fragments/site-install.html`, from which the build generates the Claude install
page; `public/README.md`, the host-neutral readme bootcampers see, names no Claude interface.
So each install check below reads that fragment as HTML: a path's `<h3>` stands where a README
heading stood, and the link from the list of paths to a path's `id` stands where the link
between the two documents stood. No case was retired.

Run:  python3 -m unittest discover -s tests
"""
import glob
import html
import os
import re
import unittest
from _built import built  # the Claude package, built from source/

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(str(built("claude")))
# Adapted (one-repository migration, 2026-11-14): see the dated note in the docstring.
README = os.path.join(REPO_ROOT, "public", "README.md")
HOSTS = os.path.join(REPO_ROOT, "hosts")
INSTALL = os.path.join(HOSTS, "claude", "fragments", "site-install.html")
INSTALL_TEMPLATE = os.path.join(REPO_ROOT, "site", "_install.html")
GROUND_RULES = os.path.join(PLUGIN, "skills", "bootcamp-onboarding", "ground-rules.md")
GRADUATION = os.path.join(PLUGIN, "skills", "graduation", "SKILL.md")
MODEL_SELECTION = os.path.join(PLUGIN, "docs", "model-selection.md")

# The canonical name of each interface the plugin can run in.
DESKTOP = "Claude Desktop"
CLI = "Claude Code CLI"
WEB = "Claude web app"
IDE = "Claude IDE extension"


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def flat(path):
    """`read` with whitespace collapsed, so a re-wrapped paragraph still matches."""
    return re.sub(r"\s+", " ", read(path))


def anchor(heading):
    """A Markdown heading's GitHub anchor."""
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug)


def visible(path):
    """An HTML file's text as a reader sees it: tags dropped, entities decoded, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", read(path)))).strip()


def ids(text):
    return set(re.findall(r'\bid="([\w-]+)"', text))


def path_heading(install_html, path_id):
    """The `<h3>` of the install path whose `id` is ``path_id``, or None when there is no such path."""
    found = re.search(r'<div class="path" id="%s">\s*<h3>(.*?)</h3>' % re.escape(path_id),
                      install_html, re.S)
    return found.group(1).strip() if found else None


def listed_path(install_html, name):
    """The `id` the list of paths links from its entry naming ``name``, or None."""
    paths = re.search(r'<ul class="paths">(.*?)</ul>', install_html, re.S)
    for target, label in re.findall(r'<a href="#([\w-]+)">(.*?)</a>', paths.group(1) if paths else "",
                                    re.S):
        if name in label:
            return target
    return None


def dangling_anchors(host):
    """In-page links in one assistant's install fragments that no `id` on its page answers."""
    fragments = sorted(glob.glob(os.path.join(HOSTS, host, "fragments", "site-*.html")))
    known = ids(read(INSTALL_TEMPLATE)).union(*(ids(read(path)) for path in fragments))
    return ["%s: #%s" % (os.path.relpath(path, REPO_ROOT), target)
            for path in fragments for target in re.findall(r'href="#([\w-]+)"', read(path))
            if target not in known]


class InstallDocsNameBothInterfaces(unittest.TestCase):
    def test_the_walkthrough_offers_both_by_name(self):
        text = visible(INSTALL)
        self.assertIn(DESKTOP, text)
        self.assertIn(CLI, text)

    def test_the_desktop_path_says_which_interface_it_covers(self):
        """A reader must know, before step 1, which interface they are following."""
        self.assertEqual(DESKTOP, path_heading(read(INSTALL), "claude-desktop"))

    def test_the_cli_path_says_which_interface_it_covers(self):
        self.assertEqual(CLI, path_heading(read(INSTALL), "claude-code-cli"))

    def test_the_link_to_the_cli_path_resolves(self):
        """Renaming an `id` silently breaks the anchor; nothing else catches it."""
        text = read(INSTALL)
        target = listed_path(text, CLI)
        self.assertIsNotNone(target, "the list of paths no longer links to the CLI path")
        self.assertEqual(CLI, path_heading(text, target),
                         "the list of paths links #%s, which is not the CLI path" % target)

    def test_the_link_to_the_desktop_path_resolves(self):
        text = read(INSTALL)
        target = listed_path(text, DESKTOP)
        self.assertIsNotNone(target, "the list of paths no longer links to the Desktop path")
        self.assertEqual(DESKTOP, path_heading(text, target),
                         "the list of paths links #%s, which is not the Desktop path" % target)

    def test_no_internal_anchor_dangles(self):
        """Every assistant's install page, every in-page anchor — the renamed troubleshooting
        heading is exactly the case that would break silently. The public README too."""
        hosts = sorted(name for name in os.listdir(HOSTS)
                       if glob.glob(os.path.join(HOSTS, name, "fragments", "site-*.html")))
        self.assertIn("claude", hosts)
        for host in hosts:
            with self.subTest(host=host):
                self.assertEqual([], dangling_anchors(host))
        text = read(README)
        headings = {anchor(m) for m in re.findall(r"^#+\s+(.*)$", text, re.M)}
        for target in re.findall(r"\]\(#([\w-]+)\)", text):
            with self.subTest(path="public/README.md", anchor=target):
                self.assertIn(target, headings)

    def test_the_anchor_checks_are_not_vacuous(self):
        """Negative controls (INV-265): a renamed `id` and a renamed heading are each reported."""
        text = read(INSTALL)
        self.assertTrue(re.findall(r'href="#([\w-]+)"', text), "the fragment links nothing in-page")
        renamed = text.replace('id="claude-code-cli"', 'id="using-the-cli"')
        self.assertNotEqual(text, renamed)
        self.assertIsNone(path_heading(renamed, listed_path(renamed, CLI)))
        self.assertIsNone(listed_path(text.replace(">Claude Code CLI</a>", ">The terminal</a>"), CLI))
        self.assertNotEqual(DESKTOP, path_heading(
            text.replace("<h3>Claude Desktop</h3>", "<h3>The desktop app</h3>"), "claude-desktop"))


class TheNudgeNamesEveryInterfaceItAdaptsTo(unittest.TestCase):
    """INV-098 adapts to four interfaces; INV-158 requires each to be named."""

    def test_ground_rules_names_all_four(self):
        text = flat(GROUND_RULES)
        for name in (CLI, DESKTOP, WEB, IDE):
            with self.subTest(interface=name):
                self.assertIn(name, text)

    def test_graduation_takes_the_interface_wording_from_ground_rules(self):
        """Graduation's nudge is ground-rules' nudge since #293, so the four names live there.

        Graduation carried its own copy of the switch question and its interface-adapted
        wording until then, and this test required that copy to name all four interfaces.
        It now points to ground-rules instead, and `test_ground_rules_names_all_four` holds
        the one copy to the same requirement. What is asserted here is that graduation did
        not fork the interface wording back in, and that its pointer reaches the copy that
        names them.
        """
        text = flat(GRADUATION)
        self.assertNotIn("Would you like to switch to", text)
        self.assertIn('`../bootcamp-onboarding/ground-rules.md` → "Module start banners and '
                      'transitions"', text)

    def test_the_model_table_note_names_the_cli_by_its_full_name(self):
        """Both copies of the table carry the note; INV-114 keeps them in sync."""
        for path in (GROUND_RULES, MODEL_SELECTION):
            with self.subTest(path=os.path.basename(path)):
                self.assertIn(CLI, flat(path))

    def test_the_unknown_interface_fallback_is_the_only_vague_wording(self):
        """"Your Claude interface" is honest when the interface is unknown, and a
        shortcut everywhere else — so it must appear only alongside that condition."""
        text = flat(GROUND_RULES)
        for match in re.finditer(r"your Claude interface", text):
            window = text[max(0, match.start() - 260) : match.end() + 120]
            self.assertRegex(
                window,
                r"cannot be determined|cannot tell|undeterminable|unknown interface",
                "vague interface wording outside the unknown-interface fallback",
            )


class TheDesktopPathIsNotDescribedAsSomethingElse(unittest.TestCase):
    def test_the_install_docs_do_not_oppose_desktop_to_claude_code(self):
        """The original defect: two interfaces of one product offered as rivals."""
        self.assertNotRegex(flat(README), r"\*\*Claude Code\*\*\s*\(command line\)")
        self.assertNotRegex(visible(INSTALL), r"Claude Code\s*\(command line\)")

    def test_the_walkthrough_states_that_desktop_runs_claude_code(self):
        self.assertRegex(
            visible(INSTALL),
            r"Claude Code plugin, and Claude Code has two interfaces"
            r"|Claude Code inside the desktop",
            "the walkthrough should say why both entries are the same plugin",
        )


if __name__ == "__main__":
    unittest.main()
