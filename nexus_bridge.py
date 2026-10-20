"""
NEXUS Bridge for JARVIS — Adds ALL NEXUS safety/features to JARVIS
Hybrid of anuragnepal1999/JARVIS + DreamTime24/NEXUS (fixed by akramsakib)

Features ported from NEXUS:
- PermissionEngine + RiskLevels (LOW/MEDIUM/HIGH)
- TaskPlanner (Understand → Inspect → Execute → Verify)
- MemoryStore + EventBus
- Telemetry (psutil CPU/RAM/Disk/Uptime)
- Orchestrator secure loop: input → intent → plan → permission → execution → verification
"""
import sys
sys.path.insert(0, "./nexus_core")

from nexus_core import RiskLevel, PermissionLevel, ToolDefinition
from nexus_core.security.permissions import PermissionEngine
from nexus_core.tasks.planner import TaskPlanner
from nexus_core.memory.store import MemoryStore
from nexus_core.event_bus import bus
from nexus_core.telemetry import get_system_status
from nexus_core.providers.base import ProviderFactory
from nexus_core.tools.registry import ToolRegistry
from nexus_core import ToolResult

# --- Initialize NEXUS core ---
permission_engine = PermissionEngine(approval_mode="manual")
task_planner = TaskPlanner()
memory_store = MemoryStore()
provider = ProviderFactory.get("local", "local-echo")
registry = ToolRegistry()

# Register NEXUS telemetry as a safe tool for JARVIS to use
telemetry_tool = ToolDefinition(
    name="get_system_status",
    description="Get real CPU/RAM/Disk/Uptime via psutil",
    permission=PermissionLevel.LOW,
    risk=RiskLevel.LOW,
    executor=lambda payload: get_system_status()
)
registry.register(telemetry_tool)

# Wrap HIGH-RISK JARVIS actions with NEXUS approval gate
HIGH_RISK_JARVIS_ACTIONS = [
    "open_url", "open_app", "execute_command", "type_text",
    "control_volume", "take_screenshot", "delete_file", "shutdown"
]

def nexus_safe_execute(tool_name: str, payload: dict, user_approves: bool = False):
    """
    All JARVIS actions now go through NEXUS PermissionEngine.
    LOW/MEDIUM → auto-allow
    HIGH → requires explicit user approval (voice: "yes, do it" or HUD approve button)
    """
    tool = registry.get(tool_name)
    if tool is None:
        # Create ad-hoc definition for JARVIS tool
        risk = RiskLevel.HIGH if tool_name in HIGH_RISK_JARVIS_ACTIONS else RiskLevel.MEDIUM
        perm = PermissionLevel.HIGH if risk == RiskLevel.HIGH else PermissionLevel.MEDIUM
        tool = ToolDefinition(name=tool_name, description=f"JARVIS action: {tool_name}", permission=perm, risk=risk)

    decision = permission_engine.evaluate(tool, user_approves=user_approves)
    bus.emit("PERMISSION_CHECK", {"tool": tool_name, "allowed": decision.allowed, "reason": decision.reason})

    if not decision.allowed:
        return {"success": False, "error": decision.reason, "requires_approval": decision.requires_approval}

    # If allowed, JARVIS original function will be called by caller
    bus.emit("TOOL_APPROVED", {"tool": tool_name})
    return {"success": True, "approved": True, "tool": tool_name}

def plan_with_nexus(user_input: str):
    """Use NEXUS TaskPlanner to break Jarvis request into 4 steps"""
    plan = task_planner.plan_goal(user_input)
    bus.emit("TASK_CREATED", {"goal": user_input, "tasks": len(plan.tasks)})
    return plan

def remember_with_nexus(category: str, content: str):
    """Bridge: store in BOTH Jarvis SharedBrain AND Nexus MemoryStore"""
    # Nexus side
    item = memory_store.store_memory(category=category, content=content)
    bus.emit("MEMORY_STORED", {"category": category, "id": item.id})
    # Jarvis side will be called separately via jarvis_agents SharedBrain
    return item

def get_nexus_telemetry():
    """Get live telemetry for JARVIS HUD — replaces/enhances jarvis-dashboard system diagnostics"""
    status = get_system_status()
    bus.emit("TELEMETRY_UPDATE", status)
    return status

# Example: How to wrap existing JARVIS jarvis_actions.py functions:
"""
BEFORE (unsafe, direct):
  jarvis_actions.open_url("https://youtube.com")

AFTER (NEXUS safe):
  from nexus_bridge import nexus_safe_execute
  check = nexus_safe_execute("open_url", {"url": "https://youtube.com"}, user_approves=False)
  if check["success"]:
      jarvis_actions.open_url("https://youtube.com")
  else:
      voice.speak(check["error"])  # "High-risk action requires explicit approval."
"""

if __name__ == "__main__":
    print("✅ NEXUS Bridge loaded")
    print(f"  PermissionEngine: {permission_engine.approval_mode}")
    print(f"  Telemetry: {get_nexus_telemetry()}")
    print(f"  Registry tools: {[t.name for t in registry.list()]}")
    plan = plan_with_nexus("open YouTube and search Ronaldo")
    print(f"  Plan for 'open YouTube': {[t.title for t in plan.tasks]}")
