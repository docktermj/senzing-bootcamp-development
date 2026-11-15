"""The Pages site's `claude plugin …` commands match `docs/README.md`'s (#455).

⚠️ **Dated note, 2026-11-14 (one-repository migration): the comparison this module made is now
true by construction, and its README half is retired.** `docs/index.html` and `docs/README.md`
were two hand-written files that repeated the same commands; both were deleted. The Claude
install page is now generated: `site/_install.html` is rendered once per assistant, and the
Claude commands are written in one place, `hosts/claude/fragments/site-install.html` and
`site-tips.html`. There is no second copy for the page to drift from. What still runs:

* the rendered Claude page carries exactly the `claude plugin …` commands its fragments hold,
  so a template that stopped including a fragment fails here, with the same negative controls
  (a changed command, an empty page, an empty other side);
* the retirement is still earned: no shared surface (`public/README.md`, `site/index.html`,
  `site/_install.html`) states a `claude plugin …` command of its own. If one does, the two-file
  agreement INV-348 describes exists again and the retired cases below must come back.

Retired, each where it stood: `readme_commands()` (the `console`-fence reader) with
`test_indented_console_fences_count_line_by_line` and `test_other_fences_and_prose_are_ignored`.
Their subject was a Markdown README carrying the Claude commands, and none does. The file keeps
its name because INV-348 names it as its enforcer. Everything below this note is the module's
description as it was, kept as the record.

`docs/index.html`, the GitHub Pages quick-start site dev owns since #452, repeats the install
commands of `docs/README.md`, and its header comment says it must follow them. Until this
module nothing checked that it did, so the two could drift silently, as the model names in
their prose already had.

⛔ **(INV-348) The page names exactly the `claude plugin …` commands `docs/README.md` names.** This
module extracts every `claude plugin …` command from the page (the text inside each
`<code>` element, HTML-unescaped, one command per non-blank stripped line) and from the README
(each non-blank stripped line inside its `console` fences, including the fences indented inside
list items), and asserts the two **sets** are equal. On a difference it lists the commands found
only on the page and those found only in the README.

⚠️ **Sets, deliberately.** The page shows `claude plugin update …` twice (the install step and
"Update or uninstall"), and it splits each README block that holds several commands into one
block per command (its header comment says so). Neither is drift, and comparing sets of lines
makes both invisible.

⛔ **An empty side fails, naming the file.** Without that, a broken extractor, or a page or
README that lost its commands, would compare `∅ == ∅` and pass. A negative control changes one
command on the page and shows the comparison fails.

⚠️ **What a green run does not establish.** Only `claude plugin …` commands are compared. The
page's other commands (`curl …`, `irm …`, `mkdir`, `cd`, `claude --model …`, "Start the
bootcamp"), the model names in prose, the slash-command table and the Claude Desktop route
(which follows the root `README.md`) are not checked. Nor is the propagated public tree: the
rewrite pass applies to both files alike, and
`tests/test_propagate_publishes_the_pages_site.py` checks the slug on the way out.

Source issue: #455.

Stdlib only (INV-108); the page is built into a scratch directory and read as text, no network.

Run:  python3 -m unittest discover -s tests
"""
import functools
import html.parser
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.model import SOURCE_DIR, load_declaration, load_hosts  # noqa: E402
from tools.bootcamp_build.site import build_site  # noqa: E402

# Adapted (one-repository migration, 2026-11-14): see the dated note in the docstring.
SITE_DIR = REPO_ROOT / "site"
FRAGMENTS_DIR = REPO_ROOT / "hosts" / "claude" / "fragments"
PAGE_REL = "claude/index.html (rendered)"
FRAGMENTS_REL = "hosts/claude/fragments/site-*.html"
#: The surfaces every assistant shares. None may state a `claude plugin …` command of its own.
SHARED_SURFACES = ("public/README.md", "site/index.html", "site/_install.html")

PREFIX = "claude plugin "


@functools.lru_cache(maxsize=None)
def rendered_page():
    """The Claude install page's HTML, rendered from the current template and fragments."""
    with tempfile.TemporaryDirectory() as scratch:
        out = Path(scratch) / "site"
        build_site(SITE_DIR, load_hosts(), load_declaration(SOURCE_DIR), out)
        return (out / "claude" / "index.html").read_text(encoding="utf-8")


def fragments_text():
    """Every Claude install fragment, joined: the one place the commands are written."""
    paths = sorted(FRAGMENTS_DIR.glob("site-*.html"))
    assert paths, "%s matched no file" % FRAGMENTS_REL
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


class _CodeText(html.parser.HTMLParser):
    """Collects the text of every `<code>` element, entities already unescaped."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "code":
            if self.depth == 0:
                self.blocks.append("")
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "code" and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.blocks[-1] += data


def _commands(lines):
    """The `claude plugin …` commands among `lines`, each stripped, as a set."""
    return {s for s in (line.strip() for line in lines) if s.startswith(PREFIX)}


def page_commands(text):
    """Every `claude plugin …` command inside a `<code>` element of the page."""
    parser = _CodeText()
    parser.feed(text)
    parser.close()
    return _commands(line for block in parser.blocks for line in block.splitlines())


# Retired (one-repository migration, 2026-11-14): `readme_commands()`, which read the commands
# out of a Markdown README's `console` fences. No README carries them now; see the docstring.


def drift(page_text, fragments):
    """None when the two sets match; otherwise the failure message, naming the side."""
    page, source = page_commands(page_text), page_commands(fragments)
    empty = ["%s yields no `claude plugin …` command inside <code>: the extractor or the file "
             "broke" % rel for rel, found in ((PAGE_REL, page), (FRAGMENTS_REL, source))
             if not found]
    if empty:
        return "; ".join(empty)
    if page == source:
        return None
    return ("the page's `claude plugin …` commands differ from its fragments'\n"
            "  only in %s:\n%s\n  only in %s:\n%s" % (
                PAGE_REL, "\n".join("    " + c for c in sorted(page - source)) or "    (none)",
                FRAGMENTS_REL,
                "\n".join("    " + c for c in sorted(source - page)) or "    (none)"))


def second_homes(texts):
    """The shared surfaces among ``texts`` ({name: text}) that state a `claude plugin …` command."""
    return sorted(name for name, text in texts.items() if PREFIX.strip() in " ".join(text.split()))


def shared_texts():
    return {rel: (REPO_ROOT / rel).read_text(encoding="utf-8") for rel in SHARED_SURFACES}


class ThePageFollowsItsFragments(unittest.TestCase):
    """The real files: the page carries the `claude plugin …` commands its fragments hold."""

    def test_the_two_sets_are_equal(self):
        problem = drift(rendered_page(), fragments_text())
        if problem:
            self.fail(problem)

    def test_both_sides_yield_commands(self):
        self.assertTrue(page_commands(rendered_page()),
                        "%s yields no `claude plugin …` command" % PAGE_REL)
        self.assertTrue(page_commands(fragments_text()),
                        "%s yields no `claude plugin …` command" % FRAGMENTS_REL)

    def test_the_install_and_the_update_commands_are_both_on_the_page(self):
        """Anchored on named commands, one from each fragment, so equality is not two halves."""
        verbs = {command.split()[2] for command in page_commands(rendered_page())}
        for verb in ("marketplace", "install", "update", "uninstall"):
            with self.subTest(verb=verb):
                self.assertIn(verb, verbs)


class TheRetirementIsStillEarned(unittest.TestCase):
    """⛔ One home for the commands is what makes the README comparison unnecessary."""

    def test_no_shared_surface_states_a_claude_plugin_command(self):
        self.assertEqual(
            [], second_homes(shared_texts()),
            "a surface every assistant shares states a `claude plugin …` command, so the "
            "commands have two homes again: restore this module's README comparison (INV-348)")

    def test_every_shared_surface_is_read(self):
        for rel in SHARED_SURFACES:
            with self.subTest(surface=rel):
                self.assertTrue((REPO_ROOT / rel).is_file(), "%s moved" % rel)

    def test_a_command_planted_on_a_shared_surface_is_reported(self):
        """Negative control: wrapped across a line or not, and naming the surface."""
        for planted in ("\n```console\nclaude plugin install a@b\n```\n",
                        "\n<p>Run <code>claude\n  plugin update a@b</code>.</p>\n"):
            with self.subTest(planted=planted):
                texts = shared_texts()
                texts["site/_install.html"] += planted
                self.assertEqual(["site/_install.html"], second_homes(texts))


class TheExtractorsReadWhatTheSpecSays(unittest.TestCase):
    """Synthetic inputs for the extraction rules."""

    def test_page_code_is_unescaped_and_stripped(self):
        page = "<p><code>  claude plugin install a&#64;b  </code> and <code>ls</code></p>"
        self.assertEqual(page_commands(page), {"claude plugin install a@b"})

    def test_text_outside_code_is_ignored(self):
        self.assertEqual(page_commands("<p>claude plugin install a@b</p>"), set())

    # Retired (one-repository migration, 2026-11-14):
    # `test_indented_console_fences_count_line_by_line` and
    # `test_other_fences_and_prose_are_ignored`, which pinned `readme_commands()` on a README's
    # `console` fences. The README that carried the commands was deleted and no other does.

    def test_duplicates_and_splitting_are_not_drift(self):
        page = ("<pre><code>claude plugin install a@b</code></pre>"
                "<pre><code>claude plugin update a@b</code></pre>"
                "<pre><code>claude plugin update a@b</code></pre>")
        fragments = "<pre><code>claude plugin install a@b\nclaude plugin update a@b</code></pre>"
        self.assertIsNone(drift(page, fragments))


class TheCheckCatchesDrift(unittest.TestCase):
    """Negative controls: a changed command and an empty side both fail, saying where."""

    def setUp(self):
        self.page = rendered_page()
        self.fragments = fragments_text()

    def test_changing_one_command_on_the_page_fails(self):
        before = sorted(page_commands(self.page))[0]
        after = before + "-drifted"
        mutated = self.page.replace(before, after)
        self.assertNotEqual(mutated, self.page, "the control mutated nothing")
        problem = drift(mutated, self.fragments)
        self.assertIsNotNone(problem, "a changed page command passed the comparison")
        self.assertIn("only in %s:\n    %s" % (PAGE_REL, after), problem)
        self.assertIn("only in %s:\n    %s" % (FRAGMENTS_REL, before), problem)

    def test_an_empty_page_fails_naming_the_page(self):
        problem = drift(self.page.replace("<code>", "<span>").replace("</code>", "</span>"),
                        self.fragments)
        self.assertIsNotNone(problem)
        self.assertIn(PAGE_REL, problem)
        self.assertNotIn(FRAGMENTS_REL, problem)

    def test_empty_fragments_fail_naming_the_fragments(self):
        # Adapted (one-repository migration, 2026-11-14): was
        # `test_an_empty_readme_fails_naming_the_readme`; the other side is now the fragments.
        problem = drift(self.page,
                        self.fragments.replace("<code>", "<span>").replace("</code>", "</span>"))
        self.assertIsNotNone(problem)
        self.assertIn(FRAGMENTS_REL, problem)
        self.assertNotIn(PAGE_REL, problem)


if __name__ == "__main__":
    unittest.main()
