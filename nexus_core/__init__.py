from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PermissionLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    permission: PermissionLevel
    risk: RiskLevel
    input_schema: dict[str, Any] = field(default_factory=dict)
    executor: Any | None = None


@dataclass(slots=True)
class ToolResult:
    tool: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class EventRecord:
    type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
