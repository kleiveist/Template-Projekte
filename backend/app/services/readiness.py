from __future__ import annotations

from collections.abc import Callable

DatabaseProbe = Callable[[], bool]


def readiness_status(
    *,
    database_enabled: bool,
    database_configured: bool,
    database_probe: DatabaseProbe,
) -> str:
    """Return a public readiness state without exposing infrastructure details."""
    if not database_enabled:
        return "ready"
    if not database_configured or not database_probe():
        return "unavailable"
    return "ready"
