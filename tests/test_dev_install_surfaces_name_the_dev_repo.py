"""The dev repository's install surfaces name the dev repository, never the public one (#522).

⚠️ **Dated note, 2026-11-14 (one-repository migration): this module is retired.** Nobody installs
from the development repository any more. It has no marketplace of its own (the old
`senzing-bootcamp-dev`), `propagate.sh` and its slug rewrite are gone, the root `README.md` is the
developer readme, and every install page is generated for the public repository,
`Senzing/bootcamp`. The eight cases that read a surface are retired, and are listed where they
stood. What still runs is the constants' agreement with this docstring and one check that the
retirement is still earned: this repository holds no marketplace catalog of its own. The file
stays because INV-360 still names it as its enforcer and
`tests/test_registered_amendments_are_not_called_pending.py` quotes this docstring. Everything
below this note is the module's description as it was, kept as the record.

This repository has four install surfaces: the root `README.md` (the Claude Desktop route and
the example recap PDF link), `docs/README.md` (the Claude Code CLI route), `docs/index.html`
(the GitHub Pages quick-start site) and the "Installing the development plugin" section of
`docs/development.md` (#610). In this tree each MUST name the development repository,
`docktermj/senzing-bootcamp-claude-plugin-development`; `propagate.sh` rewrites that slug to the
public one, `Senzing/senzing-bootcamp-claude-plugin`, on the way out.

**Why this module exists.** Commit 6e973b15 (#451) brought the public README's new Desktop
steps across and kept their public slug, so dev's Desktop route installed the published plugin
rather than the one under development. Only `docs/index.html` was checked
(`tests/test_propagate_publishes_the_pages_site.py`), and INV-348 compares that page's
`claude plugin …` commands with `docs/README.md`, not its Desktop route.

What it asserts, for each surface: the dev slug is present, the public slug is absent, and a
failure names the file. For `README.md` it also asserts the dev slug at the two sites #522
restored, the Desktop marketplace URL and the raw-content recap PDF link. `docs/development.md`
is read only from its "Installing the development plugin" heading to the next `## ` heading
(`SECTIONS`), with the lines above it kept as empty lines so a failure names the file's own
line; the rest of that page may discuss the public repository. Matching is on bytes:
the public slug is not a substring of the dev slug, so the two checks never overlap. Negative
controls put the public slug back at each README site and drop the dev slug from a surface,
and show each fails naming the file.

⚠️ **What a green run does not establish.** It reads the dev tree only. The published tree
carries the public slug at the same sites, and `tests/test_propagate_publishes_the_pages_site.py`
(INV-350) checks that no published file holds the dev slug. The surfaces are stated rather than
derived: an install surface added later is not checked until it is added to `SURFACES`.
Owner names are matched in the case written here; a differently cased public slug is not caught.

Source issue: #522. This module enforces INV-360 (registered 2026-10-13). It asserts that the
surfaces *state* the dev slug; it does not establish that a surface added later is read, for
the reason above. The fourth surface, `docs/development.md`, was added by #610 and is binding:
INV-360's base text names three, and its registered 2026-10-15 note (#610) widens it to four.
`SURFACES` below lists all four, which is the count this docstring and INV-360 both state.

Stdlib only (INV-108); four files read as bytes, no network.

Run:  python3 -m unittest discover -s tests
"""
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEV_SLUG = b"docktermj/senzing-bootcamp-claude-plugin-development"
PUBLIC_SLUG = b"Senzing/senzing-bootcamp-claude-plugin"

#: The install surfaces, stated rather than derived: the set is the subject. Since the
#: retirement no case reads them; the tuple is the record the docstring's count is held to.
SURFACES = ("README.md", "docs/README.md", "docs/index.html", "docs/development.md")


class TheSlugsAreDistinct(unittest.TestCase):
    """The precondition the byte matching relies on."""

    def test_the_public_slug_is_not_inside_the_dev_slug(self):
        self.assertNotIn(PUBLIC_SLUG, DEV_SLUG)
        self.assertNotIn(DEV_SLUG, PUBLIC_SLUG)


# Retired (one-repository migration, 2026-11-14): `EveryInstallSurfaceNamesTheDevRepo`
# (`test_every_surface_exists`, `test_every_surface_names_the_dev_repo_and_not_the_public_one`,
# `test_the_restored_readme_sites_name_the_dev_repo`) and `TheCheckCatchesThePublicSlug`
# (`test_each_readme_site_put_back_to_the_public_slug_fails_naming_the_file`,
# `test_a_surface_without_the_dev_slug_fails_naming_the_file`,
# `test_the_public_slug_in_the_development_install_section_fails_naming_the_file`,
# `test_the_public_slug_outside_the_development_install_section_is_not_read`,
# `test_the_public_slug_on_the_page_fails_naming_the_page`), with the helpers only they used
# (`SECTIONS`, `README_SITES`, `section`, `_read`, `surface_problems`, `readme_site_problems`).
# Their one subject was installing from the development repository, which no longer exists: the
# root `README.md` is the developer readme, `docs/README.md` and `docs/index.html` (carry-overs of
# the old Claude pages) were deleted on 2026-11-15, and no script rewrites a development slug on
# the way out.


class TheRetirementIsStillEarned(unittest.TestCase):
    """A retirement that outlived its reason would hide the rule it retired."""

    def test_this_repository_has_no_marketplace_of_its_own(self):
        catalog = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        self.assertFalse(
            catalog.exists(),
            "%s exists, so the development repository can be installed from again: restore the "
            "retired cases of this module (INV-360) for the surfaces that install from it"
            % catalog.relative_to(REPO_ROOT))


class TheDocstringAgreesWithTheSurfacesConstant(unittest.TestCase):
    """⛔ The prose and the constant are one claim, and they drifted apart once (#691).

    Until #691 this docstring opened "four install surfaces" and then described the fourth as
    an amendment the maintainer had yet to rule on, while `SURFACES` already listed four and
    INV-360's 2026-10-15 note (#610) had made it binding. The constant was right. These checks
    keep the count and the paths in one place, so a fifth surface cannot be added to `SURFACES`
    while the prose keeps saying four.
    """

    #: The count words this docstring may use, by the number they spell.
    SPELLED = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}

    def test_every_surface_is_named_in_the_docstring(self):
        for rel in SURFACES:
            with self.subTest(surface=rel):
                self.assertIn(rel, __doc__,
                              "%s is in SURFACES but the docstring does not name it" % rel)

    def test_the_docstring_states_the_number_of_surfaces_it_has(self):
        spelled = self.SPELLED[len(SURFACES)]
        self.assertIn("%s install surfaces" % spelled, __doc__,
                      "SURFACES lists %d entries; the docstring must say \"%s install "
                      "surfaces\"" % (len(SURFACES), spelled))
        for count, word in self.SPELLED.items():
            if count != len(SURFACES):
                with self.subTest(stale=word):
                    self.assertNotIn("%s install surfaces" % word, __doc__)


if __name__ == "__main__":
    unittest.main()
