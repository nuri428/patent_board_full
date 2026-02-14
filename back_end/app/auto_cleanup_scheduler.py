from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_MODULE_PATH = Path(__file__).with_name("scheduler") / "auto_cleanup_scheduler.py"
_SPEC = spec_from_file_location("app._auto_cleanup_scheduler_impl", _MODULE_PATH)

if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load auto cleanup scheduler module from {_MODULE_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

AutoCleanupScheduler = _MODULE.AutoCleanupScheduler
CleanupCycleStats = _MODULE.CleanupCycleStats
auto_cleanup_scheduler = _MODULE.auto_cleanup_scheduler
get_scheduler = _MODULE.get_scheduler
