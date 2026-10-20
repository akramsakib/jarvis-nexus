#!/usr/bin/env python3
"""J.A.R.V.I.S Actions — System & App Control"""
import os, re, subprocess, time, threading
from datetime import datetime

HOME = os.path.expanduser("~")
BROWSER = "google-chrome"
PROFILE = f"{HOME}/.config/google-chrome"
AUDIO = f"{HOME}/jarvis/audio"

SITES = {
    'youtube':'https://youtube.com','claude':'https://claude.ai',
    'gmail':'https://gmail.com','email':'https://mail.google.com','mail':'https://mail.google.com','netflix':'https://netflix.com',
    'spotify':'https://open.spotify.com','bbc':'https://bbc.com/news',
    'instagram':'https://instagram.com','twitter':'https://twitter.com',
    'reddit':'https://reddit.com','amazon':'https://amazon.com',
    'facebook':'https://facebook.com','whatsapp':'https://web.whatsapp.com',
    'nbc':'https://nbcnews.com','google':'https://google.com',
    'linkedin':'https://linkedin.com','maps':'https://maps.google.com',
    'github':'https://github.com','chatgpt':'https://chat.openai.com',
    'x':'https://twitter.com','tiktok':'https://tiktok.com',
    'pinterest':'https://pinterest.com','snapchat':'https://snapchat.com',
    'twitch':'https://twitch.tv','discord':'https://discord.com/app',
    'paypal':'https://paypal.com','ebay':'https://ebay.com',
    'booking':'https://booking.com','airbnb':'https://airbnb.com',
    'notion':'https://notion.so','trello':'https://trello.com',
    'figma':'https://figma.com','canva':'https://canva.com',
    'dropbox':'https://dropbox.com','drive':'https://drive.google.com',
    'docs':'https://docs.google.com','sheets':'https://sheets.google.com',
    'slides':'https://slides.google.com','meet':'https://meet.google.com',
    'zoom':'https://zoom.us','teams':'https://teams.microsoft.com',
    'schoolos':'https://schoolos.app','nepse':'https://nepalstock.com',
    'weather':'https://weather.com','translate':'https://translate.google.com',
    'wikipedia':'https://wikipedia.org','stackoverflow':'https://stackoverflow.com',
    'medium':'https://medium.com','producthunt':'https://producthunt.com',
}

APPS = {
    # Dev tools
    'vs code':'code','vscode':'code','visual studio':'code','visual studio code':'code',
    'terminal':'gnome-terminal','files':'nautilus','file manager':'nautilus',
    # System
    'calculator':'gnome-calculator','settings':'gnome-control-center',
    'system monitor':'gnome-system-monitor','task manager':'gnome-system-monitor',
    'disk usage':'baobab','screenshot tool':'gnome-screenshot',
    # Communication
    'discord':'discord','telegram':'telegram-desktop','zoom':'zoom',
    'slack':'slack','teams':'teams',
    # Media
    'vlc':'vlc','music':'rhythmbox','videos':'totem',
    'image viewer':'eog','photos':'eog',
    # Office
    'text editor':'gedit','notepad':'gedit',
    'libreoffice':'libreoffice','word':'libreoffice --writer',
    'excel':'libreoffice --calc','powerpoint':'libreoffice --impress',
    # Other
    'gimp':'gimp','inkscape':'inkscape',
}

# Dynamic app finder — finds any installed app
def find_and_open(app_name):
    import shutil, subprocess
    # Try direct command
    if shutil.which(app_name.lower().replace(' ','-')):
        subprocess.Popen([app_name.lower().replace(' ','-')], start_new_session=True)
        return True
    if shutil.which(app_name.lower().replace(' ','_')):
        subprocess.Popen([app_name.lower().replace(' ','_')], start_new_session=True)
        return True
    # Try xdg-open
    result = subprocess.run(['which', app_name.lower()], capture_output=True, text=True)
    if result.stdout.strip():
        subprocess.Popen([result.stdout.strip()], start_new_session=True)
        return True
    return False


# ── BROWSER ──────────────────────────────────────────────────────
def open_url(url, name=""):
    subprocess.Popen([BROWSER, url])
    return f"Opening {name or url}, sir."

def open_dashboard():
    dash = f"{HOME}/jarvis/jarvis-dashboard.html"
    subprocess.Popen([BROWSER,
        "--use-fake-ui-for-media-stream","--disable-web-security",
        f"--user-data-dir={PROFILE}","--kiosk","--start-fullscreen",
        "--disable-infobars","--no-first-run","--test-type",
        f"file://{dash}"])

def youtube_search(query):
    url = f"https://youtube.com/results?search_query={query.replace(' ','+')}"
    subprocess.Popen([BROWSER, url])
    return f"Searching {query} on YouTube, sir."

def google_search(query):
    url = f"https://google.com/search?q={query.replace(' ','+')}"
    subprocess.Popen([BROWSER, url])
    return f"Searching {query} on Google, sir."

def maps_directions(destination):
    url = f"https://maps.google.com/maps?q={destination.replace(' ','+')}"
    subprocess.Popen([BROWSER, url])
    return f"Opening directions to {destination}, sir."

# ── APPS ─────────────────────────────────────────────────────────
def open_app(name):
    low = name.lower().strip()
    # Check known apps first
    cmd = APPS.get(low)
    if cmd:
        subprocess.Popen(cmd.split(), start_new_session=True)
        return f"Opening {name.title()}, sir."
    # Try dynamic finder
    if find_and_open(low):
        return f"Opening {name.title()}, sir."
    # Try xdg-open as last resort
    subprocess.Popen(['xdg-open', low], start_new_session=True)
    return f"Trying to open {name.title()}, sir." 

# ── SYSTEM ───────────────────────────────────────────────────────
def volume(action, level=None):
    if action == 'up':
        os.system('pactl set-sink-volume @DEFAULT_SINK@ +10%')
        return "Volume up, sir."
    elif action == 'down':
        os.system('pactl set-sink-volume @DEFAULT_SINK@ -10%')
        return "Volume down, sir."
    elif action == 'mute':
        os.system('pactl set-sink-mute @DEFAULT_SINK@ toggle')
        return "Audio toggled, sir."
    elif action == 'set' and level:
        os.system(f'pactl set-sink-volume @DEFAULT_SINK@ {min(150,level)}%')
        return f"Volume set to {level}%, sir."
    return None

def screenshot():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = f"{HOME}/Pictures/jarvis_{ts}.png"
    os.makedirs(f"{HOME}/Pictures", exist_ok=True)
    time.sleep(1.5)
    os.system(f'DISPLAY=:0 gnome-screenshot -f "{path}" 2>/dev/null || DISPLAY=:0 scrot "{path}" 2>/dev/null')
    return "Done sir." if os.path.exists(path) else "Screenshot failed sir."

def type_text(text):
    time.sleep(0.5)
    os.system(f'xdotool type --clearmodifiers "{text}" 2>/dev/null')
    return "Typed, sir."

def lock_screen():
    os.system('gnome-screensaver-command -l 2>/dev/null || xdg-screensaver lock 2>/dev/null')
    return "Screen locked, sir."

# ── TIMERS ───────────────────────────────────────────────────────
_speak_fn = None

def set_speak(fn):
    global _speak_fn
    _speak_fn = fn

def set_timer(minutes, label=""):
    def _run():
        time.sleep(minutes * 60)
        msg = f"Sir, your {label} timer is up." if label else f"Sir, {minutes} minute timer is up."
        if _speak_fn: _speak_fn(msg)
        # Also play a sound
        os.system(f'paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga 2>/dev/null || paplay /usr/share/sounds/ubuntu/stereo/bell.ogg 2>/dev/null')
    threading.Thread(target=_run, daemon=True).start()
    label_str = f" for {label}" if label else ""
    return f"Timer set{label_str} — {minutes} minutes, sir."

def parse_timer(text):
    m = re.search(r'(\d+)\s*(minute|min|second|sec|hour|hr)', text.lower())
    if not m: return None, None
    num = int(m.group(1))
    unit = m.group(2)
    if 'hour' in unit or 'hr' in unit: num *= 60
    elif 'sec' in unit: num = max(1, num // 60) or 1
    label_text = re.sub(r'(set a? ?timer|remind me in|timer for \d+ \w+s? for?|in \d+ \w+s?)', '', text.lower()).strip()
    label_text = re.sub(r'^\s*(for|to)\s+', '', label_text).strip()
    return num, label_text

# ── COMMAND ROUTER ───────────────────────────────────────────────
def route(text, speak_fn=None):
    """Route a command to the right action. Returns response string or None."""
    if speak_fn: set_speak(speak_fn)
    low = text.lower().strip()

    # STOP audio
    if any(w in low for w in ['stop','pause','shut up','quiet','silence']):
        os.system('pkill -f ffplay 2>/dev/null')
        return "Yes sir."

    # VOLUME
    if 'volume up' in low or 'louder' in low or 'turn up' in low or 'increase volume' in low:
        return volume('up')
    if ('volume down' in low or 'quieter' in low or 'turn down' in low or 'decrease volume' in low) and 'completely' not in low:
        return volume('down')
    if 'mute' in low or 'unmute' in low or 'turn down completely' in low or 'volume off' in low:
        return volume('mute')
    vol_num = re.search(r'(?:set\s+)?volume\s+(?:to\s+)?(\d+)', low)
    if vol_num: return volume('set', int(vol_num.group(1)))

    # SCREENSHOT
    if 'screenshot' in low or 'screen shot' in low or 'capture screen' in low:
        return screenshot()

    # TYPE
    if low.startswith('type '):
        return type_text(text[5:])

    # LOCK
    if 'lock screen' in low or 'lock computer' in low:
        return lock_screen()

    # TIMER
    if 'timer' in low or 'remind me in' in low:
        mins, label = parse_timer(low)
        if mins: return set_timer(mins, label)

    # MAPS / DIRECTIONS
    if any(w in low for w in ['directions to','take me to','navigate to','how do i get to','route to']):
        dest = re.sub(r'directions to|take me to|navigate to|how do i get to|route to|jarvis|hey','',low).strip()
        return maps_directions(dest)

    # OPEN SITES
    for name,url in SITES.items():
        if f'open {name}' in low or f'launch {name}' in low or f'go to {name}' in low:
            return open_url(url, name.title())

    # YOUTUBE SEARCH
    if 'youtube' in low and any(w in low for w in ['search','play','find','watch','show','look up']):
        q = re.sub(r'search|youtube|for|on|in|play|find|watch|show|look up','',low).strip()
        if q: return youtube_search(q)
        return open_url('https://youtube.com','YouTube')

    # GOOGLE SEARCH
    if 'search for ' in low or (low.startswith('search ') and 'youtube' not in low):
        q = re.sub(r'^search for |^search ','',low).strip()
        if q: return google_search(q)

    # OPEN APPS
    for name in APPS:
        if f'open {name}' in low or f'launch {name}' in low:
            result = open_app(name)
            if result: return result

    # OPEN CHROME
    if 'open chrome' in low or 'open browser' in low:
        subprocess.Popen([BROWSER])
        return "Opening Chrome, sir."

    return None  # Not a system command — send to brain

if __name__ == "__main__":
    print("Actions module loaded")
