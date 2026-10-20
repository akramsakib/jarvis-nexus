from __future__ import annotations

from typing import Any

from nexus_core import RiskLevel, PermissionLevel, ToolDefinition, ToolResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def execute(self, name: str, payload: dict[str, Any] | None = None, approval: bool = False) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(tool=name, success=False, error="Tool not found.")

        if tool.permission == PermissionLevel.HIGH and not approval:
            return ToolResult(tool=name, success=False, error="High-risk tool requires explicit approval.")

        if tool.executor is None:
            return ToolResult(tool=name, success=False, error="Tool executor is not defined.")

        try:
            data = tool.executor(payload or {})
            return ToolResult(tool=name, success=True, data=data)
        except Exception as exc:  # pragma: no cover - defensive layer
            return ToolResult(tool=name, success=False, error=str(exc))


registry = ToolRegistry()


def _list_directory(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload.get("path", ".")
    import os
    entries = sorted(os.listdir(base))
    return {"path": base, "entries": entries}


def _read_file(payload: dict[str, Any]) -> dict[str, Any]:
    file_path = payload.get("path")
    if not file_path:
        raise ValueError("A file path is required.")
    with open(file_path, "r", encoding="utf-8") as handle:
        return {"path": file_path, "content": handle.read()}


def _write_file(payload: dict[str, Any]) -> dict[str, Any]:
    file_path = payload.get("path")
    content = payload.get("content", "")
    if not file_path:
        raise ValueError("A file path is required.")
    with open(file_path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return {"path": file_path, "written": True}


registry.register(ToolDefinition(
    name="list_directory",
    description="List directory entries for a specific path.",
    permission=PermissionLevel.LOW,
    risk=RiskLevel.LOW,
    executor=_list_directory,
))
registry.register(ToolDefinition(
    name="read_file",
    description="Read a text file from disk.",
    permission=PermissionLevel.LOW,
    risk=RiskLevel.LOW,
    executor=_read_file,
))
registry.register(ToolDefinition(
    name="write_file",
    description="Write or update a text file.",
    permission=PermissionLevel.MEDIUM,
    risk=RiskLevel.MEDIUM,
    executor=_write_file,
))
