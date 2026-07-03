"""Spoke-local pytest bootstrap.

Makes the spoke's src/ and the in-repo kernel src/ importable so the suite
runs from a plain checkout without `pip install -e`. When the spoke is
lifted out into its own repository, the kernel fallback simply finds
nothing and the installed axm-genesis package is used instead.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SPOKE_SRC = Path(__file__).resolve().parents[1] / "src"
_KERNEL_SRC = Path(__file__).resolve().parents[3] / "src"

if str(_SPOKE_SRC) not in sys.path:
    sys.path.insert(0, str(_SPOKE_SRC))
# Adopt a working-tree kernel only if it really is one (in-kernel-repo layout).
if (_KERNEL_SRC / "axm_verify").is_dir() and str(_KERNEL_SRC) not in sys.path:
    sys.path.insert(0, str(_KERNEL_SRC))
