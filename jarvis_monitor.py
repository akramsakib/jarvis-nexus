#!/usr/bin/env python3
"""J.A.R.V.I.S Monitor — Background Intelligence"""
import os, time, json, threading, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

HOME = os.path.expanduser("~")
NEWS_CACHE_FILE = f"{HOME}/jarvis/news_cache.json"
ALERT_FILE = f"{HOME}/jarvis/alerts.json"

# ── NEWS MONITOR ─────────────────────────────────────────────────
news_cache = []
alerts = []
_speak_fn = None

WATCH_KEYWORDS = [
    'portugal','ronaldo','cr7','world cup','fifa',
    'nepal','kathmandu','rupee',
    'bitcoin','crypto','btc',
    'breaking','urgent','major',
]

def set_speak(fn):
    global _speak_fn
    _speak_fn = fn

def fetch_news():
    global news_cache
    try:
        feeds = [
            'https://feeds.bbci.co.uk/news/world/rss.xml',
            'https://feeds.bbci.co.uk/sport/football/rss.xml',
        ]
        all_items = []
        for url in feeds:
            try:
                req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
                tree = ET.parse(urllib.request.urlopen(req, timeout=6))
                items = tree.getroot().findall('.//item')[:5]
                for i in items:
                    t = i.find('title')
                    if t is not None and t.text:
                        all_items.append(t.text.strip())
            except: pass
        news_cache = all_items
        # Save cache
        with open(NEWS_CACHE_FILE,'w') as f:
            json.dump({"headlines":news_cache,"updated":datetime.now().isoformat()},f)
        return news_cache
    except:
        return news_cache

def check_alerts(headlines):
    """Check if any headlines match watch keywords — alert user"""
    global alerts
    for h in headlines:
        h_lower = h.lower()
        for kw in WATCH_KEYWORDS:
            if kw in h_lower:
                # Check if we already alerted this
                if h not in alerts:
                    alerts.append(h)
                    if False and _speak_fn and 'portugal' in h_lower:
                        _speak_fn(f"Sir, breaking news about {kw}: {h[:80]}")
                    break

def monitor_loop():
    """Runs in background — fetches news every 5 min"""
    while True:
        try:
            headlines = fetch_news()
            check_alerts(headlines)
        except: pass
        time.sleep(5 * 60)

# ── WEATHER ──────────────────────────────────────────────────────
weather_cache = {}

def get_weather(city="Horsham", lat=40.1776, lon=-75.3596):
    try:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m,precipitation_probability&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=auto'
        w = json.loads(urllib.request.urlopen(url, timeout=6).read())
        c = w['current_weather']
        codes = {0:'clear skies',1:'mostly clear',2:'partly cloudy',3:'overcast',
                 45:'foggy',61:'light rain',63:'rain',71:'snow',80:'showers',95:'thunderstorms'}
        temp = round(c['temperature'])
        wind = round(c['windspeed'])
        cond = codes.get(c['weathercode'],'mixed conditions')
        hum = w['hourly']['relativehumidity_2m'][0]
        rain = w['hourly'].get('precipitation_probability',[0])[0]
        result = f"It is {temp}°F in {city} right now, {cond}, wind {wind} mph, humidity {hum}%."
        if rain > 30: result += f" {rain}% chance of rain."
        weather_cache[city] = {"text":result,"temp":temp,"cond":cond,"updated":datetime.now().isoformat()}
        return result
    except Exception as e:
        return weather_cache.get(city,{}).get("text", f"Weather data unavailable for {city} sir.")

CITY_COORDS = {
    'horsham':(40.1776,-75.3596),
    'new york':(40.7128,-74.0060), 'nyc':(40.7128,-74.0060),
    'philadelphia':(39.9526,-75.1652),
    'miami':(25.7617,-80.1918),
    'chicago':(41.8781,-87.6298),
    'london':(51.5074,-0.1278),
    'tokyo':(35.6762,139.6503),
    'dubai':(25.2048,55.2708),
    'kathmandu':(27.7172,85.3240), 'nepal':(27.7172,85.3240),
    'los angeles':(34.0522,-118.2437),
    'paris':(48.8566,2.3522),
    'lisbon':(38.7223,-9.1393),
}

def get_weather_for(text):
    text_lower = text.lower()
    for city,(lat,lon) in CITY_COORDS.items():
        if city in text_lower:
            return get_weather(city.title(), lat, lon)
    return get_weather()

# ── DAILY BRIEFING ───────────────────────────────────────────────
def daily_briefing_loop(speak_fn):
    """Auto-runs morning briefing at 8am"""
    briefed_today = None
    while True:
        now = datetime.now()
        today = now.date().isoformat()
        if now.hour == 8 and now.minute == 0 and briefed_today != today:
            briefed_today = today
            speak_fn(f"Good morning sir. It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}.")
            time.sleep(2)
            w = get_weather()
            speak_fn(w)
            time.sleep(1)
            headlines = news_cache[:3] if news_cache else []
            if headlines:
                speak_fn("Here are your top stories for today.")
                for h in headlines: speak_fn(h); time.sleep(0.5)
            speak_fn("Have a great day sir. I am standing by.")
        time.sleep(30)

def start(speak_fn=None):
    if speak_fn:
        set_speak(speak_fn)
        threading.Thread(target=daily_briefing_loop, args=(speak_fn,), daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()
    # Initial fetch
    threading.Thread(target=fetch_news, daemon=True).start()
    print("  📡 Monitor started")

if __name__ == "__main__":
    print("Monitor module loaded")
    fetch_news()
    print(f"Cached {len(news_cache)} headlines")
