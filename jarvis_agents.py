#!/usr/bin/env python3
"""J.A.R.V.I.S Multi-Agent System — Clean Version"""
import os, sys, re, json, time, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import anthropic

HOME = os.path.expanduser("~")
KEY  = open(f"{HOME}/jarvis/.api_key").read().strip()

# ── SHARED BRAIN ──────────────────────────────────────────────────
class SharedBrain:
    def __init__(self):
        self.memory  = self._load("memory.json",  {"facts":[],"ideas":[],"finance":[]})
        self.ideas   = self._load("ideas.json",   {"ideas":[]})
        self.reports = self._load("reports.json", {})
        self._lock   = threading.Lock()

    def _load(self, name, default):
        p = f"{HOME}/jarvis/{name}"
        try:
            if os.path.exists(p):
                with open(p) as f: return json.load(f)
        except: pass
        return default

    def save(self, name, data):
        with self._lock:
            with open(f"{HOME}/jarvis/{name}",'w') as f:
                json.dump(data, f, indent=2)

    def remember(self, fact, important=False):
        entry = {"text": fact, "time": datetime.now().isoformat()}
        self.memory["facts"].append(entry)
        self.save("memory.json", self.memory)

    def add_idea(self, idea, business=""):
        entry = {"idea": idea, "business": business, "time": datetime.now().isoformat()}
        self.ideas["ideas"].append(entry)
        self.save("ideas.json", self.ideas)

    def log_finance(self, amount, category):
        entry = {"amount": amount, "category": category, "time": datetime.now().isoformat()}
        self.memory["finance"].append(entry)
        self.save("memory.json", self.memory)

    def get_context(self):
        parts = []
        try:
            if self.memory.get("facts"):
                facts = [f["text"] for f in self.memory["facts"][-5:]]
                parts.append("Remember: " + "; ".join(facts))
            if self.memory.get("finance"):
                total = sum(e.get("amount",0) for e in self.memory["finance"][-10:])
                parts.append(f"Recent spending: ${total:.2f}")
        except: pass
        return "\n".join(parts)

brain = SharedBrain()

# ── BASE AGENT ────────────────────────────────────────────────────
BASE_PROMPT = """You are J.A.R.V.I.S, voice AI for Anurag Nepal in Horsham PA USA.
Ronaldo is THE GOAT. Portugal wins World Cup 2026.
Max 2 sentences. No markdown. Spoken English only. End with sir."""

class Agent:
    def __init__(self, name, system, use_search=False):
        self.name   = name
        self.system = system
        self.search = use_search
        self.client = anthropic.Anthropic(api_key=KEY)
        self.history = []
        self._warm  = True
        print(f"  🤖 {self.name} agent ready")

    def ask(self, text, max_tokens=120):
        try:
            self.history.append({"role":"user","content":text})
            if len(self.history) > 10:
                self.history = self.history[-8:]

            ctx = brain.get_context()
            system = self.system + ("\n" + ctx if ctx else "")

            needs_search = self.search and any(w in text.lower() for w in [
                "latest news","current price","live score","today score",
                "bitcoin price","stock price","breaking news","right now"
            ])

            req = dict(
                model="claude-haiku-4-5-20251001",
                max_tokens=max_tokens,
                system=system,
                messages=self.history
            )

            if needs_search:
                try:
                    req["tools"] = [{"type":"web_search_20250305","name":"web_search"}]
                    resp = self.client.messages.create(**req)
                except:
                    del req["tools"]
                    resp = self.client.messages.create(**req)
            else:
                resp = self.client.messages.create(**req)

            reply = "".join(b.text for b in resp.content if hasattr(b,"text") and b.text).strip()
            if not reply: reply = "On it sir."
            self.history.append({"role":"assistant","content":reply})
            return reply
        except Exception as e:
            print(f"  {self.name} error: {e}")
            return f"My {self.name.lower()} systems hit a snag sir."

# ── AGENTS ────────────────────────────────────────────────────────
research_agent = Agent("RESEARCH",
    BASE_PROMPT + "\nYou research and find information. Use web search for live data.",
    use_search=True)

business_agent = Agent("BUSINESS",
    BASE_PROMPT + "\nYou give sharp business advice, marketing copy, and strategy.")

personal_agent = Agent("PERSONAL",
    BASE_PROMPT + "\nYou give personal advice, motivation, astrology insights. Be warm and wise.")

live_agent = Agent("LIVE",
    BASE_PROMPT + "\nYou fetch live data: weather, scores, stocks, crypto prices.",
    use_search=True)

creative_agent = Agent("CREATIVE",
    BASE_PROMPT + "\nYou write viral content: jokes, roasts, captions, scripts, poems. Be witty.")

health_agent = Agent("HEALTH",
    BASE_PROMPT + "\nYou give health, fitness, food, and wellness advice. Be practical.")

finance_agent = Agent("FINANCE",
    BASE_PROMPT + "\nYou give financial advice, track spending, convert currency.",
    use_search=True)

master_agent = Agent("MASTER",
    """Route queries to the right agent. Reply ONLY with JSON: {"agent":"name","query":"text"}
Agents: research, business, personal, live, creative, health, finance
- research: facts, explanations, who/what/why/how questions
- business: strategy, marketing, copy writing
- personal: advice, motivation, astrology, feelings
- live: weather, scores, stocks, crypto, current prices
- creative: jokes, roasts, poems, captions, scripts
- health: food, fitness, sleep, wellness
- finance: money, spending, currency, investment""")

AGENTS = {
    "research": research_agent,
    "business": business_agent,
    "personal": personal_agent,
    "live":     live_agent,
    "creative": creative_agent,
    "health":   health_agent,
    "finance":  finance_agent,
}

# ── FAST ROUTING ──────────────────────────────────────────────────
FAST_ROUTES = {
    # Live data
    "weather":"live","temperature":"live","degrees":"live","forecast":"live",
    "score":"live","match":"live","game":"live","result":"live",
    "bitcoin":"live","btc":"live","stock":"live","crypto":"live","price":"live",
    "market":"live","eth":"live","ethereum":"live","news":"live","headline":"live",
    "breaking":"live","latest":"live","trending":"live",
    # Business
    "marketing":"business","strategy":"business","investor":"business",
    "startup":"business","revenue":"business","pricing":"business",
    "competitor":"business","pitch":"business",
    # Creative
    "joke":"creative","roast":"creative","poem":"creative","rap":"creative",
    "write":"creative","draft":"creative","caption":"creative","post":"creative",
    "tweet":"creative","instagram":"creative","funny":"creative","story":"creative",
    "script":"creative","lyrics":"creative","viral":"creative",
    # Health
    "eat":"health","food":"health","sleep":"health","tired":"health",
    "workout":"health","exercise":"health","diet":"health","calories":"health",
    "nutrition":"health","healthy":"health","sick":"health",
    # Finance
    "spent":"finance","spend":"finance","money":"finance","budget":"finance",
    "npr":"finance","usd":"finance","convert":"finance","exchange":"finance",
    "invest":"finance","salary":"finance",
    # Personal
    "motivate":"personal","motivation":"personal","feeling":"personal",
    "sad":"personal","stress":"personal","advice":"personal",
    "astrology":"personal","numerology":"personal","zodiac":"personal",
    # Research
    "explain":"research","what is":"research","who is":"research",
    "history":"research","summarize":"research","how does":"research",
    "why does":"research","tell me about":"research","compare":"research",
}

last_response = ""

def route_fast(text):
    low = text.lower()
    for keyword, agent in FAST_ROUTES.items():
        if keyword in low:
            return agent
    return None

def route_master(text):
    try:
        resp = master_agent.ask(text, max_tokens=50)
        data = json.loads(re.search(r'\{.*\}', resp, re.DOTALL).group())
        return data.get("agent","research"), data.get("query",text)
    except:
        return "research", text

def dispatch(text):
    global last_response
    low = text.lower().strip()

    # Special commands
    if "what did i say" in low or "repeat that" in low:
        return f"You said: {last_response}"

    if "i have an idea" in low or low.startswith("idea:"):
        idea = re.sub(r"i have an idea|idea:","",low).strip()
        brain.add_idea(idea)
        return "Idea captured sir."

    if "remember that" in low or low.startswith("remember "):
        fact = re.sub(r"^remember (that )?","",low).strip()
        brain.remember(fact)
        return "Stored in memory sir."

    if "what do you remember" in low or "what have you stored" in low:
        ctx = brain.get_context()
        return ctx if ctx else "Nothing stored yet sir."

    if "forget everything" in low or "clear memory" in low:
        brain.memory = {"facts":[],"ideas":[],"finance":[]}
        brain.save("memory.json", brain.memory)
        return "Memory cleared sir."

    spent = re.search(r"(?:i spent|spent|paid)\s+\$?(\d+(?:\.\d+)?)\s+(?:on|for)?\s*(.+)", low)
    if spent:
        brain.log_finance(float(spent.group(1)), spent.group(2).strip())
        return f"Logged ${spent.group(1)} on {spent.group(2).strip()} sir."

    if "my ideas" in low or "what ideas" in low:
        ideas = brain.ideas.get("ideas",[])
        if not ideas: return "No ideas stored yet sir."
        return "Your ideas: " + ". ".join(i["idea"] for i in ideas[-5:])

    if "give me the report on" in low or "research results" in low:
        topic = re.sub(r"give me the report on|research results on|research results","",low).strip()
        for key, val in brain.reports.items():
            if topic in key.lower():
                return f"Research on {key}: {val.get('result','')[:200]}"
        return f"No report found on {topic} sir."

    # Fast route
    agent_name = route_fast(text)
    if not agent_name:
        agent_name, text = route_master(text)

    agent = AGENTS.get(agent_name, research_agent)
    reply = agent.ask(text)
    last_response = reply
    return reply

def research_async(topic, name=None):
    name = name or topic[:20]
    def _run():
        result = research_agent.ask(
            f"Research: {topic}. Give 5 key findings with specific facts.",
            max_tokens=400
        )
        brain.reports[name] = {"topic":topic,"result":result,"time":datetime.now().isoformat()}
        brain.save("reports.json", brain.reports)
        print(f"  Research complete: {name}")
    threading.Thread(target=_run, daemon=True).start()
    return f"Research started on {topic} sir. Say give me the report on {topic} when ready."

if __name__ == "__main__":
    print("Agents loaded OK")
    print(f"Agents: {list(AGENTS.keys())}")
