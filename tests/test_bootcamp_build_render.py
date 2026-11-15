"""The renderer turns host-neutral source text into one host's text.

Text outside a marker is copied unchanged, which is the property the whole design rests
on: what is not marked is the same on every assistant.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.model import BuildError, Host  # noqa: E402
from tools.bootcamp_build.render import RenderStats, render_text  # noqa: E402


def make_host(host_id="alpha", directory=None, **variables):
    return Host(
        id=host_id,
        name=host_id.title(),
        package_format="claude-plugin",
        vars={"product": "Alpha Code", **variables},
        layout={},
        hooks={},
        catalog=None,
        foreign_terms=(),
        directory=Path(directory or "/nonexistent"),
    )


def render(text, host=None, *, directives=True, known=("alpha", "beta"), stats=None):
    return render_text(
        text,
        host or make_host(),
        "example.md",
        directives=directives,
        known_hosts=set(known),
        stats=stats,
    )


class UnmarkedTextIsUntouched(unittest.TestCase):
    def test_text_without_markers_is_returned_byte_for_byte(self):
        text = "# Title\r\n\r\nA line with ${SHELL_VAR} and {braces} and }} and {{ other }}.\r\n"
        self.assertEqual(render(text), text)

    def test_a_missing_final_newline_stays_missing(self):
        self.assertEqual(render("no newline at end"), "no newline at end")


class Tokens(unittest.TestCase):
    def test_a_token_becomes_the_host_value(self):
        self.assertEqual(render("Use {{host.product}} here.\n"), "Use Alpha Code here.\n")

    def test_a_variable_the_host_does_not_define_is_an_error(self):
        with self.assertRaisesRegex(BuildError, "does not define variable 'missing'"):
            render("{{host.missing}}\n")

    def test_a_malformed_token_is_an_error_not_literal_output(self):
        for bad in ("{{ host.product }}", "{{host.Product}}", "{{host}}"):
            with self.subTest(bad=bad), self.assertRaisesRegex(BuildError, "malformed host token"):
                render(f"{bad}\n")

    def test_tokens_are_counted_for_the_parity_report(self):
        stats = RenderStats()
        render("{{host.product}} and {{host.product}}\n", stats=stats)
        self.assertEqual(stats.tokens, {"product": 2})
        self.assertEqual(stats.variation_points, 2)


class HostBlocks(unittest.TestCase):
    TEXT = (
        "before\n"
        "<!-- host:only alpha -->\n"
        "alpha line\n"
        "<!-- host:end -->\n"
        "<!-- host:except alpha -->\n"
        "everyone else\n"
        "<!-- host:end -->\n"
        "after\n"
    )

    def test_only_keeps_lines_for_the_listed_host(self):
        self.assertEqual(render(self.TEXT), "before\nalpha line\nafter\n")

    def test_except_drops_lines_for_the_listed_host(self):
        self.assertEqual(
            render(self.TEXT, make_host("beta")), "before\neveryone else\nafter\n"
        )

    def test_marker_lines_are_never_emitted(self):
        for host_id in ("alpha", "beta"):
            self.assertNotIn("host:", render(self.TEXT, make_host(host_id)))

    def test_a_list_of_hosts_is_accepted(self):
        text = "<!-- host:only alpha, beta -->\nboth\n<!-- host:end -->\n"
        self.assertEqual(render(text, make_host("beta")), "both\n")

    def test_tokens_in_a_dropped_block_are_not_evaluated(self):
        text = "<!-- host:only beta -->\n{{host.only_beta_has_this}}\n<!-- host:end -->\n"
        self.assertEqual(render(text), "")

    def test_nesting_is_an_error(self):
        text = "<!-- host:only alpha -->\n<!-- host:only beta -->\nx\n<!-- host:end -->\n"
        with self.assertRaisesRegex(BuildError, "cannot nest"):
            render(text)

    def test_an_unclosed_block_is_an_error(self):
        with self.assertRaisesRegex(BuildError, "never closed"):
            render("<!-- host:only alpha -->\nx\n")

    def test_end_without_a_block_is_an_error(self):
        with self.assertRaisesRegex(BuildError, "without an open host block"):
            render("<!-- host:end -->\n")

    def test_an_unknown_host_name_is_an_error(self):
        with self.assertRaisesRegex(BuildError, "unknown host 'gamma'"):
            render("<!-- host:only gamma -->\nx\n<!-- host:end -->\n")

    def test_a_directive_sharing_its_line_is_an_error(self):
        with self.assertRaisesRegex(BuildError, "malformed host directive"):
            render("text <!-- host:only alpha -->\n")

    def test_directives_outside_markdown_are_an_error(self):
        with self.assertRaisesRegex(BuildError, "Markdown files only"):
            render("<!-- host:only alpha -->\nx\n<!-- host:end -->\n", directives=False)


class Includes(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        (Path(self.directory.name) / "fragments").mkdir()

    def fragment(self, name, text):
        (Path(self.directory.name) / "fragments" / f"{name}.md").write_text(text, encoding="utf-8")

    def host(self):
        return make_host(directory=self.directory.name)

    def test_an_include_is_replaced_by_the_host_fragment(self):
        self.fragment("models", "Pick a model in {{host.product}}.\n")
        text = "intro\n<!-- host:include models -->\noutro\n"
        self.assertEqual(render(text, self.host()), "intro\nPick a model in Alpha Code.\noutro\n")

    def test_a_host_without_the_fragment_is_an_error(self):
        with self.assertRaisesRegex(BuildError, "has no fragment 'models'"):
            render("<!-- host:include models -->\n", self.host())

    def test_a_fragment_must_end_with_a_newline(self):
        self.fragment("models", "no newline")
        with self.assertRaisesRegex(BuildError, "must end with a newline"):
            render("<!-- host:include models -->\n", self.host())

    def test_a_fragment_cannot_contain_directives(self):
        self.fragment("models", "<!-- host:only alpha -->\nx\n<!-- host:end -->\n")
        with self.assertRaisesRegex(BuildError, "cannot contain host directives"):
            render("<!-- host:include models -->\n", self.host())

    def test_an_include_in_a_dropped_block_is_skipped(self):
        text = "<!-- host:only beta -->\n<!-- host:include models -->\n<!-- host:end -->\n"
        self.assertEqual(render(text, self.host()), "")


if __name__ == "__main__":
    unittest.main()
