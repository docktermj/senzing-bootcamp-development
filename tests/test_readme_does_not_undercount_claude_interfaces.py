"""`README.md` must not tell the Bootcamper which Claude interfaces exist.

Before the 2026-08-26 fix, the install walkthrough opened with:

    Claude Code has two interfaces you can run it in.
    Pick either:
    - Claude Desktop …
    - Claude Code CLI …

**INV-098 handles four** — the Claude Code CLI, Claude Desktop, the Claude web app, and a Claude
IDE extension — so the plugin had interface-specific behavior for two contexts its own front door
said did not exist.

⛔ **The severity is that "pick either" is an INSTRUCTION, not a description.** A Bootcamper
running Claude Code in the web app or a VS Code / JetBrains extension read it, found neither
option described what they were using, and had no install path — while the bootcamp itself would
have adapted correctly once started.

⚠️ **The fix is scoping the sentence, not inventing install steps.** The walkthrough may
legitimately carry verified steps for two interfaces; what it may not do is assert that two is
all there are. Adding unverified instructions for the other two would be a new defect, so this
guard checks that the other contexts are **named and their install path disclosed as unverified**
— never that steps exist for them (INV-111/INV-163's disclose-rather-than-imply discipline).

⛔ **The context list is derived from INV-098's own text**, not hardcoded here, so this guard
cannot go stale the way the prose did. If INV-098 gains a fifth context, this test starts
requiring it.

⚠️ **Dated note, 2026-11-14 (one-repository migration): this reads the public README and the
Claude install fragments.** The root `README.md` is now the developer readme and
`docs/README.md` is a carry-over of the old Claude pages. What a bootcamper reads is
`public/README.md`, which is host-neutral, and the Claude install page, which the build
generates from `hosts/claude/fragments/site-*.html`; the walkthrough is `site-install.html`.
The fragments are HTML, so they are matched on their visible text. The claim that the plugin
works wherever Claude Code runs is now worded "other Claude Code clients also run the plugin",
and the IDE context is named by its product, "Claude Code for VS Code". Two things the old
README said have no counterpart in either file and are retired, each where it stood: the
Claude web app is not named (`NOT_NAMED`), and nothing says the other clients have no verified
install steps.

Stdlib only; INVARIANTS.md, the public README and the fragments read as text (INV-108).

Source spec: `specs/readme-claims-two-interfaces-while-inv098-handles-four.md`.

Run:  python3 -m unittest discover -s tests
"""
import html
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# Adapted (one-repository migration, 2026-11-14): see the dated note in the docstring.
TOP_README = REPO_ROOT / "public" / "README.md"
CLAUDE_FRAGMENTS = REPO_ROOT / "hosts" / "claude" / "fragments"
WALKTHROUGH = CLAUDE_FRAGMENTS / "site-install.html"
INVARIANTS = REPO_ROOT / "specs" / "INVARIANTS.md"

#: Prose asserting how many interfaces Claude Code has.
INTERFACE_COUNT = re.compile(
    r"(?i)Claude Code has\s+(one|two|three|four|five|\d+)\s+interfaces")

#: The contexts INV-098 enumerates, read out of the invariant itself.
CONTEXT_NAMES = ("Claude Code CLI", "Claude Desktop", "Claude web app", "Claude IDE extension")

#: How the user-facing docs name a context, where it is not INV-098's own wording. Adapted
#: (one-repository migration, 2026-11-14): the walkthrough names the IDE context by its product.
NAMED_AS = {"Claude IDE extension": ("IDE extension", "Claude Code for VS Code")}

#: Retired (one-repository migration, 2026-11-14): contexts INV-098 names that neither the public
#: README nor the Claude install fragments name, each with what is missing. ⛔ An explicit list,
#: never a pattern: `test_every_unnamed_context_is_still_unnamed` fails once the docs name one.
NOT_NAMED = {
    "Claude web app": "the walkthrough says only \"other Claude Code clients\"; the old README "
                      "named the Claude web app beside the IDE extensions",
}


def inv098_text():
    for line in INVARIANTS.read_text(encoding="utf-8").splitlines():
        if line.startswith("- **INV-098**"):
            return line
    raise AssertionError("INV-098 not found in INVARIANTS.md")


def contexts_from_inv098():
    """The interface contexts INV-098 actually names, derived rather than assumed."""
    text = inv098_text()
    return [name for name in CONTEXT_NAMES if name.lower() in text.lower()]


def flat(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def visible(text):
    """HTML as a reader sees it: tags dropped, entities decoded, whitespace collapsed."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def claude_pages():
    """The visible text of every Claude install fragment, the walkthrough among them."""
    paths = sorted(CLAUDE_FRAGMENTS.glob("site-*.html"))
    assert WALKTHROUGH in paths, "%s is missing" % WALKTHROUGH
    return " ".join(visible(path.read_text(encoding="utf-8")) for path in paths)


def user_facing():
    """Everything a bootcamper using Claude reads before the bootcamp starts."""
    return flat(TOP_README) + " " + claude_pages()


def names_context(docs, context):
    return any(stem in docs for stem in NAMED_AS.get(context, (context,)))


class TheDerivationIsNotVacuous(unittest.TestCase):
    """INV-265 — an empty context list would satisfy every assertion below."""

    def test_inv098_still_enumerates_several_contexts(self):
        contexts = contexts_from_inv098()
        self.assertGreaterEqual(
            len(contexts), 3,
            "INV-098 now names fewer than three interface contexts (%s). Either the invariant "
            "changed -- in which case this guard's expectations should follow it -- or the "
            "derivation has drifted and the checks below are vacuous" % contexts)
        self.assertIn("Claude web app", contexts,
                      "INV-098 no longer names the Claude web app; if that is deliberate, this "
                      "test and README.md should both be revisited together")


class TheReadmeStatesNoInterfaceCount(unittest.TestCase):
    def test_no_count_of_interfaces(self):
        hit = INTERFACE_COUNT.search(user_facing())
        self.assertIsNone(
            hit,
            "the public README or a Claude install fragment asserts how many interfaces Claude "
            "Code has (%r). It is not the plugin's fact to state, it goes stale silently, and it "
            "made 'pick either' unanswerable for readers in the contexts it omitted"
            % (hit.group(0) if hit else ""))

    def test_it_does_not_tell_the_reader_to_pick_from_a_partial_set(self):
        self.assertNotIn(
            "interfaces you can run it in. Pick either", user_facing(),
            "the install docs still instruct the reader to pick from a two-item set presented as "
            "exhaustive")

    def test_it_says_the_plugin_works_wherever_claude_code_runs(self):
        """The replacement claim, which is true and does not need maintaining."""
        self.assertRegex(
            claude_pages(),
            r"(?i)works wherever Claude Code runs|other Claude Code clients also run the plugin",
            "the Claude walkthrough no longer states that the plugin runs in the other Claude "
            "Code clients, so scoping its steps to two interfaces reads as a limitation of the "
            "plugin")

    def test_the_count_check_reads_the_fragments(self):
        """Negative control (INV-265): the old sentence, in a fragment's HTML, is reported."""
        old = visible("<p>Claude Code has <strong>two</strong>\ninterfaces you can run it in.</p>")
        self.assertTrue(INTERFACE_COUNT.search(old))
        self.assertIn("Claude Code inside the desktop application", claude_pages())


class EveryContextInv098HandlesIsNamed(unittest.TestCase):
    def test_each_context_appears_in_the_user_facing_docs(self):
        docs = user_facing()
        checked = [context for context in contexts_from_inv098() if context not in NOT_NAMED]
        self.assertGreaterEqual(len(checked), 3, "almost every context is exempt; nothing is checked")
        for context in checked:
            with self.subTest(context=context):
                # INV-098 says "a Claude IDE extension"; the docs may pluralize or name the product.
                self.assertTrue(
                    names_context(docs, context),
                    "INV-098 adapts the bootcamp's behavior to '%s', and no user-facing document "
                    "mentions it -- so a Bootcamper there is not told the plugin supports them"
                    % context)

    def test_every_unnamed_context_is_still_unnamed(self):
        """An exemption that outlived its reason would hide the next omission."""
        docs = user_facing()
        for context, reason in NOT_NAMED.items():
            with self.subTest(context=context):
                self.assertIn(context, contexts_from_inv098(),
                              "INV-098 no longer names %s; drop it from NOT_NAMED" % context)
                self.assertTrue(reason.strip())
                self.assertFalse(names_context(docs, context),
                                 "the docs name %s now; drop it from NOT_NAMED" % context)

    def test_a_context_the_docs_stop_naming_is_reported(self):
        """Negative control: the walkthrough without its VS Code sentence names no IDE context."""
        docs = user_facing()
        self.assertTrue(names_context(docs, "Claude IDE extension"))
        self.assertFalse(names_context(docs.replace("Claude Code for VS Code", "Other editors"),
                                       "Claude IDE extension"))

    # Retired (one-repository migration, 2026-11-14):
    # `test_the_unverified_install_paths_are_disclosed_as_unverified`, which required "no verified
    # install steps for them". Neither `public/README.md` nor the Claude install fragments say it
    # or anything like it: the walkthrough names the other clients and gives no steps for them,
    # without saying those routes are unverified. The generated page's verification note (from
    # `hosts/claude/checks.json`) says how far the page's own steps were checked, not this.

    def test_it_tells_those_readers_what_to_do_instead(self):
        self.assertRegex(
            claude_pages(), r"(?i)install (?:it|the plugin) the way your client installs plugins",
            "the Claude walkthrough names the other clients without saying what those readers "
            "should do, which leaves 'pick either' unanswered by another route")


if __name__ == "__main__":
    unittest.main()
