#!/usr/bin/env python3
"""J.A.R.V.I.S Speed Module — Caching, Pre-warming, Streaming"""
import os, sys, json, time, threading, hashlib
from datetime import datetime

HOME = os.path.expanduser("~")
CACHE_FILE = f"{HOME}/jarvis/search_cache.json"
AUDIO = f"{HOME}/jarvis/audio"

# ── SEARCH CACHE ─────────────────────────────────────────────────
class SearchCache:
    def __init__(self):
        self.cache = self._load()
        self._lock = threading.Lock()

    def _load(self):
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE) as f:
                    return json.load(f)
        except: pass
        return {}

    def _save(self):
        with open(CACHE_FILE,'w') as f:
            json.dump(self.cache, f)

    def get(self, query, max_age=600):
        """Get cached result if fresh enough (default 10 min)"""
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                age = time.time() - entry['timestamp']
                if age < max_age:
                    print(f"  ⚡ Cache hit: {query[:40]}")
                    return entry['result']
        return None

    def set(self, query, result):
        """Cache a result"""
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        with self._lock:
            self.cache[key] = {
                'result': result,
                'timestamp': time.time(),
                'query': query[:100]
            }
            # Keep cache small - max 200 entries
            if len(self.cache) > 200:
                oldest = sorted(self.cache.items(), key=lambda x: x[1]['timestamp'])[:50]
                for k,_ in oldest:
                    del self.cache[k]
            self._save()

cache = SearchCache()

# ── PRE-WARM AGENTS ──────────────────────────────────────────────
WARMUP_QUERIES = {
    "research":  "What are the latest tech news today?",
    "business":  "What is SchoolOS?",
    "personal":  "How are you today?",
    "live":      "What is Bitcoin price?",
    "creative":  "Tell me a joke",
    "health":    "What should I eat for breakfast?",
    "finance":   "What is USD to NPR rate?",
}

def prewarm_agents(agents_module):
    """Pre-warm all agents with real queries so first response is instant"""
    def _warm():
        time.sleep(5)  # Wait for boot to finish
        print("  🔥 Pre-warming agents...")
        for agent_name, query in WARMUP_QUERIES.items():
            try:
                agent = agents_module.AGENTS.get(agent_name)
                if agent:
                    result = agent.ask(query, max_tokens=50)
                    # Cache the result
                    cache.set(query, result)
                    print(f"  ✅ {agent_name} warmed")
            except Exception as e:
                print(f"  ❌ {agent_name}: {e}")
        print("  🔥 All agents pre-warmed - responses now instant!")
    threading.Thread(target=_warm, daemon=True).start()

# ── STREAMING SPEAK ──────────────────────────────────────────────
def speak_streaming(text, voice_module):
    """
    Split long response into sentences and speak first one immediately
    while generating the rest - feels much faster
    """
    import re
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return
    
    if len(sentences) == 1:
        # Single sentence - just speak normally
        voice_module.speak(text)
        return
    
    # Speak first sentence immediately
    voice_module.speak(sentences[0], wait=True)
    
    # Then speak remaining sentences
    for sentence in sentences[1:]:
        if voice_module._stop_flag:
            break
        voice_module.speak(sentence, wait=True)

# ── TTS PRE-GENERATOR ────────────────────────────────────────────
COMMON_RESPONSES = [
    # Greetings
    "Good morning sir, what can I do for you today?",
    "Good afternoon sir, what can I do for you today?",
    "Good evening sir, what can I do for you today?",
    # Acknowledgments
    "Yes sir.", "On it sir.", "Done sir.", "Right away sir.",
    "Of course sir.", "Certainly sir.", "Got it sir.",
    "Understood sir.", "One moment sir.", "Searching now sir.",
    "Opening that now sir.", "Sure sir.",
    # Actions
    "Timer set sir.", "Reminder set sir.",
    "Screenshot saved sir.", "Volume adjusted sir.",
    "Opening YouTube sir.", "Opening Gmail sir.",
    "Searching on YouTube sir.", "Opening Google Maps sir.",
    # Jarvis personality
    "As you wish sir.", "Consider it done sir.",
    "I am on it sir.", "Absolutely sir.",
    # Stop response
    "Yes daddy.", "Stopping sir.",
]

def pregen_audio(voice_module):
    """Pre-generate all common responses in background"""
    def _gen():
        import asyncio, hashlib, edge_tts
        async def _gen_all():
            for text in COMMON_RESPONSES:
                h = hashlib.md5(text.encode()).hexdigest()[:8]
                mp3 = f"{AUDIO}/s_{h}.mp3"
                if not os.path.exists(mp3):
                    try:
                        await edge_tts.Communicate(
                            text, "en-GB-RyanNeural",
                            rate="+10%", pitch="-8Hz"
                        ).save(mp3)
                    except: pass
        try:
            asyncio.run(_gen_all())
            print(f"  🔊 {len(COMMON_RESPONSES)} responses pre-generated")
        except Exception as e:
            print(f"  🔊 Pre-gen error: {e}")
    threading.Thread(target=_gen, daemon=True).start()

# ── CACHED DISPATCH ───────────────────────────────────────────────
def cached_dispatch(text, agents_module, max_age=300):
    """Check cache before calling agents"""
    # Don't cache very live queries
    live_keywords = ['score','price','bitcoin','btc','stock','weather','today','now','latest','breaking']
    is_live = any(w in text.lower() for w in live_keywords)
    
    if not is_live:
        cached = cache.get(text, max_age=max_age)
        if cached:
            return cached
    
    # Get fresh result
    result = agents_module.dispatch(text)
    
    # Cache if not live
    if not is_live and result:
        cache.set(text, result)
    
    return result

if __name__ == "__main__":
    print("Speed module loaded")
    print(f"Cache entries: {len(cache.cache)}")
