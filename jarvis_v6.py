#!/usr/bin/env python3
"""J.A.R.V.I.S v6.0 — Multi-Agent Super Intelligence"""
import os, sys, re, time, threading, subprocess, json
from datetime import datetime

HOME = os.path.expanduser("~")
sys.path.insert(0, f"{HOME}/jarvis")

import jarvis_voice as voice
import jarvis_actions as actions
import jarvis_monitor as monitor
import jarvis_integrations as integrations
import jarvis_speed as speed
import jarvis_proactive as proactive
import jarvis_content as content

# Load multi-agent system
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if __file__ != '<stdin>' else HOME+'/jarvis')

STARTUP = f"{HOME}/jarvis/audio/startup.mp3"
AUDIO   = f"{HOME}/jarvis/audio"

def boot():
    print("""
  ╔══════════════════════════════════════════════════╗
  ║   J.A.R.V.I.S  v6.0 — Multi-Agent Intelligence  ║
  ║   8 Specialized AI Brains Working In Parallel    ║
  ╚══════════════════════════════════════════════════╝
    """)

    # Start all systems
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

    # Pre-generate voices
    now = datetime.now()
    h = now.hour
    greeting = "Good morning" if 5<=h<12 else "Good afternoon" if 12<=h<17 else "Good evening"
    voice.pregenerate([
        f"{greeting} sir, what can I do for you today?",
        "Yes sir.", "On it sir.", "Done sir.",
        "Researching that now sir.", "Got it sir.",
    ])

    print(f"  🔇 Silent mode — say Daddy's home to activate")
    print(f"  🎙️  Always listening...\n")

    while True:
        try:
            text = voice.listen()
            if not text or len(text.strip()) < 2:
                continue

            low = text.lower().strip()
            print(f"  👤 {text}")

            # Strip wake words from query
            clean = re.sub(r'^\s*(hey jarvis|jarvis|ok jarvis)\s*','',low).strip()

            # ── STOP — kills speech instantly ─────────────────────
            if any(w in low for w in ['stop','shut up','quiet','pause','silence','enough']):
                os.system('pkill -9 -f ffplay 2>/dev/null')
                voice._stop_flag = True
                import time; time.sleep(0.2)
                voice._stop_flag = False
                voice.speak("Yes sir.")
                continue

            # If only wake word said with nothing else
            if not clean and any(w in low for w in ['hey jarvis','jarvis','ok jarvis']):
                voice.speak("Yes sir.")
                continue

            # Use clean text for all processing
            text = clean if clean else text
            low = clean if clean else low

            # ── DADDY'S HOME ──────────────────────────────────────
            if any(w in low for w in ["daddy","daddys","daddy's home","im home","i'm home"]):
                actions.open_dashboard()
                voice.play_sound(STARTUP)
                voice.speak(f"{greeting} sir, what can I do for you today?")
                continue

            # ── ASYNC RESEARCH ────────────────────────────────────
            if use_agents:
                research_patterns = [
                    r'research (.+) for me',
                    r'find out about (.+) by morning',
                    r'look into (.+) while i sleep',
                    r'get me a report on (.+)',
                ]
                for pattern in research_patterns:
                    m = re.search(pattern, low)
                    if m:
                        topic = m.group(1).strip()
                        result = agents.research_async(topic, topic[:20])
                        voice.speak(result)
                        break
                else:
                    pass

                # ── GET REPORT ───────────────────────────────────
                if 'give me the report' in low or 'whats the report on' in low or 'research results' in low:
                    topic = re.sub(r'give me the report|whats the report on|research results on|research results','',low).strip()
                    result = agents.get_report(topic)
                    voice.speak(result)
                    continue

            # ── LIVE SCORES ──────────────────────────────────────
            if any(w in low for w in ['live score','world cup score','whats the score','current score','match score']):
                result = proactive.get_live_scores()
                voice.speak(result)
                continue

            # ── WEATHER — direct API, fast ───────────────────────
            if any(w in low for w in ['weather','temperature','degrees','forecast','raining','sunny','humid','cold outside','hot outside']):
                result = monitor.get_weather_for(low)
                voice.speak(result)
                continue

            # ── NEWS — instant from cache ─────────────────────────
            if any(w in low for w in ['news','headlines','top stories','what happened']):
                headlines = monitor.news_cache[:3]
                if headlines:
                    voice.speak("Here are your top stories sir.")
                    for h2 in headlines:
                        voice.speak(h2)
                else:
                    voice.speak("News feed is loading sir, one moment.")
                continue

            # ── BRIEF ME ─────────────────────────────────────────
            if any(w in low for w in ['brief me','morning briefing','daily briefing','whats my day','status report']):
                voice.speak(f"{greeting} sir, here is your briefing.")
                voice.speak(monitor.get_weather())
                time.sleep(0.3)
                if monitor.news_cache:
                    voice.speak("Top stories:")
                    for h2 in monitor.news_cache[:3]: voice.speak(h2); time.sleep(0.3)
                if use_agents:
                    biz = agents.business_agent.ask("Give me a one sentence status check on SchoolOS, FIZON, and Lazy Looms based on what I've told you.")
                    voice.speak(biz)
                voice.speak("That is your briefing sir.")
                continue

            # ── SCREEN VISION ────────────────────────────────────
            if any(p in low for p in ["what's on my screen","whats on my screen","what do you see","analyze my screen","read my screen"]):
                voice.speak("Analyzing your screen sir.")
                result = integrations.analyze_screen(text)
                voice.speak(result)
                continue

            # ── INTEGRATIONS ─────────────────────────────────────
            result = integrations.route(text, speak_fn=voice.speak)
            if result:
                voice.speak(result)
                continue

            # ── SYSTEM ACTIONS ────────────────────────────────────
            result = actions.route(text, speak_fn=voice.speak)
            if result:
                voice.speak(result)
                continue

            # ── MULTI-AGENT DISPATCH ──────────────────────────────
            if use_agents:
                reply = speed.cached_dispatch(text, agents)
            else:
                import jarvis_brain as brain
                reply = brain.ask(text)

            if reply: speed.speak_streaming(reply, voice)

        except KeyboardInterrupt:
            voice.speak("Goodbye sir.")
            sys.exit(0)
        except Exception as e:
            print(f"  ❌ {e}")
            time.sleep(0.3)

if __name__ == "__main__":
    boot()
