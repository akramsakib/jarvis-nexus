from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from nexus_core.event_bus import bus
from nexus_core.providers.base import ProviderFactory
from nexus_core.tasks.planner import TaskPlanner
from nexus_core.tools.registry import registry


class TaskState(str, Enum):
    RECEIVED = "RECEIVED"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class OrchestratorContext:
    state: TaskState = TaskState.RECEIVED
    messages: list[str] = field(default_factory=list)
    task_plan: dict[str, Any] | None = None


class NexusOrchestrator:
    def __init__(self, provider_name: str = "local", model: str | None = None) -> None:
        self.provider = ProviderFactory.get(provider_name, model)
        self.task_planner = TaskPlanner()
        self.context = OrchestratorContext()

    def handle_user_input(self, user_input: str) -> dict[str, Any]:
        self.context.state = TaskState.UNDERSTANDING
        self.context.messages.append(user_input)
        bus.emit("AI_MESSAGE_STARTED", {"message": user_input})

        plan = self.task_planner.plan_goal(user_input)
        self.context.task_plan = {"goal": plan.goal, "tasks": [asdict(task) for task in plan.tasks]}
        self.context.state = TaskState.PLANNING
        bus.emit("TASK_CREATED", {"goal": user_input})

        provider_response = self.provider.generate(user_input, system_prompt="You are NEXUS, a calm personal AI system.")
        summary = provider_response.text

        if "write" in user_input.lower() or "create" in user_input.lower():
            self.context.state = TaskState.EXECUTING
            registry.execute("write_file", {"path": "workspace/nexus_note.txt", "content": user_input})
            bus.emit("TOOL_COMPLETED", {"tool": "write_file"})

        self.context.state = TaskState.COMPLETED
        bus.emit("AI_MESSAGE_STREAM", {"message": summary})
        return {"status": "ok", "summary": summary, "plan": self.context.task_plan}
