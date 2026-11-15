"""A freshly built package for tests that need what one assistant actually installs.

Most tests read ``source/`` directly, and a test that passes there holds on every assistant,
because text outside a host marker is copied unchanged into every package. A test that needs a
value only one host has (its plugin-root variable, its manifest, its hook configuration) asks
for that host's package here:

    from _built import built
    PLUGIN = built("claude")

Each host is built once per test process, into a scratch directory that is removed at exit, so
a test never reads a stale ``dist/``.
"""

import atexit
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.bootcamp_build.emit import build_host  # noqa: E402
from tools.bootcamp_build.model import SOURCE_DIR, host_ids, load_declaration, load_host  # noqa: E402

_scratch = None
_packages = {}


def dist_root() -> Path:
    """The scratch directory laid out like the published repository."""
    global _scratch
    if _scratch is None:
        _scratch = Path(tempfile.mkdtemp(prefix="bootcamp-built-"))
        atexit.register(shutil.rmtree, _scratch, ignore_errors=True)
    return _scratch


def built(host_id: str = "claude") -> Path:
    """The root of ``host_id``'s package, built from the current source."""
    if host_id not in _packages:
        build = build_host(
            load_declaration(SOURCE_DIR), load_host(host_id), SOURCE_DIR, dist_root(), set(host_ids())
        )
        _packages[host_id] = build.root
    return _packages[host_id]
