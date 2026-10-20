#!/usr/bin/env python3
"""J.A.R.V.I.S Proactive Intelligence — Alerts, Pattern Learning, Overnight Research"""
import os, json, time, threading, urllib.request, re
from datetime import datetime, timedelta

HOME = os.path.expanduser("~")
PATTERNS_FILE = f"{HOME}/jarvis/patterns.json"
ALERTS_FILE   = f"{HOME}/jarvis/alerts_sent.json"
RESEARCH_FILE = f"{HOME}/jarvis/overnight_research.json"

# ── PATTERN LEARNING ─────────────────────────────────────────────
class PatternLearner:
    def __init__(self):
        self.data = self._load()
    
    def _load(self):
        try:
            if os.path.exists(PATTERNS_FILE):
                with open(PATTERNS_FILE) as f: return json.load(f)
        except: pass
        return {
            "hourly_activity": {},    # hour -> query count
            "top_queries": {},         # query -> count
            "wake_times": [],          # list of hours when daddy's home said
            "last_active": None,
            "session_count": 0,
            "total_queries": 0
        }
    
    def save(self):
        with open(PATTERNS_FILE,'w') as f: json.dump(self.data, f, indent=2)
    
    def log_query(self, query):
        hour = str(datetime.now().hour)
        self.data["hourly_activity"][hour] = self.data["hourly_activity"].get(hour, 0) + 1
        key = query.lower().strip()[:50]
        self.data["top_queries"][key] = self.data["top_queries"].get(key, 0) + 1
        self.data["total_queries"] = self.data.get("total_queries", 0) + 1
        self.data["last_active"] = datetime.now().isoformat()
        self.save()
    
    def log_wake(self):
        hour = datetime.now().hour
        self.data["wake_times"].append(hour)
        self.data["wake_times"] = self.data["wake_times"][-20:]
        self.data["session_count"] = self.data.get("session_count", 0) + 1
        self.save()
    
    def get_most_active_hour(self):
        if not self.data["hourly_activity"]: return None
        return max(self.data["hourly_activity"], key=self.data["hourly_activity"].get)
    
    def get_top_queries(self, n=5):
        sq = sorted(self.data["top_queries"].items(), key=lambda x: x[1], reverse=True)
        return [q for q,_ in sq[:n]]
    
    def get_insight(self):
        top = self.get_top_queries(3)
        hour = self.get_most_active_hour()
        total = self.data.get("total_queries", 0)
        if not top: return None
        insight = f"You have asked me {total} questions total sir. "
        if top: insight += f"You most frequently ask about {top[0]}. "
        if hour: insight += f"You are most active at {hour}:00."
        return insight

patterns = PatternLearner()

# ── PROACTIVE ALERTS ──────────────────────────────────────────────
alerts_sent = set()
_speak_fn = None

def set_speak(fn):
    global _speak_fn
    _speak_fn = fn

def load_alerts():
    global alerts_sent
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE) as f:
                data = json.load(f)
                alerts_sent = set(data.get("sent", []))
    except: pass

def save_alerts():
    with open(ALERTS_FILE,'w') as f:
        json.dump({"sent": list(alerts_sent)[-100:]}, f)

def alert(msg, key):
    """Send alert if not already sent in last hour"""
    if key in alerts_sent: return
    alerts_sent.add(key)
    save_alerts()
    if _speak_fn:
        _speak_fn(f"Sir, {msg}")

# Monitor Portugal/Ronaldo news
def monitor_football_alerts():
    while True:
        try:
            import xml.etree.ElementTree as ET
            req = urllib.request.Request(
                'https://feeds.bbci.co.uk/sport/football/rss.xml',
                headers={'User-Agent':'Mozilla/5.0'}
            )
            tree = ET.parse(urllib.request.urlopen(req, timeout=6))
            for item in tree.getroot().findall('.//item')[:10]:
                t = item.find('title')
                if t is None or not t.text: continue
                title = t.text.strip()
                title_low = title.lower()
                
                key = f"football_{hash(title)}"
                
                if any(w in title_low for w in ['portugal','ronaldo','cr7','world cup goal','world cup score']):
                    alert(f"football update sir: {title}", key)
                    
        except: pass
        time.sleep(3 * 60)  # Check every 3 minutes

# Monitor Bitcoin price swings
_last_btc = None
def monitor_bitcoin():
    global _last_btc
    while True:
        try:
            data = json.loads(urllib.request.urlopen(
                'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true',
                timeout=5
            ).read())
            price = data['bitcoin']['usd']
            change = data['bitcoin'].get('usd_24h_change', 0)
            
            if _last_btc is not None:
                pct_change = abs((price - _last_btc) / _last_btc * 100)
                if pct_change > 3:
                    direction = "up" if price > _last_btc else "down"
                    key = f"btc_{int(price/1000)}"
                    alert(f"Bitcoin is {direction} {pct_change:.1f}% and now at ${price:,.0f} sir.", key)
            
            # Alert on big 24hr moves
            if abs(change) > 5:
                direction = "up" if change > 0 else "down"
                key = f"btc_24h_{int(change)}"
                alert(f"Bitcoin is {direction} {abs(change):.1f}% in the last 24 hours, currently at ${price:,.0f}.", key)
            
            _last_btc = price
        except: pass
        time.sleep(2 * 60)  # Check every 2 minutes

# Monitor breaking world news
_seen_headlines = set()
def monitor_breaking_news():
    global _seen_headlines
    while True:
        try:
            import xml.etree.ElementTree as ET
            req = urllib.request.Request(
                'https://feeds.bbci.co.uk/news/world/rss.xml',
                headers={'User-Agent':'Mozilla/5.0'}
            )
            tree = ET.parse(urllib.request.urlopen(req, timeout=6))
            for item in tree.getroot().findall('.//item')[:5]:
                t = item.find('title')
                if t is None or not t.text: continue
                title = t.text.strip()
                title_low = title.lower()
                key = f"news_{hash(title)}"
                
                # Only alert for truly breaking news
                breaking_words = ['breaking','urgent','just in','alert','major','attack','earthquake','crash']
                if any(w in title_low for w in breaking_words) and key not in _seen_headlines:
                    _seen_headlines.add(key)
                    alert(f"breaking news: {title}", key)
                    
        except: pass
        time.sleep(2 * 60)  # Check every 2 min

# Hydration reminder
def hydration_reminder():
    last_remind = datetime.now()
    while True:
        time.sleep(30 * 60)  # Check every 30 min
        now = datetime.now()
        # Only remind between 8am and 10pm
        if 8 <= now.hour <= 22:
            hours_since = (now - last_remind).seconds / 3600
            if hours_since >= 2:
                key = f"hydration_{now.strftime('%Y%m%d%H')}"
                alert("you have been active for 2 hours. Stay hydrated sir, drink some water.", key)
                last_remind = now

# Work session tracker  
_session_start = None
def track_work_session():
    global _session_start
    while True:
        time.sleep(60)
        if _session_start:
            hours = (datetime.now() - _session_start).seconds / 3600
            if hours >= 2:
                key = f"break_{datetime.now().strftime('%Y%m%d%H')}"
                alert("you have been working for over 2 hours. Consider taking a short break sir.", key)
                _session_start = datetime.now()  # Reset

def start_session():
    global _session_start
    _session_start = datetime.now()
    patterns.log_wake()

# ── OVERNIGHT RESEARCH ───────────────────────────────────────────
research_queue = []
research_results = {}

def add_research_task(topic):
    research_queue.append({
        "topic": topic,
        "added": datetime.now().isoformat(),
        "status": "pending"
    })
    save_research()
    return f"Research task queued sir. I will have a full report on {topic} ready for you."

def save_research():
    with open(RESEARCH_FILE,'w') as f:
        json.dump({
            "queue": research_queue,
            "results": research_results
        }, f, indent=2)

def load_research():
    global research_queue, research_results
    try:
        if os.path.exists(RESEARCH_FILE):
            with open(RESEARCH_FILE) as f:
                data = json.load(f)
                research_queue = data.get("queue", [])
                research_results = data.get("results", {})
    except: pass

def process_research_queue(brain_ask_fn):
    """Process research tasks in background"""
    def _process():
        while True:
            for task in research_queue:
                if task.get("status") == "pending":
                    topic = task["topic"]
                    print(f"  🔍 Researching: {topic}")
                    try:
                        result = brain_ask_fn(
                            f"Do comprehensive research on: {topic}. Give 5 detailed findings with specific facts, numbers, and actionable insights. Be thorough.",
                            max_tokens=400
                        )
                        research_results[topic] = {
                            "result": result,
                            "completed": datetime.now().isoformat()
                        }
                        task["status"] = "complete"
                        save_research()
                        print(f"  ✅ Research complete: {topic}")
                        # Alert user
                        if _speak_fn:
                            _speak_fn(f"Sir, I have completed my research on {topic}. Say get report on {topic} to hear it.")
                    except Exception as e:
                        task["status"] = "error"
                        print(f"  ❌ Research failed: {e}")
            time.sleep(30)
    threading.Thread(target=_process, daemon=True).start()

def get_report(topic):
    for key, result in research_results.items():
        if topic.lower() in key.lower():
            return f"Here is my research on {key} sir: {result['result']}"
    # Check queue
    for task in research_queue:
        if topic.lower() in task['topic'].lower():
            if task['status'] == 'pending':
                return f"Still researching {topic} sir, I will alert you when complete."
    return f"No research found on {topic} sir. Say research {topic} for me to start."

# ── START ALL MONITORS ───────────────────────────────────────────
def start(speak_fn, brain_ask_fn=None):
    set_speak(speak_fn)
    load_alerts()
    load_research()
    
    # Start all background monitors
    threading.Thread(target=monitor_football_alerts, daemon=True).start()
    threading.Thread(target=monitor_bitcoin, daemon=True).start()
    threading.Thread(target=monitor_breaking_news, daemon=True).start()
    threading.Thread(target=hydration_reminder, daemon=True).start()
    threading.Thread(target=track_work_session, daemon=True).start()
    threading.Thread(target=monitor_world_cup_scores, daemon=True).start()
    threading.Thread(target=monitor_battery, daemon=True).start()
    threading.Thread(target=auto_morning, daemon=True).start()
    threading.Thread(target=auto_night_mode, daemon=True).start()
    print("  ⚽ World Cup live scores: ON")
    print("  🔋 Battery monitor: ON")
    print("  🌙 Auto night mode: ON")
    
    if brain_ask_fn:
        process_research_queue(brain_ask_fn)
    
    print("  📡 Proactive intelligence active")
    print("  ⚽ Football alerts: ON")
    print("  ₿  Bitcoin alerts: ON")
    print("  📰 Breaking news: ON")
    print("  💧 Hydration reminders: ON")

if __name__ == "__main__":
    print("Proactive module loaded")

# ── LIVE WORLD CUP SCORES ────────────────────────────────────────
_last_scores = {}

def monitor_world_cup_scores():
    """Check live World Cup scores every 2 minutes"""
    global _last_scores
    while True:
        try:
            # Use ESPN API - free, no key needed
            url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=6).read())
            
            events = data.get('events', [])
            for event in events:
                game_id = event.get('id','')
                status = event.get('status',{})
                state = status.get('type',{}).get('state','')
                detail = status.get('type',{}).get('description','')
                
                comps = event.get('competitions',[{}])[0]
                teams = comps.get('competitors',[])
                
                if len(teams) < 2: continue
                
                home = teams[0].get('team',{}).get('displayName','')
                away = teams[1].get('team',{}).get('displayName','')
                home_score = teams[0].get('score','0')
                away_score = teams[1].get('score','0')
                
                score_key = f"{game_id}_{home_score}_{away_score}"
                game_str = f"{home} {home_score} - {away_score} {away}"
                
                # Alert on score change
                if game_id in _last_scores and _last_scores[game_id] != score_key:
                    # Score changed - GOAL!
                    is_portugal = any(p in home.lower() or p in away.lower() 
                                     for p in ['portugal'])
                    
                    if is_portugal:
                        alert(f"GOAL! Portugal score update: {game_str}", score_key)
                    else:
                        alert(f"goal in the World Cup: {game_str}", score_key)
                
                # Alert on game start
                if state == 'in' and game_id not in _last_scores:
                    is_portugal = any(p in home.lower() or p in away.lower() 
                                     for p in ['portugal'])
                    if is_portugal:
                        alert(f"Portugal's match has kicked off sir! {game_str}", f"start_{game_id}")
                
                _last_scores[game_id] = score_key
                
                # Alert on game end
                if state == 'post':
                    is_portugal = any(p in home.lower() or p in away.lower() 
                                     for p in ['portugal'])
                    if is_portugal:
                        key = f"end_{game_id}"
                        winner = home if int(home_score) > int(away_score) else away
                        alert(f"Portugal match ended sir. Final score: {game_str}. {winner} won.", key)
                        
        except Exception as e:
            pass
        time.sleep(2 * 60)  # Check every 2 minutes

def get_live_scores():
    """Get current World Cup scores"""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=6).read())
        events = data.get('events', [])
        if not events:
            return "No live World Cup matches right now sir."
        results = []
        for event in events[:5]:
            comps = event.get('competitions',[{}])[0]
            teams = comps.get('competitors',[])
            status = event.get('status',{}).get('type',{}).get('description','')
            if len(teams) < 2: continue
            home = teams[0].get('team',{}).get('displayName','')
            away = teams[1].get('team',{}).get('displayName','')
            hs = teams[0].get('score','0')
            as_ = teams[1].get('score','0')
            results.append(f"{home} {hs} - {as_} {away} ({status})")
        return "Live scores sir: " + ". ".join(results)
    except:
        return "Could not fetch live scores sir."

# ── BATTERY MONITOR ──────────────────────────────────────────────
def monitor_battery():
    alerted_low = False
    while True:
        try:
            pct = int(open('/sys/class/power_supply/BAT0/capacity').read().strip())
            status = open('/sys/class/power_supply/BAT0/status').read().strip()
            if pct <= 20 and status != 'Charging' and not alerted_low:
                alert(f"battery is at {pct} percent sir. Please plug in your charger.", f"bat_{pct}")
                alerted_low = True
            if pct > 25:
                alerted_low = False
        except: pass
        time.sleep(5 * 60)

# ── AUTO MORNING OPEN ────────────────────────────────────────────
def auto_morning():
    opened_today = None
    while True:
        now = datetime.now()
        today = now.date().isoformat()
        if now.hour == 8 and now.minute == 0 and opened_today != today:
            opened_today = today
            if _speak_fn:
                _speak_fn(f"Good morning sir. It is 8 AM. Starting your daily briefing.")
        time.sleep(30)

# ── NIGHT MODE AUTO ──────────────────────────────────────────────
def auto_night_mode():
    night_on = False
    while True:
        now = datetime.now()
        if now.hour >= 22 and not night_on:
            import os
            os.system('pactl set-sink-volume @DEFAULT_SINK@ 50%')
            if _speak_fn:
                _speak_fn("Night mode activated sir. I have lowered the volume.")
            night_on = True
        if now.hour == 7 and night_on:
            os.system('pactl set-sink-volume @DEFAULT_SINK@ 80%')
            night_on = False
        time.sleep(60)
