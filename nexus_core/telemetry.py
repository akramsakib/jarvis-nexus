from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import psutil


def get_system_status() -> dict[str, Any]:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot = psutil.boot_time()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=None),
        "ram_percent": mem.percent,
        "ram_used_mb": round(mem.used / (1024 * 1024), 2),
        "disk_percent": disk.percent,
        "uptime_seconds": round((datetime.now(timezone.utc).timestamp() - boot), 2),
        "active_processes": len(psutil.pids()),
        "battery_state": "Unavailable" if not hasattr(psutil, "sensors_battery") or psutil.sensors_battery() is None else psutil.sensors_battery().percent,
    }
