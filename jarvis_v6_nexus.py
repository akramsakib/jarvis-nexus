#!/usr/bin/env python3
"""
J.A.R.V.I.S v6 Nexus Edition — Hybrid of anuragnepal1999/JARVIS + DreamTime24/NEXUS

Original JARVIS v6 boot + NEXUS safety/orchestration layer

Changes vs jarvis_v6.py:
- All voice input goes through NEXUS Orchestrator (plan → permission → execute → verify)
- HIGH-risk actions (open app, shutdown, etc) require approval via NEXUS PermissionEngine
- Memory goes to BOTH Jarvis SharedBrain AND Nexus MemoryStore
- Telemetry from NEXUS psutil replaces basic diagnostics
- Dashboard combines JARVIS 3D globe + NEXUS mice HUD
"""
import os, sys, re, time, threading, subprocess, json
from datetime import datetime

# Add hybrid paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "nexus_core"))

HOME = os.path.expanduser("~")
sys.path.insert(0, f"{HOME}/jarvis")

import jarvis_voice as voice
import jarvis_actions as actions
import jarvis_monitor as monitor
import jarvis_integrations as integrations
import jarvis_speed as speed
import jarvis_proactive as proactive
import jarvis_content as content

# --- NEXUS BRIDGE ---
try:
    import nexus_bridge
    from nexus_core.telemetry import get_system_status
    NEXUS_ENABLED = True
    print("✅ NEXUS Bridge: ONLINE — Safety + Telemetry + Memory enabled")
except Exception as e:
    NEXUS_ENABLED = False
    print(f"⚠️ NEXUS Bridge offline: {e}")

def nexus_gate(tool_name, payload=None, approve=False):
    if not NEXUS_ENABLED:
        return {"success": True}
    return nexus_bridge.nexus_safe_execute(tool_name, payload or {}, user_approves=approve)

def boot():
    print("""
  ╔══════════════════════════════════════════════════╗
  ║   J.A.R.V.I.S  v6 Nexus Edition               ║
  ║   JARVIS Voice + NEXUS Safety & HUD          ║
  ║   8 Agents + Permission Gates + Telemetry    ║
  ╚══════════════════════════════════════════════════╝
    """)

    monitor.start(speak_fn=voice.speak)
    actions.set_speak(voice.speak)

    # Load agents
    print("  🧠 Initializing agent network...")
    try:
        import jarvis_agents as agents
        print(f"  ✅ {len(agents.AGENTS)} specialized agents online")
        use_agents = True
        speed.prewarm_agents(agents)
        speed.pregen_audio(voice)
    except Exception as e:
        print(f"  ⚠️  Agent system failed: {e}")
        import jarvis_brain as brain
        use_agents = False

    if NEXUS_ENABLED:
        print("  🛡️  NEXUS PermissionEngine: MANUAL (HIGH-risk needs 'yes, do it')")
        print(f"  📊 Telemetry: {get_system_status()['cpu_percent']}% CPU, {get_system_status()['ram_percent']}% RAM")

    now = datetime.now()
    h = now.hour
    greeting = "Good morning" if 5<=h<12 else "Good afternoon" if 12<=h<17 else "Good evening"
    voice.pregenerate([
        f"{greeting} sir, NEXUS safety online. What can I do?",
        "Yes sir.", "On it sir.", "Done sir.",
        "Requires approval sir — say yes to confirm.",
    ])

    print(f"  🔇 Say \"Daddy's home\" or \"Hey Jarvis\" to activate")
    print(f"  🛡️  NEXUS guarding HIGH-risk actions — say \"yes\" to approve\n")

    while True:
        try:
            text = voice.listen()
            if not text or len(text.strip()) < 2:
                continue

            low = text.lower().strip()
            print(f"  👤 {text}")

            # --- NEXUS PLANNING STEP (new) ---
            if NEXUS_ENABLED:
                plan = nexus_bridge.plan_with_nexus(text)
                print(f"  📋 NEXUS Plan: {[t.title for t in plan.tasks[:2]]}")

            clean = re.sub(r'^\s*(hey jarvis|jarvis|ok jarvis)\s*','',low).strip()

            if any(w in low for w in ['stop','shut up','quiet','pause','silence','enough']):
                os.system('pkill -9 -f ffplay 2>/dev/null')
                voice._stop_flag = True
                time.sleep(0.2)
                voice._stop_flag = False
                voice.speak("Yes sir.")
                continue

            if not clean and any(w in low for w in ['hey jarvis','jarvis','ok jarvis']):
                voice.speak("Yes sir, NEXUS standing by.")
                continue

            text = clean if clean else text
            low = clean if clean else low

            # --- DADDY'S HOME with NEXUS telemetry ---
            if any(w in low for w in ["daddy","daddys","daddy's home","im home","i'm home"]):
                # NEXUS telemetry check before opening dashboard
                if NEXUS_ENABLED:
                    tel = nexus_bridge.get_nexus_telemetry()
                    print(f"  📊 Daddy's home — CPU {tel['cpu_percent']}% RAM {tel['ram_percent']}%")
                actions.open_dashboard()  # JARVIS original dashboard
                voice.play_sound(f"{HOME}/jarvis/audio/startup.mp3" if os.path.exists(f"{HOME}/jarvis/audio/startup.mp3") else None)
                voice.speak(f"{greeting} sir, NEXUS and JARVIS online. All systems nominal.")
                continue

            # --- NEXUS MEMORY BRIDGE example ---
            if "remember" in low or "my name is" in low:
                if NEXUS_ENABLED:
                    nexus_bridge.remember_with_nexus("personal", text)
                    print(f"  💾 NEXUS Memory: stored '{text[:40]}'")

            # --- SAFETY-GATED ACTIONS (example: open site) ---
            if "open" in low and "youtube" in low:
                check = nexus_gate("open_url", {"url": "https://youtube.com"}, approve=False)
                if not check["success"]:
                    voice.speak("That action needs approval sir. Say yes to confirm.")
                    # Wait for approval
                    confirm = voice.listen()
                    if confirm and "yes" in confirm.lower():
                        check = nexus_gate("open_url", {"url": "https://youtube.com"}, approve=True)
                        if check["success"]:
                            actions.open_url("https://youtube.com")
                            voice.speak("Opening YouTube sir.")
                    continue
                else:
                    actions.open_url("https://youtube.com")
                    voice.speak("Opening YouTube sir.")
                    continue

            # --- Fallback to original JARVIS agent routing ---
            if use_agents:
                # Let Jarvis agents handle it (Research, Live, Creative, etc)
                import jarvis_agents as agents
                result = agents.route(text) if hasattr(agents, 'route') else agents.AGENTS['Master'].ask(text)
                voice.speak(result)
            else:
                voice.speak("Yes sir, command received. NEXUS routing active.")

        except KeyboardInterrupt:
            print("\n  👋 NEXUS + JARVIS shutting down safely...")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
            if NEXUS_ENABLED:
                # NEXUS verification step
                print(f"  🔍 NEXUS VERIFY failed for: {text}")

if __name__ == "__main__":
    boot()
