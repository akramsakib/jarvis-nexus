from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Task:
    id: str
    title: str
    description: str
    priority: int = 1
    status: str = "PLANNED"
    dependencies: list[str] = field(default_factory=list)
    parent: str | None = None
    effort: str = "medium"
    result: str | None = None
    logs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TaskPlan:
    goal: str
    tasks: list[Task]


class TaskPlanner:
    def plan_goal(self, goal: str) -> TaskPlan:
        normalized = goal.strip()
        if not normalized:
            raise ValueError("Goal cannot be empty.")

        tasks = [
            Task(id="task-1", title="Understand objective", description=f"Clarify the goal and constraints for: {normalized}", priority=1, status="PLANNED", effort="low"),
            Task(id="task-2", title="Inspect available context", description="Review project, files, and recent state relevant to the objective.", priority=2, status="PLANNED", effort="medium", dependencies=["task-1"]),
            Task(id="task-3", title="Execute the primary work", description="Carry out the required action or implementation.", priority=3, status="PLANNED", effort="medium", dependencies=["task-2"]),
            Task(id="task-4", title="Verify and report", description="Validate the result and prepare a concise status summary.", priority=4, status="PLANNED", effort="low", dependencies=["task-3"]),
        ]
        return TaskPlan(goal=normalized, tasks=tasks)

    def update_task_status(self, tasks: list[Task], task_id: str, status: str) -> None:
        for task in tasks:
            if task.id == task_id:
                task.status = status
                task.logs.append(f"Status changed to {status}.")
                return
        raise KeyError(f"Task {task_id} not found.")


planner = TaskPlanner()
