import streamlit as st
from groq import Groq
from datetime import datetime
import time
import base64
import json
import os
import re
import urllib.parse
import io

st.set_page_config(page_title="VectorWare AI", page_icon="🌀", layout="centered", initial_sidebar_state="expanded")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {
    "dark_mode": True, "messages": [], "chat_histories": [],
    "pending_image": None, "user_name": None, "memory_facts": [],
    "voice_prompt": None, "mood": None, "followups": [],
    "goals": [], "tts_text": None, "lang": "en",
    "pending_doc": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

BG        = "radial-gradient(circle at top center, #150a3a 0%, #05030d 100%)" if st.session_state.dark_mode else "radial-gradient(circle at top center, #f0ebff 0%, #ffffff 100%)"
SIDEBAR_BG= "#090615" if st.session_state.dark_mode else "#f5f0ff"
TEXT      = "#f3f4f6" if st.session_state.dark_mode else "#1a1a2e"
INPUT_BG  = "#160f33" if st.session_state.dark_mode else "#ffffff"
MSG_TEXT  = "#e2e8f0" if st.session_state.dark_mode else "#1f2937"

st.markdown(f"""
<style>
/* ── Kill ALL Streamlit branding ── */
#MainMenu,footer,header,[data-testid="stToolbar"],
[data-testid="stDecoration"],[data-testid="stStatusWidget"],
[data-testid="stHeader"],.viewerBadge_container__r5tak,
.viewerBadge_link__qRIco,#stDecoration,
a[href*="streamlit.io"],img[src*="streamlit"],
[data-testid="stAppViewBlockContainer"] > div > div > div > a,
.css-1dp5vir,.e8zbici2,.css-14xtw13,.e8zbici0 {{
    display:none !important; visibility:hidden !important;
}}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
.stApp {{ font-family:'Inter',sans-serif !important; background:{BG}; color:{TEXT} !important; }}
section[data-testid="stSidebar"] {{ background:{SIDEBAR_BG} !important; border-right:1px solid rgba(147,85,255,0.2) !important; }}
section[data-testid="stSidebar"] * {{ color:{TEXT} !important; }}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] div,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] div {{ font-size:0px !important; color:transparent !important; }}
[data-testid="stChatMessageAvatarUser"] div::before {{ content:"👤"; font-size:1.2rem !important; }}
[data-testid="stChatMessageAvatarAssistant"] div::before {{ content:"🌀"; font-size:1.2rem !important; }}
[data-testid="stChatMessageContent"] p {{ color:{MSG_TEXT} !important; line-height:1.75 !important; }}
.stChatInput input {{ background-color:{INPUT_BG} !important; color:{TEXT} !important; border:1px solid rgba(147,85,255,0.3) !important; border-radius:24px !important; padding:12px 20px !important; }}
.stButton button {{ background:rgba(147,85,255,0.1) !important; color:{TEXT} !important; border:1px solid rgba(147,85,255,0.25) !important; border-radius:12px !important; transition:all 0.2s !important; }}
.stButton button:hover {{ background:rgba(147,85,255,0.25) !important; }}
[data-testid="stFileUploader"] {{ background:transparent !important; border:none !important; padding:0 !important; }}
[data-testid="stFileUploader"] label {{ display:none !important; }}
[data-testid="stFileUploader"] section > div {{ padding:0 !important; }}
@keyframes spiralGlow {{ 0%,100% {{ filter:drop-shadow(0 0 6px #9b59ff); }} 50% {{ filter:drop-shadow(0 0 16px #00d4ff); }} }}
@keyframes spiralSpin {{ 0% {{ transform:rotate(0deg); }} 100% {{ transform:rotate(360deg); }} }}
.spiral-idle {{ animation:spiralGlow 4s ease-in-out infinite; display:inline-block; }}
.spiral-thinking {{ animation:spiralSpin 1.2s linear infinite,spiralGlow 1.5s ease-in-out infinite; display:inline-block; }}
.greeting {{ font-size:2.2rem; font-weight:300; color:{TEXT} !important; margin:0; }}
.greeting-sub {{ font-size:2.2rem; font-weight:600; background:linear-gradient(90deg,#9b59ff,#bf00ff,#00d4ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0 0 10px 0; }}
.name-card {{ background:rgba(147,85,255,0.06); border:1px solid rgba(147,85,255,0.25); border-radius:20px; padding:28px 22px; margin:20px 0; text-align:center; }}
.history-label {{ color:#6b7280; font-size:0.68rem; font-weight:700; letter-spacing:0.08em; margin:12px 0 4px 0; }}
.name-badge {{ background:rgba(147,85,255,0.12); border:1px solid rgba(147,85,255,0.25); border-radius:10px; padding:7px 12px; margin-bottom:10px; font-size:0.8rem; color:#d8b4fe; text-align:center; }}
.founder-tag {{ background:rgba(147,85,255,0.15); border-radius:8px; padding:6px 10px; margin:5px 0; font-size:0.8rem; color:#d8b4fe !important; display:block; }}
.about-section {{ background:rgba(147,85,255,0.06); border:1px solid rgba(147,85,255,0.2); border-radius:14px; padding:14px; margin-top:15px; }}
.thinking-box {{ background:rgba(147,85,255,0.06); border:1px solid rgba(147,85,255,0.2); border-radius:12px; padding:10px 14px; margin-bottom:10px; font-size:0.82rem; color:#a78bfa; }}
.memory-pill {{ display:inline-flex; align-items:center; gap:5px; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.2); border-radius:20px; padding:3px 10px; font-size:0.72rem; color:#00d4ff; margin:2px; }}
.img-preview-pill {{ display:inline-flex; align-items:center; gap:6px; background:rgba(147,85,255,0.15); border:1px solid rgba(147,85,255,0.3); border-radius:20px; padding:4px 10px; font-size:0.78rem; color:#d8b4fe; margin-bottom:8px; }}
.search-pill {{ display:inline-flex; align-items:center; gap:5px; background:rgba(147,85,255,0.08); border:1px solid rgba(147,85,255,0.2); border-radius:20px; padding:3px 10px; font-size:0.72rem; color:#c084fc; margin-bottom:8px; }}
.followup-chip {{ display:inline-block; background:rgba(147,85,255,0.1); border:1px solid rgba(147,85,255,0.3); border-radius:20px; padding:5px 14px; font-size:0.78rem; color:#d8b4fe; margin:3px; cursor:pointer; transition:all 0.2s; }}
.followup-chip:hover {{ background:rgba(147,85,255,0.25); }}
.goal-card {{ background:rgba(0,212,255,0.05); border:1px solid rgba(0,212,255,0.2); border-radius:12px; padding:10px 14px; margin:5px 0; font-size:0.8rem; color:#e2e8f0; }}
.goal-step {{ color:#a78bfa; font-size:0.75rem; margin:2px 0; }}
.lang-badge {{ background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.25); border-radius:8px; padding:3px 10px; font-size:0.72rem; color:#00d4ff; display:inline-block; margin-bottom:6px; }}
.sug-btn {{ width:100%; text-align:left; background:rgba(147,85,255,0.07); border:1px solid rgba(147,85,255,0.2); border-radius:12px; padding:10px 14px; font-size:0.85rem; color:{TEXT}; margin-bottom:6px; cursor:pointer; }}
/* Mobile-first suggestion grid */
@media (max-width:640px) {{
    .greeting {{ font-size:1.7rem; }}
    .greeting-sub {{ font-size:1.7rem; }}
}}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
MEMORY_FILE = "vectorware_memory.json"
GOALS_FILE  = "vectorware_goals.json"
SPIRAL_SVG  = """<svg width="{size}" height="{size}" viewBox="0 0 200 200">
<defs><linearGradient id="sg{id}" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#bf00ff"/><stop offset="100%" style="stop-color:#7b2fff"/>
</linearGradient></defs>
<path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 C90,165 50,140 40,100 C25,50 60,15 100,15 C150,15 185,55 185,100 C185,155 140,190 90,185"
fill="none" stroke="url(#sg{id})" stroke-width="18" stroke-linecap="round"/></svg>"""

MOODS = {
    "🧠 Focused":      "Be concise, analytical and direct. No fluff.",
    "😄 Casual":       "Be warm, friendly and conversational. Light humour welcome.",
    "🚀 Hype":         "Be energetic, bold and motivational. Big vision energy.",
    "🧘 Calm":         "Be gentle, measured and thoughtful. Steady tone.",
    "💼 Professional": "Be formal, precise and business-ready.",
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_memory(name):
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE) as f:
                return json.load(f).get(name, {}).get("facts", [])
        except: pass
    return []

def save_memory(name, facts):
    data = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE) as f: data = json.load(f)
        except: pass
    data[name] = {"facts": facts, "updated": datetime.now().isoformat()}
    with open(MEMORY_FILE, "w") as f: json.dump(data, f, indent=2)

def load_goals(name):
    if os.path.exists(GOALS_FILE):
        try:
            with open(GOALS_FILE) as f:
                return json.load(f).get(name, [])
        except: pass
    return []

def save_goals(name, goals):
    data = {}
    if os.path.exists(GOALS_FILE):
        try:
            with open(GOALS_FILE) as f: data = json.load(f)
        except: pass
    data[name] = goals
    with open(GOALS_FILE, "w") as f: json.dump(data, f, indent=2)

def extract_facts(text):
    facts = []
    for pat in [
        r"I(?:'m| am) (?:a |an )?(.+?)(?:\.|,|$)",
        r"I work (?:as |in |at )(.+?)(?:\.|,|$)",
        r"I(?:'m| am) from (.+?)(?:\.|,|$)",
        r"my (?:company|business|startup) (?:is |called )?(.+?)(?:\.|,|$)",
    ]:
        for m in re.findall(pat, text, re.IGNORECASE):
            f = m.strip()
            if 3 < len(f) < 80: facts.append(f)
    return facts

def encode_image(uploaded_file):
    data = uploaded_file.read()
    return base64.b64encode(data).decode(), uploaded_file.type

def get_time_greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"

def group_histories(histories):
    now = datetime.now()
    today, yesterday, this_week, older = [], [], [], []
    for c in histories:
        d = (now - c.get("date", now)).days
        if d == 0: today.append(c)
        elif d == 1: yesterday.append(c)
        elif d <= 7: this_week.append(c)
        else: older.append(c)
    return today, yesterday, this_week, older

def web_search(query):
    try:
        from tavily import TavilyClient
        r = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"]).search(query=query, max_results=3)
        if r and r.get("results"):
            return "\n".join(f"- {x['title']}: {x['content'][:200]}" for x in r["results"][:3])
    except: pass
    return None

def needs_search(p):
    return any(k in p.lower() for k in ["latest","today","current","news","price","weather","right now",
        "trending","update","live","score","stock","crypto","bitcoin","2025","2026","recently","just happened"])

def generate_image(prompt):
    enc = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{enc}?width=768&height=512&nologo=true"

def is_image_request(p):
    return any(k in p.lower() for k in ["generate image","draw","create image","show me a picture",
        "make an image","imagine","paint","illustrate","render","visualize","picture of","image of",
        "generate a picture","create a picture","sketch"])

def is_csv_analysis(p):
    return any(k in p.lower() for k in ["analyze","analyse","chart","graph","visualize","insights",
        "data","csv","spreadsheet","column","rows","trend"])

def detect_language(text):
    """Simple heuristic; Groq does the real work via system prompt."""
    return "en"

def is_goal_request(p):
    return any(k in p.lower() for k in ["my goal","set a goal","i want to achieve","help me achieve",
        "track my goal","goal is to","i want to","i plan to","my target"])

def is_doc_summary(p):
    return any(k in p.lower() for k in ["summarize","summarise","summary","what does this document",
        "what is this pdf","read this","explain this document","analyse this file"])

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def call_groq(system, user_text, max_tokens=1200):
    r = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"system","content":system},{"role":"user","content":user_text}],
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()

def get_followups(last_response, user_name):
    try:
        raw = call_groq(
            "You generate exactly 3 short follow-up question suggestions (max 8 words each) "
            "based on an AI response. Return ONLY a JSON array of 3 strings, no extra text.",
            f"AI just said: {last_response[:400]}"
        )
        raw = raw.strip()
        if raw.startswith("```"): raw = re.sub(r"```[a-z]*", "", raw).replace("```","").strip()
        return json.loads(raw)[:3]
    except:
        return []

def summarize_document(text_content, user_name):
    return call_groq(
        f"You are VectorWare AI. Summarize documents clearly for {user_name}. "
        "Give: 1) 3-sentence overview 2) Key bullet points 3) Action items if any.",
        f"Document content:\n{text_content[:6000]}"
    )

def build_goal_plan(goal_text, user_name):
    try:
        raw = call_groq(
            "You create structured goal plans. Return ONLY a JSON object with keys: "
            "'goal' (string), 'steps' (array of 5 short strings), 'timeline' (string). No extra text.",
            f"User goal: {goal_text}"
        )
        raw = raw.strip()
        if raw.startswith("```"): raw = re.sub(r"```[a-z]*","",raw).replace("```","").strip()
        return json.loads(raw)
    except:
        return None

# ── NAME ONBOARDING ───────────────────────────────────────────────────────────
if st.session_state.user_name is None:
    st.markdown(f"<div style='text-align:center;padding:40px 0 10px 0;'><div class='spiral-idle'>{SPIRAL_SVG.format(size=60,id='intro')}</div></div>", unsafe_allow_html=True)
    st.markdown(f"""<div class='name-card'>
    <p style='font-size:1.6rem;font-weight:300;color:{TEXT};margin:0;'>Welcome to</p>
    <p style='font-size:1.8rem;font-weight:700;background:linear-gradient(90deg,#9b59ff,#bf00ff,#00d4ff);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 8px 0;'>VectorWare AI</p>
    <p style='color:#9ca3af;font-size:0.95rem;margin:0 0 24px 0;'>Next-generation AI — before we begin, what is your name?</p>
    </div>""", unsafe_allow_html=True)
    _, c2, _ = st.columns([0.15, 0.7, 0.15])
    with c2:
        name_input = st.text_input("name", placeholder="Enter your name…", label_visibility="collapsed", key="name_field")
        if st.button("Let's Go", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name   = name_input.strip()
                st.session_state.memory_facts = load_memory(name_input.strip())
                st.session_state.goals        = load_goals(name_input.strip())
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='text-align:center;padding:20px 0 10px 0;'><div class='spiral-idle'>{SPIRAL_SVG.format(size=38,id='sb')}</div><p style='font-size:1rem;color:#fff;margin:8px 0 0 0;font-weight:500;'>VectorWare AI</p></div>", unsafe_allow_html=True)

    mode_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown(f"<div class='name-badge'>👤 {st.session_state.user_name}</div>", unsafe_allow_html=True)
    if st.button("✨ New Chat", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.pending_image = None
        st.session_state.followups     = []
        st.session_state.pending_doc   = None
        st.rerun()
    if st.button("🔄 Change Name", use_container_width=True):
        for k in ["user_name","messages","memory_facts","goals","followups","pending_doc"]:
            st.session_state[k] = [] if k in ["messages","memory_facts","goals","followups"] else None
        st.rerun()

    # Mood selector
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p class='history-label'>AI TONE</p>", unsafe_allow_html=True)
    for ml in MOODS:
        active = st.session_state.mood == ml
        if st.button(ml, key=f"mood_{ml}", use_container_width=True):
            st.session_state.mood = None if active else ml
            st.rerun()

    # Goals tracker
    if st.session_state.goals:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='history-label'>🎯 MY GOALS</p>", unsafe_allow_html=True)
        for g in st.session_state.goals[:3]:
            st.markdown(f"<div class='goal-card'><b>{g.get('goal','')[:35]}</b><br>"
                        + "".join(f"<div class='goal-step'>• {s}</div>" for s in g.get('steps',[])[:3])
                        + f"<div style='color:#6b7280;font-size:0.7rem;margin-top:4px;'>⏱ {g.get('timeline','')}</div></div>",
                        unsafe_allow_html=True)

    # Memory
    if st.session_state.memory_facts:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='history-label'>WHAT I REMEMBER</p>", unsafe_allow_html=True)
        for f in st.session_state.memory_facts[:5]:
            st.markdown(f"<span class='memory-pill'>• {f[:40]}</span>", unsafe_allow_html=True)

    # History
    st.markdown("<br>", unsafe_allow_html=True)
    today, yesterday, this_week, older = group_histories(st.session_state.chat_histories)
    def render_section(label, chats, offset=0):
        if chats:
            st.markdown(f"<p class='history-label'>{label}</p>", unsafe_allow_html=True)
            for i, chat in enumerate(chats[:5]):
                if st.button(f"  {chat['title']}", key=f"h_{label}_{offset}_{i}", use_container_width=True):
                    st.session_state.messages  = chat["messages"]
                    st.session_state.followups = []
                    st.rerun()
    if not st.session_state.chat_histories:
        st.markdown("<p style='color:#4b5563;font-size:0.8rem;'>No conversations yet</p>", unsafe_allow_html=True)
    else:
        render_section("TODAY", today, 0)
        render_section("YESTERDAY", yesterday, 10)
        render_section("THIS WEEK", this_week, 20)
        render_section("OLDER", older, 30)

    st.markdown("""<div style='margin-top:12px;padding:8px 12px;background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.2);border-radius:10px;'>
    <p style='color:#00d4ff;font-size:0.7rem;font-weight:600;margin:0 0 2px 0;'>ACTIVE MODEL</p>
    <p style='color:#e5e7eb;font-size:0.75rem;margin:0;'>Llama 4 Scout 17B</p>
    <p style='color:#6b7280;font-size:0.65rem;margin:2px 0 0 0;'>Vision · Search · Memory · Image Gen · TTS · Goals</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class='about-section'>
    <p style='color:#9b59ff;font-size:0.82rem;font-weight:600;margin:0 0 6px 0;'>Corporate Engine</p>
    <p style='color:#9ca3af;font-size:0.75rem;line-height:1.5;margin:0 0 10px 0;'>Next-generation AI architecture delivering high-throughput autonomous enterprise capabilities globally.</p>
    <p style='color:#6b7280;font-size:0.7rem;font-weight:600;margin:0 0 4px 0;'>FOUNDERS</p>
    <span class='founder-tag'>Samuel Frimpong</span>
    <span class='founder-tag'>Cardinal Kofi Nsiah</span>
    <span class='founder-tag'>Gabriel Ahwireng</span>
    <span class='founder-tag'>Gideon Ahwireng</span>
    <p style='color:#4b5563;font-size:0.65rem;text-align:center;margin:12px 0 0 0;'>© 2026 VectorWare Inc.</p>
    </div>""", unsafe_allow_html=True)

# ── WELCOME DASHBOARD (mobile-safe single column) ─────────────────────────────
if not st.session_state.messages:
    greeting = get_time_greeting()
    st.markdown(f"""<div style='padding:30px 0 16px 0;'>
    <div class='spiral-idle' style='display:block;margin-bottom:12px;'>{SPIRAL_SVG.format(size=50,id='main')}</div>
    <p class='greeting'>{greeting},</p>
    <p class='greeting-sub'>{st.session_state.user_name}</p>
    <p style='color:#9ca3af;font-size:0.9rem;margin-top:0;'>How can I help you today?</p>
    </div>""", unsafe_allow_html=True)

    suggestions = [
        "🌐 Design a website for my business",
        "📈 Explain forex trading strategies",
        "🤖 What can AI automation do for my company",
        "📝 Write an executive pitch proposal",
        "🎯 Help me set and track a business goal",
        "🖼️ Generate an image of a futuristic city",
    ]
    # Single column on mobile — no st.columns here
    for idx, text in enumerate(suggestions):
        if st.button(text, key=f"sug_{idx}", use_container_width=True):
            st.session_state.messages.append({"role":"user","content":text})
            st.rerun()

# ── RENDER CHAT HISTORY ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            if isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if block["type"] == "text": st.write(block["text"])
                    elif block["type"] == "image_url":
                        st.image(base64.b64decode(block["image_url"]["url"].split(",")[1]), width=260)
            else:
                st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            c = msg["content"]
            if isinstance(c, dict):
                if c.get("type") == "image_gen":
                    st.image(c["url"], caption=c.get("caption",""))
                    st.write(c.get("text",""))
                elif c.get("type") == "goal":
                    st.write(c.get("text",""))
                    st.markdown(f"<div class='goal-card'><b>🎯 {c['plan']['goal']}</b><br>"
                                + "".join(f"<div class='goal-step'>• {s}</div>" for s in c['plan']['steps'])
                                + f"<div style='color:#6b7280;font-size:0.7rem;margin-top:4px;'>⏱ {c['plan']['timeline']}</div></div>",
                                unsafe_allow_html=True)
                else:
                    st.write(str(c))
            else:
                st.write(c)

# ── FOLLOW-UP CHIPS ───────────────────────────────────────────────────────────
if st.session_state.followups:
    st.markdown("<div style='margin:8px 0 4px 0;'>", unsafe_allow_html=True)
    cols = st.columns(len(st.session_state.followups))
    for i, chip in enumerate(st.session_state.followups):
        with cols[i]:
            if st.button(chip, key=f"chip_{i}_{chip[:10]}", use_container_width=True):
                st.session_state.messages.append({"role":"user","content":chip})
                st.session_state.followups = []
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── INPUT ROW ─────────────────────────────────────────────────────────────────
col_input, col_mic, col_upload, col_doc = st.columns([0.73, 0.09, 0.09, 0.09])

prompt = None
with col_input:
    prompt = st.chat_input(f"Ask VectorWare anything, {st.session_state.user_name}…")

with col_mic:
    try:
        from streamlit_mic_recorder import mic_recorder
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", just_once=True,
                             use_container_width=False, key="mic")
        if audio:
            ab = io.BytesIO(audio["bytes"])
            ab.name = "audio.wav"
            with st.spinner(""):
                tr = client.audio.transcriptions.create(model="whisper-large-v3", file=ab)
            if tr.text:
                st.session_state.voice_prompt = tr.text
                st.rerun()
    except:
        st.markdown("🎤", unsafe_allow_html=True)

with col_upload:
    uploaded_img = st.file_uploader("img", type=["png","jpg","jpeg","gif","webp"],
                                    label_visibility="collapsed", key="image_uploader")

with col_doc:
    uploaded_doc = st.file_uploader("doc", type=["txt","pdf","csv"],
                                    label_visibility="collapsed", key="doc_uploader")

# Handle image attachment
if uploaded_img is not None:
    b64, mime = encode_image(uploaded_img)
    st.session_state.pending_image = {"base64": b64, "mime_type": mime, "name": uploaded_img.name}
    st.markdown(f"<div class='img-preview-pill'>📎 {uploaded_img.name}</div>", unsafe_allow_html=True)

# Handle doc attachment
if uploaded_doc is not None:
    raw_bytes = uploaded_doc.read()
    try:
        if uploaded_doc.name.endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                    doc_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            except:
                doc_text = raw_bytes.decode("utf-8", errors="ignore")
        elif uploaded_doc.name.endswith(".csv"):
            import csv
            decoded = raw_bytes.decode("utf-8", errors="ignore")
            doc_text = decoded[:5000]
        else:
            doc_text = raw_bytes.decode("utf-8", errors="ignore")
        st.session_state.pending_doc = {"name": uploaded_doc.name, "text": doc_text}
        st.markdown(f"<div class='img-preview-pill'>📄 {uploaded_doc.name} attached</div>", unsafe_allow_html=True)
    except:
        st.warning("Could not read that file.")

if st.session_state.voice_prompt:
    prompt = st.session_state.voice_prompt
    st.session_state.voice_prompt = None

# ── PROCESS MESSAGE ───────────────────────────────────────────────────────────
if prompt:
    # Build user content
    if st.session_state.pending_image:
        img = st.session_state.pending_image
        user_content = [
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":{"url":f"data:{img['mime_type']};base64,{img['base64']}"}}
        ]
        with st.chat_message("user"):
            st.write(prompt)
            st.image(base64.b64decode(img["base64"]), width=260)
        st.session_state.messages.append({"role":"user","content":user_content})
        st.session_state.pending_image = None
    else:
        st.session_state.messages.append({"role":"user","content":prompt})
        st.chat_message("user").write(prompt)

    # Memory extraction
    new_facts = extract_facts(prompt)
    if new_facts:
        for f in new_facts:
            if f not in st.session_state.memory_facts:
                st.session_state.memory_facts.append(f)
        save_memory(st.session_state.user_name, st.session_state.memory_facts)

    st.session_state.followups = []

    # ── DOCUMENT SUMMARY ─────────────────────────────────────────────────
    if st.session_state.pending_doc and (is_doc_summary(prompt) or True):
        doc = st.session_state.pending_doc
        thinking_ph = st.empty()
        loader_ph   = st.empty()
        thinking_ph.markdown(f"<div class='thinking-box'>📄 Reading {doc['name']}…</div>", unsafe_allow_html=True)
        loader_ph.markdown(f"""<div style='display:flex;align-items:center;gap:12px;padding:8px 0;'>
            <div class='spiral-thinking'>{SPIRAL_SVG.format(size=28,id='load')}</div>
            <p style='color:#9b59ff;margin:0;font-size:0.9rem;'>VectorWare is reading your document…</p>
        </div>""", unsafe_allow_html=True)

        if doc["name"].endswith(".csv"):
            # Data analysis path
            system = (f"You are VectorWare AI, a data analyst. The user is {st.session_state.user_name}. "
                      f"Analyze this CSV data and give: key stats, trends, 3 business insights, and recommendations.")
            resp = call_groq(system, f"CSV data:\n{doc['text']}\n\nUser question: {prompt}", max_tokens=1400)
        else:
            resp = summarize_document(doc["text"], st.session_state.user_name)

        thinking_ph.empty(); loader_ph.empty()
        with st.chat_message("assistant"):
            ph = st.empty()
            shown = ""
            for char in resp:
                shown += char
                ph.markdown(shown + "▌")
                time.sleep(0.004)
            ph.markdown(shown)

        st.session_state.messages.append({"role":"assistant","content":resp})
        st.session_state.pending_doc = None
        st.session_state.followups   = get_followups(resp, st.session_state.user_name)

        if len(st.session_state.messages) == 2:
            title = prompt[:26] + "..."
            st.session_state.chat_histories.insert(0, {"title":title,"messages":list(st.session_state.messages),"time":datetime.now().strftime("%H:%M"),"date":datetime.now()})
        st.rerun()

    # ── IMAGE GENERATION ─────────────────────────────────────────────────
    if is_image_request(prompt):
        thinking_ph = st.empty()
        loader_ph   = st.empty()
        thinking_ph.markdown("<div class='thinking-box'>🎨 Generating your image…</div>", unsafe_allow_html=True)
        loader_ph.markdown(f"""<div style='display:flex;align-items:center;gap:12px;padding:8px 0;'>
            <div class='spiral-thinking'>{SPIRAL_SVG.format(size=28,id='load')}</div>
            <p style='color:#9b59ff;margin:0;font-size:0.9rem;'>VectorWare is painting…</p>
        </div>""", unsafe_allow_html=True)

        image_url   = generate_image(prompt)
        time.sleep(1.0)
        thinking_ph.empty(); loader_ph.empty()

        caption  = f"Generated: {prompt}"
        reply_tx = f"Here's your image, {st.session_state.user_name}! Rendered from your description."
        with st.chat_message("assistant"):
            st.image(image_url, caption=caption)
            st.write(reply_tx)

        st.session_state.messages.append({"role":"assistant","content":{"type":"image_gen","url":image_url,"caption":caption,"text":reply_tx}})
        if len(st.session_state.messages) == 2:
            title = prompt[:26] + "..."
            st.session_state.chat_histories.insert(0, {"title":title,"messages":list(st.session_state.messages),"time":datetime.now().strftime("%H:%M"),"date":datetime.now()})
        st.rerun()

    # ── GOAL TRACKER ─────────────────────────────────────────────────────
    if is_goal_request(prompt):
        thinking_ph = st.empty()
        loader_ph   = st.empty()
        thinking_ph.markdown("<div class='thinking-box'>🎯 Building your goal plan…</div>", unsafe_allow_html=True)
        loader_ph.markdown(f"""<div style='display:flex;align-items:center;gap:12px;padding:8px 0;'>
            <div class='spiral-thinking'>{SPIRAL_SVG.format(size=28,id='load')}</div>
            <p style='color:#9b59ff;margin:0;font-size:0.9rem;'>VectorWare is planning…</p>
        </div>""", unsafe_allow_html=True)

        plan = build_goal_plan(prompt, st.session_state.user_name)
        thinking_ph.empty(); loader_ph.empty()

        if plan:
            st.session_state.goals.append(plan)
            save_goals(st.session_state.user_name, st.session_state.goals)
            reply_tx = f"Done, {st.session_state.user_name}! I've set up your goal plan and saved it to your sidebar."
            with st.chat_message("assistant"):
                st.write(reply_tx)
                st.markdown(f"<div class='goal-card'><b>🎯 {plan['goal']}</b><br>"
                            + "".join(f"<div class='goal-step'>• {s}</div>" for s in plan['steps'])
                            + f"<div style='color:#6b7280;font-size:0.7rem;margin-top:4px;'>⏱ {plan['timeline']}</div></div>",
                            unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":{"type":"goal","plan":plan,"text":reply_tx}})
            if len(st.session_state.messages) == 2:
                title = prompt[:26] + "..."
                st.session_state.chat_histories.insert(0, {"title":title,"messages":list(st.session_state.messages),"time":datetime.now().strftime("%H:%M"),"date":datetime.now()})
            st.rerun()

    # ── NORMAL CHAT ───────────────────────────────────────────────────────
    search_context = ""; search_used = False
    if needs_search(prompt):
        with st.spinner("🔍 Searching…"):
            r = web_search(prompt)
            if r:
                search_context = f"\n\nLive web search results:\n{r}"
                search_used    = True

    thinking_steps = []
    if search_used:   thinking_steps.append("Searched the web")
    if new_facts:     thinking_steps.append(f"Remembered: {', '.join(new_facts[:2])}")
    if st.session_state.mood: thinking_steps.append(f"Tone: {st.session_state.mood}")
    thinking_steps.append("Generating response…")
    thinking_ph = st.empty()
    thinking_ph.markdown("<div class='thinking-box'>" + " | ".join(thinking_steps) + "</div>", unsafe_allow_html=True)
    if search_used:
        st.markdown("<span class='search-pill'>🔍 Includes live web data</span>", unsafe_allow_html=True)

    loader_ph = st.empty()
    loader_ph.markdown(f"""<div style='display:flex;align-items:center;gap:12px;padding:8px 0;'>
        <div class='spiral-thinking'>{SPIRAL_SVG.format(size=28,id='load')}</div>
        <p style='color:#9b59ff;margin:0;font-size:0.9rem;font-weight:500;'>VectorWare is thinking…</p>
    </div>""", unsafe_allow_html=True)

    memory_ctx = ""
    if st.session_state.memory_facts:
        memory_ctx = f"\n\nWhat you know about {st.session_state.user_name}: {', '.join(st.session_state.memory_facts)}"

    mood_instruction = ""
    if st.session_state.mood and st.session_state.mood in MOODS:
        mood_instruction = f"\n\nTone instruction: {MOODS[st.session_state.mood]}"

    lang_instruction = ("\n\nIMPORTANT: Detect the language the user is writing in and always reply "
                        "in that same language naturally.")

    system_prompt = (
        f"You are VectorWare AI, a highly intelligent, professional and friendly AI assistant "
        f"built by VectorWare Inc. The user's name is {st.session_state.user_name}. "
        f"Address them by name naturally where it feels right. Be concise, insightful, and professional."
        f"{memory_ctx}{search_context}{mood_instruction}{lang_instruction}"
    )

    api_messages = [{"role":"system","content":system_prompt}]
    for m in st.session_state.messages:
        c = m["content"]
        if isinstance(c, dict): c = c.get("text","")
        if isinstance(c, list):
            api_messages.append({"role":m["role"],"content":c})
        else:
            api_messages.append({"role":m["role"],"content":c})

    stream = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=api_messages,
        max_tokens=2048,
        stream=True
    )

    thinking_ph.empty(); loader_ph.empty()

    with st.chat_message("assistant"):
        ph = st.empty()
        full_response = ""
        for chunk in stream:
            c = chunk.choices[0].delta.content
            if c:
                for char in c:
                    full_response += char
                    ph.markdown(full_response + "▌")
                    time.sleep(0.005)
        ph.markdown(full_response)

    st.session_state.messages.append({"role":"assistant","content":full_response})

    # Generate follow-up chips
    st.session_state.followups = get_followups(full_response, st.session_state.user_name)

    # TTS — play response aloud via Groq
    try:
        tts_resp = client.audio.speech.create(
            model="playai-tts",
            voice="Celeste-PlayAI",
            input=full_response[:500],
        )
        audio_bytes = tts_resp.content
        audio_b64   = base64.b64encode(audio_bytes).decode()
        st.markdown(
            f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )
    except:
        pass  # TTS optional — silently skip if model not available

    if len(st.session_state.messages) == 2:
        title = prompt[:26] + "..." if len(prompt) > 26 else prompt
        st.session_state.chat_histories.insert(0, {
            "title": title, "messages": list(st.session_state.messages),
            "time": datetime.now().strftime("%H:%M"), "date": datetime.now()
        })
    st.rerun()
