"""The documented slash-command set equals the shipped one, in both directions.

`source/commands/` is the shipped set — Claude Code discovers `commands/*.md`
by convention, and `.claude-plugin/plugin.json` correctly does not enumerate them. The documented
set was a hand-maintained table in `docs/README.md` (see the dated note below for where it is
read now). Nothing compared them, so they drifted:

    docs/README.md:76  "The plugin ships three slash commands."   <- five ship
    docs/README.md      table lists 3                              <- /bootcamp-note and
                                                                      /package-bootcamp absent
    README.md:92        "See [Bootcamp commands] for the other two."

⛔ **A prior audit already found and fixed this class** — *"two of three shipped slash commands
documented nowhere"*. It recurred because that fix wrote the missing rows instead of pinning the
set. So this test compares sets, and pins nothing else.

⛔ **No count is asserted anywhere in this file, deliberately.** A test that pins "five commands"
fails on the next legitimate addition and teaches whoever fixes it to bump a number — reproducing
the defect inside the guard. The two sets are derived and compared; their size is not the subject.

⚠️ **Both directions matter.** A documented command that no longer ships is equally wrong, and it
is the direction a delete-and-forget produces — the reader is told to run something that does not
exist.

⚠️ **Dated note, 2026-11-14 (one-repository migration): the documented set is read from the
rendered Claude install page.** `docs/README.md`, the old Claude user doc whose table this
compared, was deleted. Slash commands are the Claude package's (`source/commands/` lands as
`commands/*.md` there), so what documents them is the Claude install page, which the build
renders from `site/_install.html` and `hosts/claude/`. Its "Bootcamp requests" tip lists each
request in plain English and then names the slash commands (`site.commands_note` in
`hosts/claude/host.json`). The page is built here, into a scratch directory, and read as a
reader sees it. Both directions are kept, and the phantom direction now reads the whole page,
so a command named in the walkthrough is held to the shipped set too. The count checks read
that page and `public/README.md` where they read `docs/README.md`. No case was retired.

Stdlib only; the commands directory listed and the pages read as text (INV-108).

Source spec: `specs/the-documented-command-set-has-drifted-from-the-shipped-one.md`.

Run:  python3 -m unittest discover -s tests
"""
import functools
import html
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.model import SOURCE_DIR, load_declaration, load_hosts  # noqa: E402
from tools.bootcamp_build.site import build_site  # noqa: E402

COMMANDS_DIR = REPO_ROOT / "source" / "commands"
# Adapted (one-repository migration, 2026-11-14): see the dated note in the docstring.
SITE_DIR = REPO_ROOT / "site"
PUBLIC_README = REPO_ROOT / "public" / "README.md"
TOP_README = REPO_ROOT / "README.md"
PAGE_REL = "the Claude install page (site/_install.html rendered for hosts/claude)"

#: A slash command in visible text: `/name` that is not part of a path or a URL.
COMMAND = re.compile(r"(?<![\w/.:])/[a-z][a-z0-9-]*(?![\w-])(?!/|\.\w)")

#: The "Bootcamp requests" tip, from its opening tag to the next tip or the end of the list.
COMMANDS_TIP = re.compile(r'<div class="tip" id="commands">(.*?)(?=<div class="tip"|</section>)', re.S)

#: Prose asserting how many commands there are. The habit that produced two stale counts.
COUNT_CLAIM = re.compile(
    r"(?i)ships\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+slash\s+commands"
    r"|for the other\s+(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b")


@functools.lru_cache(maxsize=None)
def claude_install_page():
    """The Claude install page's HTML, rendered from the current template and fragments."""
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "site"
        build_site(SITE_DIR, load_hosts(), load_declaration(SOURCE_DIR), out)
        return (out / "claude" / "index.html").read_text(encoding="utf-8")


def visible(text):
    """HTML as a reader sees it: scripts and comments dropped, tags dropped, entities decoded."""
    text = re.sub(r"<(script|style)\b.*?</\1>|<!--.*?-->", " ", text, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def commands_tip(page):
    found = COMMANDS_TIP.search(page)
    assert found, "%s has no \"Bootcamp requests\" tip (id=\"commands\")" % PAGE_REL
    return found.group(1)


def shipped_commands():
    return {"/" + path.stem for path in COMMANDS_DIR.glob("*.md")}


def documented_commands(page=None):
    """The slash commands the page's "Bootcamp requests" tip names."""
    return set(COMMAND.findall(visible(commands_tip(page or claude_install_page()))))


def named_anywhere(page=None):
    """Every slash command named anywhere on the page, the walkthrough included."""
    return set(COMMAND.findall(visible(page or claude_install_page())))


class NeitherSetIsEmpty(unittest.TestCase):
    """INV-265 — a set comparison is satisfied trivially when both sides are empty."""

    def test_commands_were_found_on_disk(self):
        shipped = shipped_commands()
        self.assertGreaterEqual(
            len(shipped), 3,
            "fewer than three command files were found in %s; the glob has drifted and the "
            "comparison below proves nothing" % COMMANDS_DIR)
        self.assertIn("/start-bootcamp", shipped,
                      "the command glob is missing one certainly present; the pattern is wrong")

    def test_the_table_parsed(self):
        documented = documented_commands()
        self.assertGreaterEqual(
            len(documented), 3,
            "the \"Bootcamp requests\" tip of %s named fewer than three slash commands; the "
            "pattern has drifted from the tip's shape" % PAGE_REL)
        self.assertIn("/start-bootcamp", documented)

    def test_a_path_or_a_url_is_not_read_as_a_command(self):
        """Must-not-flag (INV-282): the page is full of slashes that name no command."""
        text = visible("<p>Saved to <code>docs/feedback/NOTES.md</code>, <code>src/</code> and "
                       "<code>backups/packages/</code>; see https://mcp.senzing.com/mcp, "
                       "choose <strong>&lt;/&gt; Code</strong>, then <code>/graduate</code> or "
                       "/package-bootcamp.</p>")
        self.assertEqual(["/graduate", "/package-bootcamp"], COMMAND.findall(text))


class TheTwoSetsAgree(unittest.TestCase):
    def test_every_shipped_command_is_documented(self):
        missing = sorted(shipped_commands() - documented_commands())
        self.assertEqual(
            [], missing,
            "shipped slash command(s) absent from the \"Bootcamp requests\" tip of %s: %s. A "
            "Bootcamper reading the documentation cannot discover them"
            % (PAGE_REL, ", ".join(missing)))

    def test_every_documented_command_ships(self):
        """The delete-and-forget direction: the reader told to run something that is gone."""
        phantom = sorted(named_anywhere() - shipped_commands())
        self.assertEqual(
            [], phantom,
            "%s names command(s) that do not ship: %s" % (PAGE_REL, ", ".join(phantom)))

    def test_a_command_struck_from_the_tip_is_reported(self):
        """Negative control: the tip without one shipped command no longer covers the set."""
        page = claude_install_page()
        tip = commands_tip(page)
        struck = page.replace(tip, tip.replace("/bootcamp-note", "a note"))
        self.assertNotEqual(page, struck, "the control struck nothing")
        self.assertEqual(["/bootcamp-note"], sorted(shipped_commands() - documented_commands(struck)))

    def test_a_phantom_command_in_the_walkthrough_is_reported(self):
        """Negative control: a command named outside the tip is held to the shipped set."""
        page = claude_install_page().replace("<code>/start-bootcamp</code>",
                                             "<code>/begin-bootcamp</code>")
        self.assertEqual(["/begin-bootcamp"], sorted(named_anywhere(page) - shipped_commands()))


class NoDocumentStatesACount(unittest.TestCase):
    """A count in prose is a positive false statement the moment a command is added."""

    def test_the_user_docs_state_no_count(self):
        for name, text in ((PAGE_REL, visible(claude_install_page())),
                           ("public/README.md",
                            " ".join(PUBLIC_README.read_text(encoding="utf-8").split()))):
            with self.subTest(document=name):
                hit = COUNT_CLAIM.search(text)
                self.assertIsNone(
                    hit, "%s states a number of slash commands (%r); state the set, not a "
                         "count -- the number goes stale silently while reading authoritative"
                         % (name, hit.group(0) if hit else ""))

    def test_the_top_readme_states_no_count(self):
        hit = COUNT_CLAIM.search(TOP_README.read_text(encoding="utf-8"))
        self.assertIsNone(
            hit, "README.md states a number of slash commands (%r)"
                 % (hit.group(0) if hit else ""))

    def test_the_count_check_reads_the_rendered_page(self):
        """Negative control: the sentence the old page carried is caught in the page's text."""
        page = claude_install_page().replace("Each also has a slash command:",
                                             "The plugin ships five slash\n commands:")
        self.assertNotEqual(claude_install_page(), page, "the control planted nothing")
        self.assertIsNotNone(COUNT_CLAIM.search(visible(page)))


if __name__ == "__main__":
    unittest.main()
