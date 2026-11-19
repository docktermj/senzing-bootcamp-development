"""`szBuildVersion.json`'s location is attributed per platform, never by one blanket caveat.

MCP-NEGATIVE-SCAN: ignore-file — this file quotes the `MCP-NEGATIVE:` token as a LOCATOR, to
find the real marker in module-02's SKILL.md and assert its `owner:` clause. Those string
literals are matchers, not dated claims, so the scanner would otherwise report them as
malformed markers. The absence claims in the docstring below are the same ones that marker
already carries, and it is the marker — not this test — that sits on the re-ask worklist.

Module 2 gives the fallback route for reading the SDK build version and then labels its own
provenance. The label was a single ⚠️ spanning all three platforms — *"environment
observations, not MCP-sourced facts"* — written 2026-08-13 against server 1.32.9, when no MCP
route carried any `szBuildVersion.json` location. It was accurate then.

The server has since gained the **Windows** path: `sdk_guide(topic='install',
platform='windows')` names `szBuildVersion.json` among the support data under
`<scoop-app-dir>\\data` (verified server 1.35.3, 2026-09-01). Because the caveat was phrased
per-paragraph rather than per-platform, there was no way for it to become half-true — it
simply became wrong for one platform while reading as though it had been reviewed.

⚠️ Why this matters more than a stale note usually would: INV-080 routes every Senzing fact
through the MCP server, and this ⚠️ is what tells a reader which side of that line a statement
sits on. Mislabeling a served fact as a local observation degrades both ways — a guide hitting
a mismatch has no reason to re-ask the server, and a reader who trusts the ⚠️ discounts a path
the server would confirm. This paragraph is the fallback reached *after* the SDK route fails,
so it is consulted exactly when the Bootcamper is already stuck.

Verified 2026-09-01, server 1.35.3, all three routes asked:
    windows    -> names szBuildVersion.json in gotchas[]            (MCP-sourced)
    linux_apt  -> names it nowhere; observed on-box at 4.4.0.26242  (observation)
    macos_arm  -> names it nowhere; support data listed without it  (unknown)

#79 re-asked `search_docs(query='szBuildVersion.json build version file location')` on server
1.46.1 (docs index 2026-11-14 17:44 UTC), 2026-11-19. The corpus now names
`/opt/senzing/er/szBuildVersion.json`, but only in a `senzing-garage` performance-test runbook,
for the 4.x container images. So the Linux bullet no longer says "No MCP route states it": it
keeps the install observation as its source and cites the runbook as corroboration scoped to
those images, and the negative marker is narrowed to macOS. The three routes above were asked
again on the same day and still answer as recorded.

Enforces **INV-285** — a provenance label covering several independently-moving facts is
stated per fact, each with its own route and date.

⚠️ What this asserts is that the per-platform attribution **ships**, not that a live turn
obeys it. An ``Enforced by`` clause naming this file is a claim about the text, and the
guide's behavior at that step is `dry-run` phase 3's to observe.

Stdlib only; nothing under ``source/`` is imported (INV-108).
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = (REPO / "source" / "skills" /
         "module-02-sdk-setup" / "SKILL.md")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


#: The MCP-NEGATIVE marker grammar is imported, never restated, so the marker below parses here
#: exactly as the negatives report parses it.
reports = _load(REPO / ".claude" / "skills" / "dry-run" / "coverage_reports.py",
                "coverage_reports_for_build_version_provenance")


def provenance_block():
    """From the build-metadata sentence to the end of the per-platform list."""
    text = SKILL.read_text(encoding="utf-8")
    start = text.find("in `szBuildVersion.json`")
    assert start != -1, "the build-metadata paragraph was not found -- reworded?"
    end = text.find("<!-- MCP-NEGATIVE:", start)
    assert end != -1, "the MCP-NEGATIVE marker that follows the paragraph was not found"
    return text[start:end]


def flat(s):
    return re.sub(r"\s+", " ", s)


class ProvenanceIsStatedPerPlatform(unittest.TestCase):
    def setUp(self):
        self.block = flat(provenance_block())

    def test_the_three_platforms_are_attributed_separately(self):
        """The spec's fifth criterion, and the whole point: one blanket caveat cannot age well."""
        for platform in ("Windows", "Linux", "macOS"):
            with self.subTest(platform=platform):
                self.assertRegex(
                    self.block, r"\*\*%s —" % platform,
                    "Each platform must carry its own provenance. A single caveat spanning all "
                    "three has no way to become half-true: when the server gained the Windows "
                    "path, the note became wrong for one platform while still reading as "
                    "reviewed.",
                )

    def test_windows_is_attributed_to_the_mcp_route_that_serves_it(self):
        self.assertRegex(
            self.block,
            r"(?i)Windows — MCP-sourced",
            "Windows must no longer sit under 'environment observations'. The server states "
            "the path outright, and mislabeling a served fact as a local observation removes "
            "the reader's reason to re-ask the authority.",
        )
        self.assertRegex(
            self.block, r"sdk_guide\(topic='install', platform='windows'\)",
            "The Windows attribution must name the route that serves it, so a reader can "
            "re-ask it rather than trusting this file.",
        )

    def test_linux_stays_an_observation_and_says_so(self):
        self.assertRegex(
            self.block, r"(?i)Linux — environment observation, not MCP-sourced",
            "Linux is still an observation and must stay labeled as one (INV-149): the only "
            "route that names the path is a senzing-garage runbook about container images, "
            "which corroborates the install observation and does not replace it (#79). "
            "Promoting it on the strength of that runbook, or of the Windows change, would be "
            "the same defect in the other direction.",
        )
        self.assertRegex(
            self.block, r"4\.4\.0\.\d+",
            "The Linux observation must name the build it was observed against; the previous "
            "note said only 'Linux observed 2026-08-13' with no version.",
        )

    def test_macos_stays_unknown_and_names_the_route_that_was_asked(self):
        self.assertRegex(
            self.block, r"(?i)macOS — unknown",
            "macOS must stay unknown — the route was asked and does not carry it.",
        )
        self.assertRegex(
            self.block, r"sdk_guide\(topic='install', platform='macos_arm'\)",
            "The macOS entry must name the route that was asked and came back without it, so "
            "the next reader does not re-ask the same question blind (INV-194).",
        )

    def test_every_platform_claim_carries_a_date(self):
        dates = re.findall(r"20\d\d-\d\d-\d\d", self.block)
        self.assertGreaterEqual(
            len(dates), 3,
            "Each platform's provenance must carry its own date. A shared date is how the "
            "Windows half stayed stamped with a review it never had. Found: %r" % (dates,),
        )

    def test_the_server_version_is_named(self):
        self.assertRegex(
            self.block, r"1\.35\.\d",
            "The MCP-sourced claims must name the server version they were verified against "
            "(INV-080).",
        )


def linux_bullet():
    block = flat(provenance_block())
    start = block.index("**Linux —")
    return block[start:block.index("**macOS —", start)]


class TheLinuxBulletCitesTheRunbookAsCorroboration(unittest.TestCase):
    """#79: the corpus now names the Linux path, in one place and for one case.

    `search_docs(query='szBuildVersion.json build version file location')` names
    `/opt/senzing/er/szBuildVersion.json` in a `senzing-garage` performance-test runbook, for the
    4.x container images (server 1.46.1, 2026-11-19). The bullet keeps the 2026-09-01 install
    observation as its source and cites that hit as corroboration scoped to those images.
    """

    def setUp(self):
        self.bullet = linux_bullet()

    def test_the_install_observation_stays_the_primary_source(self):
        self.assertRegex(self.bullet, r"BUILD_VERSION 4\.4\.0\.26242`? \(2026-09-01\)",
                         "the 2026-09-01 observation keeps its build and its date (INV-191)")
        self.assertRegex(self.bullet, r"(?i)install observation is the source")

    def test_the_search_docs_hit_is_cited_as_corroboration_scoped_to_container_images(self):
        self.assertIn(
            "search_docs(query='szBuildVersion.json build version file location')", self.bullet,
            "the bullet must name the call that names the path, so the next reader can re-ask it",
        )
        self.assertRegex(self.bullet, r"(?i)corroborat")
        self.assertRegex(self.bullet, r"senzing-garage`? performance-test runbook")
        self.assertRegex(self.bullet, r"(?i)4\.x container images")
        self.assertRegex(
            self.bullet,
            r"server \*{0,2}\d+\.\d+\.\d+\*{0,2}, docs index \d{4}-\d\d-\d\d \d\d:\d\d UTC, "
            r"\d{4}-\d\d-\d\d",
            "the corroboration must carry the server version, docs index and date it was asked "
            "on (INV-080)",
        )

    def test_the_linux_apt_install_sentence_is_kept(self):
        self.assertRegex(
            self.bullet,
            r"`sdk_guide\(topic='install', platform='linux_apt'\)` gives `default_paths` and a "
            r"`ls /opt/senzing/er/lib/libSz\.so` verification step and never mentions the file",
        )

    def test_the_retired_no_route_claim_is_gone(self):
        """Negative control: on server 1.46.1 a route does name the path."""
        self.assertNotRegex(
            self.bullet, r"(?i)no MCP route (states|names|gives|serves) (it|the path)",
            "the bullet again says no MCP route states the Linux path; search_docs names it, "
            "in a runbook about the 4.x container images",
        )


class TheNegativeMarkerIsScopedToWhatTheServerStillLacks(unittest.TestCase):
    """The marker keeps the macOS absence and records the Linux runbook hit (#79)."""

    def setUp(self):
        text = SKILL.read_text(encoding="utf-8")
        i = text.index("<!-- MCP-NEGATIVE: search_docs(query='szBuildVersion.json")
        self.raw = text[i: text.index("-->", i) + 3]
        self.marker = flat(self.raw)
        self.parsed = reports.MCP_NEGATIVE.search(self.raw)

    def test_the_marker_still_parses(self):
        self.assertIsNotNone(
            self.parsed,
            "the marker no longer parses as an MCP-NEGATIVE marker, so it drops off the "
            "negatives worklist",
        )

    def test_the_claim_is_the_macos_absence(self):
        claim = flat(self.parsed.group("claim"))
        self.assertRegex(claim, r"(?i)no indexed document gives the file's path for macOS")

    def test_the_claim_records_the_linux_runbook_hit(self):
        claim = flat(self.parsed.group("claim"))
        self.assertRegex(claim, r"(?i)for Linux the corpus names \S*szBuildVersion\.json only in "
                                r"a senzing-garage performance-test runbook")
        self.assertRegex(claim, r"(?i)4\.x container images")

    def test_the_retired_any_platform_claim_is_gone(self):
        """Negative control: the claim #79 found false on server 1.46.1."""
        self.assertNotRegex(
            self.marker, r"(?i)on any platform",
            "the marker again says no indexed document gives the path on any platform; the "
            "corpus names the Linux path for the 4.x container images",
        )

    def test_the_marker_is_dated_no_earlier_than_the_re_ask(self):
        version = tuple(int(n) for n in self.parsed.group("version").split("."))
        self.assertGreaterEqual(
            version, (1, 46, 1),
            "the marker is dated before the server #79 re-asked it on, so the negatives report "
            "lists it as DUE again",
        )
        self.assertGreaterEqual(self.parsed.group("date"), "2026-11-19")

    def test_the_owner_clause_records_the_route_that_does_serve_windows(self):
        self.assertRegex(
            self.marker, r"(?i)the Windows path IS served",
            "The owner clause must record that Windows is served elsewhere. Left as-is it is "
            "not wrong but INCOMPLETE, and an incomplete owner clause sends the next re-check "
            "to conclude the fact is unavailable on every platform.",
        )
        self.assertRegex(
            self.marker, r"platform='windows'",
            "The owner clause must name the serving route, not merely allude to it.",
        )

    def test_the_owner_clause_names_the_macos_install_route(self):
        """INV-213: an absence claim names the route that would carry the fact."""
        self.assertIn("sdk_guide(topic='install', platform='macos_arm')",
                      flat(self.parsed.group("owner")))


if __name__ == "__main__":
    unittest.main()
