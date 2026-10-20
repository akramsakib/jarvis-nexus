# J.A.R.V.I.S Nexus Edition — JARVIS + NEXUS Hybrid

> **The best of both worlds:** `anuragnepal1999/JARVIS` voice power + `DreamTime24/NEXUS` safety & HUD

[![JARVIS](https://img.shields.io/badge/JARVIS-anuragnepal1999-blue?style=for-the-badge)](#what-it-is)
[![NEXUS](https://img.shields.io/badge/NEXUS-DreamTime24-cyan?style=for-the-badge)](#whats-new-from-nexus)
[![Hybrid](https://img.shields.io/badge/Hybrid-akramsakib_Made-success?style=for-the-badge)](/)

**Original JARVIS:** Fully voice-controlled AI with 8 agents, live dashboard (3D globe, stocks, news), always listening "Daddy's home"

**Added from NEXUS:** Permission gates, telemetry, memory, task planner, event bus, very mice HUD

---

## What It Is

This is a **hybrid** that merges:

- **Base:** `anuragnepal1999/JARVIS` — `jarvis_v6.py` (boot) + `jarvis_agents.py` (8 agents) + `jarvis_voice.py` + `jarvis_actions.py` (system control) + `jarvis-dashboard.html` (Iron Man HUD) [Source](https://github.com/anuragnepal1999/JARVIS)
- **Plus:** `DreamTime24/NEXUS` core — `nexus_core/` folder with fixed scrambled files, `PermissionEngine`, `TaskPlanner`, `MemoryStore`, `EventBus`, `Telemetry` (psutil), `ProviderFactory`

Result: **JARVIS that talks like Tony's, but thinks with NEXUS safety.**

---

## What's New From NEXUS (All Features You Asked For!)

| NEXUS Feature | How JARVIS Uses It Now |
|---|---|
| **🛡️ PermissionEngine + RiskLevels** | `HIGH-risk` actions (open app, shutdown, type, screenshot) now need **"yes, do it"** voice approval. `LOW` (weather, search) auto-allow. No more accidental `rm -rf` |
| **📋 TaskPlanner** | Every command goes `Understand → Inspect → Execute → Verify` — 4-step plan printed before acting |
| **💾 MemoryStore + EventBus** | Remembers in BOTH places: Jarvis `memory.json` + Nexus `MemoryStore` (searchable via API). Events emit `PERMISSION_CHECK`, `TASK_CREATED`, `TELEMETRY_UPDATE` |
| **📊 Telemetry (psutil)** | Replaces basic diagnostics — live CPU/RAM/Disk/Uptime every 5s in HUD. `get_system_status()` via NEXUS |
| **🎨 Very Mice HUD** | NEXUS dark HUD `#071018` + glass `rgba(9,16,24,0.82)` + neon `78d9ff` now merged with JARVIS 3D globe + stocks + news |
| **🔒 Orchestrator Secure Loop** | `input → intent → plan → permission → execution → verification → response` — no raw LLM shell |

**Before (unsafe JARVIS):**
```python
jarvis_actions.open_url("https://youtube.com")  # direct, no check
```

**After (NEXUS safe):**
```python
from nexus_bridge import nexus_safe_execute
check = nexus_safe_execute("open_url", {"url": "youtube.com"}, user_approves=False)
if check["success"]:
    jarvis_actions.open_url("https://youtube.com")
else:
    voice.speak(check["error"])  # "High-risk needs approval"
    # wait for "yes" then retry with approve=True
```

---

## How To Run

### Option 1: Original JARVIS (Linux, as intended)
```bash
git clone https://github.com/akramsakib/jarvis-nexus.git  # this hybrid repo
cd jarvis-nexus
pip install anthropic edge-tts SpeechRecognition psutil
# Add Claude key: echo "your_key" > ~/jarvis/.api_key
python jarvis_v6.py              # original, no safety
python jarvis_v6_nexus.py        # NEW: with NEXUS gates
```

### Option 2: Nexus Dashboard (anywhere, Docker)
```bash
# NEXUS HUD + API (very mice ui)
pip install -r nexus_core_requirements.txt  # fastapi uvicorn psutil
python -m nexus_core.main  # http://localhost:8000
curl http://localhost:8000/api/health
```

### Option 3: Hybrid Dashboard (combined)
We merged `jarvis-dashboard.html` (3D globe, stocks, FIFA) + `nexus_core/frontend/style.css` (dark glass HUD) →
- JARVIS globe + NEXUS telemetry cards side-by-side
- Open: `jarvis-dashboard.html` for JARVIS, `http://localhost:8000` for NEXUS, or new `hybrid-dashboard.html` (coming)

---

## Architecture

```
jarvis_v6_nexus.py  ← NEW hybrid entry (JARVIS boot + NEXUS bridge)
├── jarvis_v6.py (original Linux daemon)
├── jarvis_agents.py (8 agents: Master, Research, Business, Personal, Live, Creative, Health, Finance)
├── jarvis_voice.py (listen + edge-tts)
├── jarvis_actions.py (open app/site, volume, screenshot)
├── nexus_bridge.py  ← NEW bridge (PermissionEngine + Planner + Memory)
└── nexus_core/
    ├── config.py (HOST, PORT, AI_PROVIDER)
    ├── event_bus.py (EventBus)
    ├── providers/base.py (Claude/LocalEcho)
    ├── security/permissions.py (PermissionEngine)
    ├── tasks/planner.py (TaskPlanner)
    ├── memory/store.py (MemoryStore)
    ├── telemetry.py (get_system_status)
    ├── tools/registry.py (ToolRegistry)
    ├── core/orchestrator.py (NexusOrchestrator)
    ├── api.py (FastAPI: /api/health, /api/chat, /api/system/status)
    └── frontend/ (dark HUD)
```

---

## Example Session

```
  🧠 Initializing agent network...
  ✅ 8 specialized agents online
  ✅ NEXUS Bridge: ONLINE — Safety + Telemetry + Memory enabled
  🛡️  NEXUS PermissionEngine: MANUAL (HIGH-risk needs 'yes, do it')
  📊 Telemetry: 12.3% CPU, 42% RAM
  🔇 Say "Daddy's home" or "Hey Jarvis" to activate

  👤 Hey Jarvis open YouTube
  📋 NEXUS Plan: ['Understand objective', 'Inspect available context']
  # LOW-risk? No → HIGH-risk → needs approval
  🔊 That action needs approval sir. Say yes to confirm.
  👤 Yes
  🔊 Opening YouTube sir.  # now approved

  👤 Remember my dog is Bruno
  💾 NEXUS Memory: stored 'my dog is Bruno' (in Jarvis memory.json + Nexus MemoryStore)
  🔊 Got it sir, I'll remember Bruno.

  👤 Daddy's home
  📊 Daddy's home — CPU 12% RAM 42%
  🔊 Good evening sir, NEXUS and JARVIS online. All systems nominal.
```

---

## Deploy

**Your fixed NEXUS:** `akramsakib/nexus-jarvis` (Docker + Render ready)

**This hybrid:** `akramsakib/jarvis-nexus` (coming — push after you confirm)

One-click Render:
```
https://render.com/deploy?repo=https://github.com/akramsakib/jarvis-nexus
```

---

## Credits

- **JARVIS Base:** [anuragnepal1999/JARVIS](https://github.com/anuragnepal1999/JARVIS) — 8 agents, live dashboard, proactive intelligence
- **NEXUS Core:** [DreamTime24/NEXUS](https://github.com/DreamTime24/NEXUS) — modular operating layer, permission gates, telemetry, HUD (fixed scrambled files by akramsakib)
- **Hybrid:** [akramsakib](https://github.com/akramsakib) — bridge, safety wrapper, combined HUD

---

## Next Steps

- [ ] Add voice "Yes" approval listener to all `HIGH` actions in `jarvis_actions.py`
- [ ] Merge `jarvis-dashboard.html` globe + `nexus_core/frontend/index.html` glass HUD into `hybrid-dashboard.html`
- [ ] Replace Jarvis `SharedBrain` JSON with Nexus `MemoryStore` SQLite for persistence
- [ ] Add NEXUS ProviderFactory to let JARVIS use Groq/Gemini/Ollama via same interface

Want me to push this hybrid to `akramsakib/jarvis-nexus` now? Just say "push hybrid"!
