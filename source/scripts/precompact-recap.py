#!/usr/bin/env python3
"""PreCompact hook: to preserve your in-progress recap before the conversation is compacted.

Compaction summarizes the conversation, which can drop an in-progress module's recap
narrative even though the session continues. When a bootcamp is active this hook:
  1. folds the current in-progress recap checkpoint into docs/bootcamp_recap.md
     (deterministic, idempotent, append-only — see recap_checkpoint.py), and
  2. emits a short reminder so the post-compaction guide keeps
     docs/progress/recap_checkpoint.md current at each step.

Non-blocking. Cross-platform: invoked as a ``type: command`` hook whose ``command`` names the
interpreter and this script, quoted (``python3 "<path>"``), per INV-052. The reminder is
written to stdout as UTF-8 bytes, whatever encoding the console gives Python (#25).
"""
import sys

import recap_checkpoint

if recap_checkpoint.bootcamp_active():
    recap_checkpoint.fold_checkpoint()
    recap_checkpoint.write_utf8(
        sys.stdout,
        "A Senzing bootcamp is in progress. Keep the current module's in-progress "
        "recap saved to docs/progress/recap_checkpoint.md (append-only, refreshed at "
        "each step boundary) so no progress narrative is lost when context is summarized.\n"
    )

sys.exit(0)
