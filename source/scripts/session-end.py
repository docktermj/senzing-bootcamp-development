#!/usr/bin/env python3
"""SessionEnd hook: to preserve your in-progress recap when the session ends.

When a bootcamp is active, fold the in-progress module recap checkpoint into
docs/bootcamp_recap.md so quitting mid-module never loses that module's narrative
(deterministic, idempotent, append-only — see recap_checkpoint.py), and stop any
container the bootcamp started so it does not linger after exit, using the runtime
CLI recorded with it (``<runtime> stop``, never remove, so it can be restarted on
resume — see docker_lifecycle.py, INV-101). Silent and non-blocking: it emits no
output, and every container step is optional and warns-and-continues when that
runtime's CLI is absent or errors.

Once graduation has ended the bootcamp (``bootcamp_complete: true`` in the progress file
or in the preferences, ``module_start_apparatus.bootcamp_complete()``) only the fold is
skipped: graduation folds and clears the checkpoint itself. The containers are still
stopped, because graduation records completion before its own session ends, and a stop
gated on completion would leave that session's containers running.

Cross-platform: invoked as a ``type: command`` hook whose ``command`` names the
interpreter and this script, quoted (``python3 "<path>"``), per INV-052. Python is already a hard bootcamp dependency.
"""
import sys

import docker_lifecycle
import module_start_apparatus
import recap_checkpoint

if recap_checkpoint.bootcamp_active():
    # Only the fold stands down on a finished bootcamp; the stop stays under this gate.
    if not module_start_apparatus.bootcamp_complete():
        recap_checkpoint.fold_checkpoint()
    docker_lifecycle.stop_started_containers()

sys.exit(0)
