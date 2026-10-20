#!/usr/bin/env python3
"""J.A.R.V.I.S Integrations"""
import os, re, subprocess, time, threading, urllib.request, json
from datetime import datetime

HOME = os.path.expanduser("~")
BROWSER = "google-chrome"
PROFILE = f"{HOME}/.config/google-chrome"

def analyze_screen(question="What do you see on this screen?"):
    try:
        import anthropic, base64
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = f"{HOME}/Pictures/vision_{ts}.png"
        os.makedirs(f"{HOME}/Pictures", exist_ok=True)
        time.sleep(1)
        os.system(f'DISPLAY=:0 gnome-screenshot -f "{path}" 2>/dev/null || DISPLAY=:0 scrot "{path}" 2>/dev/null')
        if not os.path.exists(path): return "Could not capture screen sir."
        with open(path,'rb') as f: img_data = __import__('base64').b64encode(f.read()).decode()
        key = open(f"{HOME}/jarvis/.api_key").read().strip()
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=200,
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":"image/png","data":img_data}},
                {"type":"text","text":f"You are Jarvis from Iron Man. {question} Answer in 2 sentences, spoken style, end with sir."}
            ]}])
        return resp.content[0].text.strip()
    except Exception as e:
        return f"Vision unavailable sir."

def compose_email(to, subject, body):
    import urllib.parse
    url = f"https://mail.google.com/mail/?view=cm&to={urllib.parse.quote(to)}&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    subprocess.Popen([BROWSER, f"--user-data-dir={PROFILE}", url])
    return "Gmail compose opened sir."

def open_gmail(): 
    subprocess.Popen([BROWSER, f"--user-data-dir={PROFILE}", "https://mail.google.com"])
    return "Opening Gmail sir."

def open_calendar():
    subprocess.Popen([BROWSER, f"--user-data-dir={PROFILE}", "https://calendar.google.com"])
    return "Opening your calendar sir."

def spotify_search(query):
    import urllib.parse
    subprocess.Popen([BROWSER, f"--user-data-dir={PROFILE}", f"https://open.spotify.com/search/{urllib.parse.quote(query)}"])
    return f"Searching Spotify for {query} sir."

def spotify_control(action):
    keys = {'next':'ctrl+Right','previous':'ctrl+Left','pause':'space','play':'space'}
    key = keys.get(action.lower())
    if key: os.system(f'xdotool key {key} 2>/dev/null'); return f"Spotify {action} sir."
    return None

def get_battery():
    try:
        pct = open('/sys/class/power_supply/BAT0/capacity').read().strip()
        status = open('/sys/class/power_supply/BAT0/status').read().strip()
        return f"Battery at {pct}%, {status.lower()} sir."
    except: return "Battery info unavailable sir."

def get_ip():
    try:
        local = subprocess.run(['hostname','-I'],capture_output=True,text=True).stdout.strip().split()[0]
        pub = urllib.request.urlopen('https://api.ipify.org',timeout=4).read().decode()
        return f"Local IP {local}, public IP {pub} sir."
    except: return "Network info unavailable sir."

def set_reminder_at_time(message, hour, minute, speak_fn):
    def _wait():
        while True:
            now = datetime.now()
            if now.hour == hour and now.minute == minute:
                speak_fn(f"Sir, reminder: {message}")
                break
            time.sleep(30)
    threading.Thread(target=_wait, daemon=True).start()
    return f"Reminder set for {hour:02d}:{minute:02d} — {message} sir."

def parse_time_reminder(text):
    m = re.search(r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text.lower())
    msg = re.search(r'(?:to|about|that)\s+(.+?)(?:\s+at\s+\d|$)', text.lower())
    if m:
        h = int(m.group(1)); mn = int(m.group(2) or 0); ampm = m.group(3) or ''
        if 'pm' in ampm and h != 12: h += 12
        if 'am' in ampm and h == 12: h = 0
        return h, mn, (msg.group(1).strip() if msg else "your reminder")
    return None, None, None

def auto_restart_watcher():
    def _watch():
        time.sleep(30)
        while True:
            r = subprocess.run(['pgrep','-f','jarvis_v6.py'],capture_output=True)
            if not r.stdout.strip():
                subprocess.Popen(['python3',f'{HOME}/jarvis/jarvis_v6.py'],start_new_session=True)
                break
            time.sleep(10)
    threading.Thread(target=_watch,daemon=True).start()

def route(text, speak_fn=None):
    low = text.lower().strip()

    if any(p in low for p in ["what's on my screen","whats on my screen","what do you see","analyze my screen","read my screen"]):
        return analyze_screen(text)

    if 'send email' in low or 'compose email' in low or 'email to' in low:
        to = re.search(r'to\s+(\S+@\S+|\w+)', low)
        subj = re.search(r'(?:subject|about)\s+(.+?)(?:\s+saying|$)', low)
        body = re.search(r'(?:saying|body|message)\s+(.+?)$', low)
        if to: return compose_email(to.group(1), subj.group(1) if subj else "Message", body.group(1) if body else "")
        return open_gmail()

    if 'open gmail' in low or 'check email' in low or 'my emails' in low:
        return open_gmail()

    if 'open calendar' in low or 'my calendar' in low or 'my schedule' in low:
        return open_calendar()

    if 'play' in low and any(w in low for w in ['spotify','music','song']):
        q = re.sub(r'play|on spotify|spotify|music|song','',low).strip()
        if q: return spotify_search(q)

    if 'next song' in low or 'skip' in low: return spotify_control('next')
    if 'previous song' in low: return spotify_control('previous')
    if 'pause music' in low: return spotify_control('pause')

    if 'battery' in low: return get_battery()
    if 'my ip' in low or 'ip address' in low: return get_ip()

    if 'remind me at' in low:
        h, m, msg = parse_time_reminder(low)
        if h is not None and speak_fn: return set_reminder_at_time(msg, h, m, speak_fn)

    return None
