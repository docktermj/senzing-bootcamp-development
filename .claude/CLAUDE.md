# Working in this repository

Maintainer context for Claude Code sessions in this repository. The auto mode classifier
reads this file too. Auto mode does not read `autoMode` from project settings, so the
context lives here, and the actions that must always prompt are `permissions.ask` rules
in `.claude/settings.json`.

## One source, every assistant

The bootcamp is written once, in `source/`, and built into a package for each AI assistant
(Claude, GitHub Copilot, Kiro, ChatGPT, Gemini). `README.md` explains the layout.

- **Change the bootcamp in `source/`, never in `dist/`.** `dist/` is generated and ignored.
- **A change must work on every assistant.** Text in `source/` names no assistant. Where
  assistants differ, use a `{{host.name}}` value, a `<!-- host:only … -->` block or a
  `<!-- host:include … -->` fragment, and give every assistant its value.
- **Run these before saying a change is done:**
  `python3 -m tools.bootcamp_build check` and `python3 -m unittest discover -s tests`.
- **A test that reads `source/` holds for every assistant.** Use `built("claude")` from
  `tests/_built.py` only for what is true of the Claude rendering alone.
- **Say what was actually run on a real assistant.** `hosts/<assistant>/checks.json` records
  each real run. Never record one that did not happen.

## Outward-facing actions

- **This repository is public.** Any push to it is publishing. Only this repository's own
  work belongs in it. Secrets, credentials and bootcamper personal data never belong in
  it, whatever its visibility.
- **Raw bootcamper feedback stays out of git.** A feedback file carries a bootcamper's own
  text. `.gitignore` covers it; never force-add one, and commit only `feedback/PROCESSED.jsonl`.
- **The public repository is `Senzing/bootcamp`.** Promotion writes its working tree and
  never commits or pushes. Its `main` needs a signed commit and a code-owner review.
- **Filing a GitHub issue here is outward-facing.** The repository's skills create an
  issue only after an explicit yes from the maintainer for that issue.
- **Sending feedback upstream is irreversible.** The Senzing MCP server's
  `submit_feedback` tool sends each message to Senzing. It needs the maintainer's
  explicit yes for each message, and the maintainer tooling never calls it on its own.

## Trusted services

- `mcp.senzing.com` is the Senzing MCP server, the plugin's hard runtime dependency.
  Calling its read-only tools for documentation, references and examples is routine.

## Files that handle credentials

These files define secret detection or credential hardening. Never put a real secret,
credential or personal record in them, including as a test fixture:

- `source/scripts/secret_patterns.py`
- `tests/test_screenshot_retention_and_order.py`
- `tests/test_secret_patterns_are_shared.py`
