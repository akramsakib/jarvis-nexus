from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nexus_core import RiskLevel, PermissionLevel, ToolDefinition


@dataclass(slots=True)
class ApprovalDecision:
    allowed: bool
    reason: str = ""
    requires_approval: bool = False


class PermissionEngine:
    def __init__(self, approval_mode: str = "manual") -> None:
        self.approval_mode = approval_mode

    def evaluate(self, tool: ToolDefinition, user_approves: bool = False, policy: dict[str, Any] | None = None) -> ApprovalDecision:
        policy = policy or {}
        if tool.permission == PermissionLevel.HIGH and tool.risk == RiskLevel.HIGH:
            if self.approval_mode == "manual" and not user_approves:
                return ApprovalDecision(False, "High-risk action requires explicit approval.", True)
            if policy.get("allow_high_risk", False) is False and not user_approves:
                return ApprovalDecision(False, "High-risk action rejected by policy.", True)
            return ApprovalDecision(True, "Approved by explicit policy gate.", False)
        return ApprovalDecision(True, "Permission check passed.", False)


permission_engine = PermissionEngine()
