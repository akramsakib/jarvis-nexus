#!/usr/bin/env python3
"""J.A.R.V.I.S Voice — edge_tts primary for speed, ElevenLabs for cached phrases"""
import os, re, asyncio, subprocess, hashlib, threading
import speech_recognition as sr

HOME = os.path.expanduser("~")
AUDIO = f"{HOME}/jarvis/audio"
os.makedirs(AUDIO, exist_ok=True)

ELEVEN_KEY   = "sk_08dd6a36e8b869da88bbb2ccaee7671d34e7ff6395bd749a"
ELEVEN_VOICE = "JBFqnCBsd6RMkjVDRZzb"

_is_speaking = False
_stop_flag   = False
_ffplay_proc = None

def stop():
    global _stop_flag, _ffplay_proc, _is_speaking
    _stop_flag = True
    _is_speaking = False
    os.system("pkill -9 -f ffplay 2>/dev/null")
    if _ffplay_proc:
        try: _ffplay_proc.kill()
        except: pass
    import time; time.sleep(0.3)

def is_stopped():
    return _stop_flag

def speak(text, wait=True):
    global _is_speaking, _stop_flag, _ffplay_proc
    _stop_flag = False
    t = re.sub(r'[\*#`_\[\]\(\)]','',str(text)).strip()
    t = re.sub(r'\s+',' ',t)
    if not t or _stop_flag: return
    print(f"\n  🤖  {t}\n")
    _is_speaking = True
    h = hashlib.md5(t.encode()).hexdigest()[:8]
    mp3 = f"{AUDIO}/s_{h}.mp3"
    if not os.path.exists(mp3):
        # Use edge_tts — fast, local, sounds good
        async def _gen():
            import edge_tts
            await edge_tts.Communicate(t,"en-GB-RyanNeural",rate="+10%",pitch="-8Hz").save(mp3)
        try: asyncio.run(_gen())
        except:
            _is_speaking = False
            return
    if _stop_flag:
        _is_speaking = False
        return
    # Double check before playing
    if _stop_flag:
        _is_speaking = False  
        return
    _ffplay_proc = subprocess.Popen(
        ["ffplay","-nodisp","-autoexit","-loglevel","quiet",mp3],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if wait:
        _ffplay_proc.wait()
    _is_speaking = False

def play_sound(path, wait=True):
    if os.path.exists(path):
        if wait:
            subprocess.run(["ffplay","-nodisp","-autoexit","-loglevel","quiet",path],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["ffplay","-nodisp","-autoexit","-loglevel","quiet",path],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_speaking(): return _is_speaking

rec = sr.Recognizer()
rec.energy_threshold = 300
rec.pause_threshold = 2.0
rec.non_speaking_duration = 1.5
rec.dynamic_energy_threshold = True

def listen(device=1, timeout=10, phrase_limit=60):
    try:
        with sr.Microphone(device_index=1) as src:
            rec.adjust_for_ambient_noise(src, duration=0.1)
            audio = rec.listen(src, timeout=timeout, phrase_time_limit=phrase_limit)
            text = rec.recognize_google(audio)
            print(f"  👤 {text}")
            return text
    except sr.WaitTimeoutError: return ""
    except sr.UnknownValueError: return ""
    except Exception:
        import time; time.sleep(0.2)
        return ""

def listen_for_stop(stop_fn):
    def _t():
        try:
            r = sr.Recognizer()
            r.energy_threshold = 500
            r.pause_threshold = 0.3
            with sr.Microphone(device_index=1) as src:
                audio = r.listen(src, timeout=5, phrase_time_limit=2)
                text = r.recognize_google(audio).lower()
                if any(w in text for w in ['stop','quiet','shut up','pause','enough']):
                    stop_fn()
        except: pass
    threading.Thread(target=_t, daemon=True).start()

def pregenerate(texts):
    async def _gen_all():
        import edge_tts
        for t in texts:
            h = hashlib.md5(t.encode()).hexdigest()[:8]
            mp3 = f"{AUDIO}/s_{h}.mp3"
            if not os.path.exists(mp3):
                try:
                    await edge_tts.Communicate(t,"en-GB-RyanNeural",rate="+10%",pitch="-8Hz").save(mp3)
                except: pass
    try: asyncio.run(_gen_all())
    except: pass

# ── ALWAYS-ON STOP LISTENER ──────────────────────────────────────
def start_stop_listener():
    """Runs forever in background — always listening for stop command"""
    import time
    def _run():
        while True:
            try:
                r = sr.Recognizer()
                r.energy_threshold = 200
                r.pause_threshold = 0.3
                r.dynamic_energy_threshold = False
                with sr.Microphone(device_index=1) as src:
                    while True:
                        try:
                            audio = r.listen(src, timeout=2, phrase_time_limit=2)
                            text = r.recognize_google(audio).lower().strip()
                            if any(w in text for w in ['stop','quiet','shut up','pause','enough','silence']):
                                print("  🛑 STOP detected!")
                                os.system("pkill -9 -f ffplay 2>/dev/null")
                        except sr.WaitTimeoutError: pass
                        except sr.UnknownValueError: pass
                        except Exception: time.sleep(0.1)
            except Exception as e:
                time.sleep(1)
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    print("  🛑 Stop listener active")
