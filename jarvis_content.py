#!/usr/bin/env python3
"""J.A.R.V.I.S Content Creator — Viral TikTok & Instagram Videos"""
import os, re, json, time, subprocess, threading, urllib.request
from datetime import datetime

HOME = os.path.expanduser("~")
CONTENT_DIR = f"{HOME}/jarvis/content"
os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(f"{CONTENT_DIR}/videos", exist_ok=True)
os.makedirs(f"{CONTENT_DIR}/scripts", exist_ok=True)
os.makedirs(f"{CONTENT_DIR}/audio", exist_ok=True)

API_KEY = open(f"{HOME}/jarvis/.api_key").read().strip()

# ── SCRIPT GENERATOR ─────────────────────────────────────────────
def generate_script(topic, style="tiktok", duration=30):
    """Generate viral video script using Claude"""
    import anthropic
    client = anthropic.Anthropic(api_key=API_KEY)
    
    style_prompts = {
        "tiktok": f"""Write a viral TikTok script about: {topic}
Rules:
- Hook in first 3 seconds (grab attention instantly)
- Total duration: {duration} seconds when spoken
- Fast paced, energetic, punchy
- Include [PAUSE] for dramatic effect
- Include [CAPTION: text] for on-screen text
- End with strong CTA (follow, like, comment)
- Trending style — like top TikTok creators
Format: Just the spoken script with stage directions in brackets.""",
        
        "instagram": f"""Write a viral Instagram Reel script about: {topic}
Rules:
- Hook in first 2 seconds
- {duration} seconds duration
- Conversational, authentic tone
- Include [TEXT ON SCREEN: text] markers
- Include [B-ROLL: description] for visuals
- Strong hook + value + CTA
Format: Spoken script with production notes in brackets.""",
        
        "educational": f"""Write a viral educational short video script about: {topic}
Rules:
- Start with shocking fact or question
- {duration} seconds
- Teach one thing clearly
- Include [VISUAL: description] markers  
- End with mind-blowing conclusion
- Make it shareable"""
    }
    
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role":"user","content": style_prompts.get(style, style_prompts["tiktok"])}]
    )
    return resp.content[0].text.strip()

# ── VOICEOVER GENERATOR ──────────────────────────────────────────
def generate_voiceover(script, output_path, voice="en-GB-RyanNeural"):
    """Generate voiceover from script using edge_tts"""
    import asyncio, edge_tts
    
    # Clean script — remove stage directions for audio
    clean = re.sub(r'\[.*?\]', '', script)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    async def _gen():
        await edge_tts.Communicate(clean, voice, rate="+15%", pitch="-5Hz").save(output_path)
    
    asyncio.run(_gen())
    return output_path

# ── TRENDING TOPICS FINDER ───────────────────────────────────────
def get_trending_topics():
    """Fetch trending topics from multiple sources"""
    import anthropic
    client = anthropic.Anthropic(api_key=API_KEY)
    
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        tools=[{"type":"web_search_20250305","name":"web_search"}],
        messages=[{"role":"user","content":"What are the top 10 trending topics on TikTok and Instagram right now in 2026? List them as a simple numbered list."}]
    )
    return "".join(b.text for b in resp.content if hasattr(b,'text') and b.text)

# ── VIDEO CREATOR ────────────────────────────────────────────────
def create_video(topic, style="tiktok", duration=30):
    """Full video creation pipeline"""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_topic = re.sub(r'[^a-z0-9]', '_', topic.lower())[:30]
    
    print(f"  🎬 Creating video: {topic}")
    
    # Step 1: Generate script
    print("  📝 Writing script...")
    script = generate_script(topic, style, duration)
    script_path = f"{CONTENT_DIR}/scripts/{safe_topic}_{ts}.txt"
    with open(script_path,'w') as f:
        f.write(f"TOPIC: {topic}\nSTYLE: {style}\nDURATION: {duration}s\n\n{script}")
    print(f"  ✅ Script saved: {script_path}")
    
    # Step 2: Generate voiceover
    print("  🎙️ Generating voiceover...")
    audio_path = f"{CONTENT_DIR}/audio/{safe_topic}_{ts}.mp3"
    generate_voiceover(script, audio_path)
    print(f"  ✅ Audio saved: {audio_path}")
    
    # Step 3: Create captions file
    captions = extract_captions(script)
    captions_path = f"{CONTENT_DIR}/scripts/{safe_topic}_{ts}_captions.txt"
    with open(captions_path,'w') as f:
        f.write('\n'.join(captions))
    
    # Step 4: Create simple video with ffmpeg (black bg + captions)
    video_path = f"{CONTENT_DIR}/videos/{safe_topic}_{ts}.mp4"
    
    # Get audio duration
    result = subprocess.run(
        ['ffprobe','-v','quiet','-print_format','json','-show_format', audio_path],
        capture_output=True, text=True
    )
    try:
        duration_sec = float(json.loads(result.stdout)['format']['duration'])
    except:
        duration_sec = duration
    
    # Create video: dark background + audio + title text
    title_clean = topic.replace("'","\\'")
    cmd = [
        'ffmpeg','-y',
        '-f','lavfi','-i',f'color=c=black:size=1080x1920:duration={duration_sec}:rate=30',
        '-i', audio_path,
        '-filter_complex',
        f"[0:v]drawtext=fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='{title_clean}':box=1:boxcolor=black@0.5:boxborderw=10[v]",
        '-map','[v]','-map','1:a',
        '-c:v','libx264','-c:a','aac',
        '-shortest', video_path,
        '-loglevel','quiet'
    ]
    
    subprocess.run(cmd)
    
    result = {
        "topic": topic,
        "style": style,
        "script": script,
        "script_path": script_path,
        "audio_path": audio_path,
        "video_path": video_path,
        "captions": captions,
        "created": datetime.now().isoformat()
    }
    
    # Save to content log
    log_path = f"{CONTENT_DIR}/content_log.json"
    log = []
    if os.path.exists(log_path):
        with open(log_path) as f: log = json.load(f)
    log.append(result)
    with open(log_path,'w') as f: json.dump(log[-50:], f, indent=2)
    
    print(f"  ✅ Video created: {video_path}")
    return result

def extract_captions(script):
    """Extract caption text from script"""
    captions = re.findall(r'\[(?:CAPTION|TEXT ON SCREEN): ([^\]]+)\]', script)
    if not captions:
        # Extract first few sentences as captions
        sentences = re.split(r'[.!?]+', script)
        captions = [s.strip() for s in sentences[:5] if len(s.strip()) > 10]
    return captions

# ── DAILY CONTENT SCHEDULER ──────────────────────────────────────
def daily_content_generator(speak_fn):
    """Generate content ideas every morning"""
    generated_today = None
    while True:
        now = datetime.now()
        today = now.date().isoformat()
        
        if now.hour == 9 and now.minute == 0 and generated_today != today:
            generated_today = today
            try:
                speak_fn("Good morning sir. I am generating your viral content ideas for today.")
                topics = get_trending_topics()
                speak_fn(f"Here are today's trending topics sir: {topics[:200]}")
                speak_fn("Say Jarvis create video about any topic to start creating.")
            except Exception as e:
                print(f"Daily content error: {e}")
        
        time.sleep(30)

# ── CONTENT COMMAND ROUTER ────────────────────────────────────────
def route(text, speak_fn=None):
    low = text.lower().strip()
    
    # CREATE VIDEO
    if any(p in low for p in ['create video','make video','make a video','create a video','film about','tiktok about','reel about']):
        topic = re.sub(r'create (a )?video (about)?|make (a )?video (about)?|tiktok about|reel about','',low).strip()
        if not topic or len(topic) < 3:
            return "What topic would you like me to create a video about sir?"
        
        if speak_fn: speak_fn(f"Creating a viral video about {topic} sir. This will take about 30 seconds.")
        
        def _create():
            try:
                result = create_video(topic)
                if speak_fn:
                    speak_fn(f"Your video is ready sir. Script and audio saved to your content folder. Open Files and go to jarvis/content/videos to find it.")
            except Exception as e:
                if speak_fn: speak_fn(f"Video creation encountered an error sir: {str(e)[:50]}")
        
        threading.Thread(target=_create, daemon=True).start()
        return None
    
    # GET TRENDING TOPICS
    if any(p in low for p in ['trending topics','what is trending','whats trending','viral topics','content ideas']):
        if speak_fn: speak_fn("Checking what is trending right now sir.")
        def _trend():
            try:
                topics = get_trending_topics()
                if speak_fn: speak_fn(f"Here are the trending topics sir: {topics[:300]}")
            except Exception as e:
                if speak_fn: speak_fn("Could not fetch trending topics sir.")
        threading.Thread(target=_trend, daemon=True).start()
        return None
    
    # GENERATE SCRIPT ONLY
    if any(p in low for p in ['write script','generate script','script for','script about']):
        topic = re.sub(r'write script (for|about)?|generate script (for|about)?|script for|script about','',low).strip()
        if not topic: return "What topic should I write a script for sir?"
        if speak_fn: speak_fn(f"Writing a viral script for {topic} sir.")
        def _script():
            try:
                script = generate_script(topic)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                path = f"{CONTENT_DIR}/scripts/{topic.replace(' ','_')}_{ts}.txt"
                with open(path,'w') as f: f.write(script)
                if speak_fn: speak_fn(f"Script complete sir. Saved to your content folder. Here is the opening: {script[:150]}")
            except Exception as e:
                if speak_fn: speak_fn("Script generation failed sir.")
        threading.Thread(target=_script, daemon=True).start()
        return None
    
    # LIST RECENT CONTENT
    if any(p in low for p in ['my videos','recent content','content i made','what videos']):
        log_path = f"{CONTENT_DIR}/content_log.json"
        if os.path.exists(log_path):
            with open(log_path) as f: log = json.load(f)
            if log:
                recent = log[-3:]
                result = f"Your last {len(recent)} videos sir: "
                result += ", ".join(v['topic'] for v in recent)
                return result
        return "No videos created yet sir. Say create video about any topic to start."
    
    return None

def start(speak_fn):
    threading.Thread(target=daily_content_generator, args=(speak_fn,), daemon=True).start()
    print("  🎬 Content creator active")

if __name__ == "__main__":
    print("Content module loaded")
    print(f"Content dir: {CONTENT_DIR}")
