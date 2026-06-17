import streamlit as st
from groq import Groq
from datetime import datetime
import time
import base64
import json
import os
import re
import urllib.parse

st.set_page_config(page_title=“VectorWare AI”, page_icon=“🌀”, layout=“centered”, initial_sidebar_state=“expanded”)

if “dark_mode” not in st.session_state:
st.session_state.dark_mode = True
if “messages” not in st.session_state:
st.session_state.messages = []
if “chat_histories” not in st.session_state:
st.session_state.chat_histories = []
if “pending_image” not in st.session_state:
st.session_state.pending_image = None
if “user_name” not in st.session_state:
st.session_state.user_name = None
if “memory_facts” not in st.session_state:
st.session_state.memory_facts = []
if “voice_prompt” not in st.session_state:
st.session_state.voice_prompt = None
if “mood” not in st.session_state:
st.session_state.mood = None

BG = “radial-gradient(circle at top center, #150a3a 0%, #05030d 100%)” if st.session_state.dark_mode else “radial-gradient(circle at top center, #f0ebff 0%, #ffffff 100%)”
SIDEBAR_BG = “#090615” if st.session_state.dark_mode else “#f5f0ff”
TEXT = “#f3f4f6” if st.session_state.dark_mode else “#1a1a2e”
INPUT_BG = “#160f33” if st.session_state.dark_mode else “#ffffff”
MSG_TEXT = “#e2e8f0” if st.session_state.dark_mode else “#1f2937”

st.markdown(f”””

<style>
#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}
header {{visibility: hidden !important;}}
[data-testid="stToolbar"] {{display: none !important;}}
[data-testid="stDecoration"] {{display: none !important;}}
[data-testid="stStatusWidget"] {{display: none !important;}}
[data-testid="stHeader"] {{display: none !important;}}
.viewerBadge_container__r5tak {{display: none !important;}}
.viewerBadge_link__qRIco {{display: none !important;}}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
.stApp {{ font-family: 'Inter', sans-serif !important; background: {BG}; color: {TEXT} !important; }}
section[data-testid="stSidebar"] {{ background: {SIDEBAR_BG} !important; border-right: 1px solid rgba(147,85,255,0.2) !important; }}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] div,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] div {{ font-size: 0px !important; color: transparent !important; }}
[data-testid="stChatMessageAvatarUser"] div::before {{ content: "👤"; font-size: 1.2rem !important; }}
[data-testid="stChatMessageAvatarAssistant"] div::before {{ content: "🌀"; font-size: 1.2rem !important; }}
[data-testid="stChatMessageContent"] p {{ color: {MSG_TEXT} !important; line-height: 1.75 !important; }}
.stChatInput input {{ background-color: {INPUT_BG} !important; color: {TEXT} !important; border: 1px solid rgba(147,85,255,0.3) !important; border-radius: 24px !important; padding: 12px 20px !important; }}
.stButton button {{ background: rgba(147,85,255,0.1) !important; color: {TEXT} !important; border: 1px solid rgba(147,85,255,0.25) !important; border-radius: 12px !important; transition: all 0.2s !important; }}
.stButton button:hover {{ background: rgba(147,85,255,0.25) !important; }}

/* Icon buttons for mic and upload */
.icon-btn button {{
    background: rgba(147,85,255,0.12) !important;
    border: 1px solid rgba(147,85,255,0.3) !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: unset !important;
    transition: all 0.2s !important;
}}
.icon-btn button:hover {{
    background: rgba(147,85,255,0.3) !important;
    transform: scale(1.08) !important;
}}

[data-testid="stFileUploader"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}
[data-testfile="stFileUploader"] section {{ background: transparent !important; border: none !important; padding: 0 !important; }}
[data-testid="stFileUploader"] label {{ display: none !important; }}
[data-testid="stFileUploader"] section > div {{ padding: 0 !important; }}

@keyframes spiralGlow {{ 0%,100% {{ filter: drop-shadow(0 0 6px #9b59ff); }} 50% {{ filter: drop-shadow(0 0 16px #00d4ff); }} }}
@keyframes spiralSpin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
.spiral-idle {{ animation: spiralGlow 4s ease-in-out infinite; display: inline-block; }}
.spiral-thinking {{ animation: spiralSpin 1.2s linear infinite, spiralGlow 1.5s ease-in-out infinite; display: inline-block; }}
.greeting {{ font-size: 2.4rem; font-weight: 300; color: {TEXT} !important; margin: 0; }}
.greeting-sub {{ font-size: 2.4rem; font-weight: 600; background: linear-gradient(90deg,#9b59ff,#bf00ff,#00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 15px 0; }}
.name-card {{ background: rgba(147,85,255,0.06); border: 1px solid rgba(147,85,255,0.25); border-radius: 20px; padding: 32px 28px; margin: 20px 0; text-align: center; }}
.history-label {{ color: #6b7280; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; margin: 12px 0 4px 0; }}
.name-badge {{ background: rgba(147,85,255,0.12); border: 1px solid rgba(147,85,255,0.25); border-radius: 10px; padding: 7px 12px; margin-bottom: 10px; font-size: 0.8rem; color: #d8b4fe; text-align: center; }}
.founder-tag {{ background: rgba(147,85,255,0.15); border-radius: 8px; padding: 6px 10px; margin: 5px 0; font-size: 0.8rem; color: #d8b4fe !important; display: block; }}
.about-section {{ background: rgba(147,85,255,0.06); border: 1px solid rgba(147,85,255,0.2); border-radius: 14px; padding: 14px; margin-top: 15px; }}
.thinking-box {{ background: rgba(147,85,255,0.06); border: 1px solid rgba(147,85,255,0.2); border-radius: 12px; padding: 10px 14px; margin-bottom: 10px; font-size: 0.82rem; color: #a78bfa; }}
.memory-pill {{ display: inline-flex; align-items: center; gap: 5px; background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.2); border-radius: 20px; padding: 3px 10px; font-size: 0.72rem; color: #00d4ff; margin: 2px; }}
.img-preview-pill {{ display: inline-flex; align-items: center; gap: 6px; background: rgba(147,85,255,0.15); border: 1px solid rgba(147,85,255,0.3); border-radius: 20px; padding: 4px 10px; font-size: 0.78rem; color: #d8b4fe; margin-bottom: 8px; }}
.search-pill {{ display: inline-flex; align-items: center; gap: 5px; background: rgba(147,85,255,0.08); border: 1px solid rgba(147,85,255,0.2); border-radius: 20px; padding: 3px 10px; font-size: 0.72rem; color: #c084fc; margin-bottom: 8px; }}
.mood-bar {{ display: flex; gap: 8px; margin: 10px 0 16px 0; flex-wrap: wrap; }}
.mood-pill {{ background: rgba(147,85,255,0.08); border: 1px solid rgba(147,85,255,0.2); border-radius: 20px; padding: 4px 12px; font-size: 0.78rem; color: #c084fc; cursor: pointer; transition: all 0.2s; display: inline-block; }}
.mood-pill:hover {{ background: rgba(147,85,255,0.22); }}
.mood-pill.active {{ background: rgba(147,85,255,0.3); border-color: #9b59ff; color: #e9d5ff; }}
.img-gen-result {{ border: 1px solid rgba(147,85,255,0.3); border-radius: 16px; overflow: hidden; margin: 8px 0; }}
.tool-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
</style>

“””, unsafe_allow_html=True)

MEMORY_FILE = “vectorware_memory.json”

def load_memory(name):
if os.path.exists(MEMORY_FILE):
try:
with open(MEMORY_FILE, “r”) as f:
data = json.load(f)
return data.get(name, {}).get(“facts”, [])
except Exception:
pass
return []

def save_memory(name, facts):
data = {}
if os.path.exists(MEMORY_FILE):
try:
with open(MEMORY_FILE, “r”) as f:
data = json.load(f)
except Exception:
data = {}
data[name] = {“facts”: facts, “updated”: datetime.now().isoformat()}
with open(MEMORY_FILE, “w”) as f:
json.dump(data, f, indent=2)

def extract_facts(text):
facts = []
patterns = [
r”I(?:’m| am) (?:a |an )?(.+?)(?:.|,|$)”,
r”I work (?:as |in |at )(.+?)(?:.|,|$)”,
r”I(?:’m| am) from (.+?)(?:.|,|$)”,
r”my (?:company|business|startup) (?:is |called )?(.+?)(?:.|,|$)”,
]
for pattern in patterns:
for match in re.findall(pattern, text, re.IGNORECASE):
fact = match.strip()
if 3 < len(fact) < 80:
facts.append(fact)
return facts

def encode_image(uploaded_file):
bytes_data = uploaded_file.read()
b64 = base64.b64encode(bytes_data).decode(“utf-8”)
return b64, uploaded_file.type

def get_time_greeting():
hour = datetime.now().hour
if hour < 12:
return “Good morning”
elif hour < 17:
return “Good afternoon”
return “Good evening”

def group_histories(histories):
now = datetime.now()
today, yesterday, this_week, older = [], [], [], []
for chat in histories:
diff = (now - chat.get(“date”, now)).days
if diff == 0: today.append(chat)
elif diff == 1: yesterday.append(chat)
elif diff <= 7: this_week.append(chat)
else: older.append(chat)
return today, yesterday, this_week, older

def web_search(query):
try:
from tavily import TavilyClient
tavily = TavilyClient(api_key=st.secrets[“TAVILY_API_KEY”])
results = tavily.search(query=query, max_results=3)
if results and results.get(“results”):
snippets = [f”- {r[‘title’]}: {r[‘content’][:200]}” for r in results[“results”][:3]]
return “\n”.join(snippets)
except Exception:
pass
return None

def needs_search(prompt):
keywords = [“latest”,“today”,“current”,“news”,“price”,“weather”,“right now”,“trending”,“update”,“live”,“score”,“stock”,“crypto”,“bitcoin”,“2025”,“2026”,“recently”,“just happened”]
return any(kw in prompt.lower() for kw in keywords)

# ── IMAGE GENERATION ─────────────────────────────────────────────────────────

def generate_image(prompt):
encoded = urllib.parse.quote(prompt)
return f”https://image.pollinations.ai/prompt/{encoded}?width=768&height=512&nologo=true”

def is_image_request(prompt):
keywords = [“generate image”,“draw”,“create image”,“show me a picture”,“make an image”,
“imagine”,“paint”,“illustrate”,“render”,“visualize”,“picture of”,“image of”,
“generate a”,“create a picture”,“sketch”]
return any(kw in prompt.lower() for kw in keywords)

# ── MOOD TONE SYSTEM ─────────────────────────────────────────────────────────

MOODS = {
“🧠 Focused”: “Be concise, analytical and direct. No fluff.”,
“😄 Casual”: “Be warm, friendly and conversational. Light humour welcome.”,
“🚀 Hype”: “Be energetic, bold and motivational. Big vision energy.”,
“🧘 Calm”: “Be gentle, measured and thoughtful. Steady tone.”,
“💼 Professional”: “Be formal, precise and business-ready.”,
}

client = Groq(api_key=st.secrets[“GROQ_API_KEY”])

SPIRAL_SVG = “””<svg width="{size}" height="{size}" viewBox="0 0 200 200">
<defs><linearGradient id="sg{id}" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#bf00ff"/><stop offset="100%" style="stop-color:#7b2fff"/>
</linearGradient></defs>
<path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 C90,165 50,140 40,100 C25,50 60,15 100,15 C150,15 185,55 185,100 C185,155 140,190 90,185"
fill="none" stroke="url(#sg{id})" stroke-width="18" stroke-linecap="round"/>
</svg>”””

# ── NAME ONBOARDING ──────────────────────────────────────────────────────────

if st.session_state.user_name is None:
st.markdown(f”<div style='text-align:center; padding:40px 0 10px 0;'><div class='spiral-idle'>{SPIRAL_SVG.format(size=60, id=‘intro’)}</div></div>”, unsafe_allow_html=True)
st.markdown(f”””
<div class='name-card'>
<p style='font-size:1.6rem; font-weight:300; color:{TEXT}; margin:0;'>Welcome to</p>
<p style='font-size:1.8rem; font-weight:700; background:linear-gradient(90deg,#9b59ff,#bf00ff,#00d4ff);
-webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0 0 8px 0;'>VectorWare AI</p>
<p style='color:#9ca3af; font-size:0.95rem; margin:0 0 24px 0;'>Next-generation AI - before we begin, what is your name?</p>
</div>”””, unsafe_allow_html=True)
c1, c2, c3 = st.columns([0.15, 0.7, 0.15])
with c2:
name_input = st.text_input(“name”, placeholder=“Enter your name…”, label_visibility=“collapsed”, key=“name_field”)
if st.button(“Let’s Go”, use_container_width=True):
if name_input.strip():
st.session_state.user_name = name_input.strip()
st.session_state.memory_facts = load_memory(name_input.strip())
st.rerun()
else:
st.warning(“Please enter your name to continue.”)
st.stop()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
st.markdown(f”<div style='text-align:center; padding:20px 0 10px 0;'><div class='spiral-idle'>{SPIRAL_SVG.format(size=38, id=‘sb’)}</div><p style='font-size:1rem; color:#ffffff; margin:8px 0 0 0; font-weight:500;'>VectorWare AI</p></div>”, unsafe_allow_html=True)
mode_label = “Switch to Light Mode” if st.session_state.dark_mode else “Switch to Dark Mode”
if st.button(mode_label, use_container_width=True):
st.session_state.dark_mode = not st.session_state.dark_mode
st.rerun()
st.markdown(f”<div class='name-badge'>👤 {st.session_state.user_name}</div>”, unsafe_allow_html=True)
if st.button(“New Chat”, use_container_width=True):
st.session_state.messages = []
st.session_state.pending_image = None
st.rerun()
if st.button(“Change Name”, use_container_width=True):
st.session_state.user_name = None
st.session_state.messages = []
st.session_state.memory_facts = []
st.rerun()

```
# Mood selector in sidebar
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p class='history-label'>AI TONE</p>", unsafe_allow_html=True)
for mood_label in MOODS:
    is_active = st.session_state.mood == mood_label
    btn_style = "background:rgba(147,85,255,0.3) !important; border-color:#9b59ff !important;" if is_active else ""
    col_m1, col_m2 = st.columns([0.85, 0.15])
    with col_m1:
        if st.button(mood_label, key=f"mood_{mood_label}", use_container_width=True):
            st.session_state.mood = None if is_active else mood_label
            st.rerun()

if st.session_state.memory_facts:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p class='history-label'>WHAT I REMEMBER</p>", unsafe_allow_html=True)
    for fact in st.session_state.memory_facts[:5]:
        st.markdown(f"<span class='memory-pill'>- {fact[:40]}</span>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
today, yesterday, this_week, older = group_histories(st.session_state.chat_histories)

def render_section(label, chats, offset=0):
    if chats:
        st.markdown(f"<p class='history-label'>{label}</p>", unsafe_allow_html=True)
        for i, chat in enumerate(chats[:5]):
            if st.button(f"  {chat['title']}", key=f"h_{label}_{offset}_{i}", use_container_width=True):
                st.session_state.messages = chat["messages"]
                st.rerun()

if not st.session_state.chat_histories:
    st.markdown("<p style='color:#4b5563; font-size:0.8rem;'>No conversations yet</p>", unsafe_allow_html=True)
else:
    render_section("TODAY", today, 0)
    render_section("YESTERDAY", yesterday, 10)
    render_section("THIS WEEK", this_week, 20)
    render_section("OLDER", older, 30)

st.markdown("""<div style='margin-top:12px; padding:8px 12px; background:rgba(0,212,255,0.07); border:1px solid rgba(0,212,255,0.2); border-radius:10px;'>
<p style='color:#00d4ff; font-size:0.7rem; font-weight:600; margin:0 0 2px 0;'>ACTIVE MODEL</p>
<p style='color:#e5e7eb; font-size:0.75rem; margin:0;'>Llama 4 Scout 17B</p>
<p style='color:#6b7280; font-size:0.65rem; margin:2px 0 0 0;'>Vision · Search · Memory · Image Gen</p>
</div>""", unsafe_allow_html=True)
st.markdown("""<div class='about-section'>
<p style='color:#9b59ff; font-size:0.82rem; font-weight:600; margin:0 0 6px 0;'>Corporate Engine</p>
<p style='color:#9ca3af; font-size:0.75rem; line-height:1.5; margin:0 0 10px 0;'>Next-generation AI architecture delivering high-throughput autonomous enterprise capabilities globally.</p>
<p style='color:#6b7280; font-size:0.7rem; font-weight:600; margin:0 0 4px 0;'>FOUNDERS</p>
<span class='founder-tag'>Samuel Frimpong</span>
<span class='founder-tag'>Cardinal Kofi Nsiah</span>
<span class='founder-tag'>Gabriel Ahwireng</span>
<span class='founder-tag'>Gideon Ahwireng</span>
<p style='color:#4b5563; font-size:0.65rem; text-align:center; margin:12px 0 0 0;'>2026 VectorWare Inc.</p>
</div>""", unsafe_allow_html=True)
```

# ── WELCOME DASHBOARD ────────────────────────────────────────────────────────

if not st.session_state.messages:
greeting = get_time_greeting()
st.markdown(f”””<div style='padding:40px 0 20px 0;'>
<div class='spiral-idle' style='display:block; margin-bottom:15px;'>{SPIRAL_SVG.format(size=55, id=‘main’)}</div>
<p class='greeting'>{greeting},</p>
<p class='greeting-sub'>{st.session_state.user_name}</p>
<p style='color:#9ca3af; font-size:0.95rem; margin-top:0;'>How can I help you today?</p>
</div>”””, unsafe_allow_html=True)
suggestions = [
“Design a website for my business”,
“Explain forex trading strategies”,
“What can AI automation do for my company”,
“Write an executive pitch proposal”
]
col1, col2 = st.columns(2)
for idx, text in enumerate(suggestions):
with col1 if idx % 2 == 0 else col2:
if st.button(text, key=f”sug_{idx}”, use_container_width=True):
st.session_state.messages.append({“role”: “user”, “content”: text})
st.rerun()

# ── RENDER CHAT HISTORY ──────────────────────────────────────────────────────

for i, msg in enumerate(st.session_state.messages):
if msg[“role”] == “user”:
with st.chat_message(“user”):
if isinstance(msg.get(“content”), list):
for block in msg[“content”]:
if block[“type”] == “text”:
st.write(block[“text”])
elif block[“type”] == “image_url”:
st.image(base64.b64decode(block[“image_url”][“url”].split(”,”)[1]), width=260)
else:
st.write(msg[“content”])
else:
with st.chat_message(“assistant”):
content = msg[“content”]
if isinstance(content, dict) and content.get(“type”) == “image_gen”:
st.image(content[“url”], caption=content[“caption”])
st.write(content[“text”])
else:
st.write(content)

# ── INPUT ROW: chat input + mic icon + upload icon ───────────────────────────

col_input, col_mic, col_upload = st.columns([0.82, 0.09, 0.09])

prompt = None
with col_input:
prompt = st.chat_input(f”Ask VectorWare anything, {st.session_state.user_name}…”)

with col_mic:
st.markdown(”<div class='icon-btn' style='padding-top:6px;'>”, unsafe_allow_html=True)
try:
from streamlit_mic_recorder import mic_recorder
audio = mic_recorder(start_prompt=“🎙️”, stop_prompt=“⏹️”, just_once=True, use_container_width=False, key=“mic”)
if audio:
import io
audio_bytes = io.BytesIO(audio[“bytes”])
audio_bytes.name = “audio.wav”
with st.spinner(””):
transcription = client.audio.transcriptions.create(model=“whisper-large-v3”, file=audio_bytes)
if transcription.text:
st.session_state.voice_prompt = transcription.text
st.rerun()
except Exception:
st.markdown(“🎤”, unsafe_allow_html=True)
st.markdown(”</div>”, unsafe_allow_html=True)

with col_upload:
st.markdown(”<div style='padding-top:4px;'>”, unsafe_allow_html=True)
uploaded_file = st.file_uploader(
“img”,
type=[“png”,“jpg”,“jpeg”,“gif”,“webp”],
label_visibility=“collapsed”,
key=“image_uploader”
)
st.markdown(”</div>”, unsafe_allow_html=True)

if uploaded_file is not None:
b64, mime = encode_image(uploaded_file)
st.session_state.pending_image = {“base64”: b64, “mime_type”: mime, “name”: uploaded_file.name}
st.markdown(f”<div class='img-preview-pill'>📎 {uploaded_file.name} attached</div>”, unsafe_allow_html=True)

if st.session_state.voice_prompt:
prompt = st.session_state.voice_prompt
st.session_state.voice_prompt = None

# ── PROCESS MESSAGE ──────────────────────────────────────────────────────────

if prompt:
if st.session_state.pending_image:
img = st.session_state.pending_image
user_content = [
{“type”: “text”, “text”: prompt},
{“type”: “image_url”, “image_url”: {“url”: f”data:{img[‘mime_type’]};base64,{img[‘base64’]}”}}
]
with st.chat_message(“user”):
st.write(prompt)
st.image(base64.b64decode(img[“base64”]), width=260)
st.session_state.messages.append({“role”: “user”, “content”: user_content})
st.session_state.pending_image = None
else:
user_content = prompt
st.session_state.messages.append({“role”: “user”, “content”: prompt})
st.chat_message(“user”).write(prompt)

```
new_facts = extract_facts(prompt)
if new_facts:
    for fact in new_facts:
        if fact not in st.session_state.memory_facts:
            st.session_state.memory_facts.append(fact)
    save_memory(st.session_state.user_name, st.session_state.memory_facts)

# ── IMAGE GENERATION INTERCEPT ────────────────────────────────────────
if is_image_request(prompt):
    thinking_ph = st.empty()
    loader = st.empty()
    thinking_ph.markdown("<div class='thinking-box'>🎨 Generating your image...</div>", unsafe_allow_html=True)
    loader.markdown(f"""<div style='display:flex; align-items:center; gap:12px; padding:8px 0;'>
        <div class='spiral-thinking'>{SPIRAL_SVG.format(size=28, id='load')}</div>
        <p style='color:#9b59ff; margin:0; font-size:0.9rem; font-weight:500;'>VectorWare is painting...</p>
    </div>""", unsafe_allow_html=True)

    image_url = generate_image(prompt)
    time.sleep(1.2)
    thinking_ph.empty()
    loader.empty()

    caption_text = f"Generated: {prompt}"
    reply_text = f"Here's your image, {st.session_state.user_name}! Rendered from your description."

    with st.chat_message("assistant"):
        st.image(image_url, caption=caption_text)
        st.write(reply_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": {"type": "image_gen", "url": image_url, "caption": caption_text, "text": reply_text}
    })

    if len(st.session_state.messages) == 2:
        title = prompt[:26] + "..." if len(prompt) > 26 else prompt
        st.session_state.chat_histories.insert(0, {
            "title": title,
            "messages": list(st.session_state.messages),
            "time": datetime.now().strftime("%H:%M"),
            "date": datetime.now()
        })
        st.rerun()
    st.stop()

# ── NORMAL CHAT FLOW ──────────────────────────────────────────────────
search_context = ""
search_used = False
if needs_search(prompt):
    with st.spinner("Searching the web..."):
        result = web_search(prompt)
        if result:
            search_context = f"\n\nLive web search results:\n{result}"
            search_used = True

thinking_steps = []
if search_used:
    thinking_steps.append("Searched the web for live data")
if new_facts:
    thinking_steps.append(f"Remembered: {', '.join(new_facts[:2])}")
if st.session_state.mood:
    thinking_steps.append(f"Tone: {st.session_state.mood}")
thinking_steps.append("Generating response...")
thinking_html = "<div class='thinking-box'>" + " | ".join(thinking_steps) + "</div>"
thinking_ph = st.empty()
thinking_ph.markdown(thinking_html, unsafe_allow_html=True)
if search_used:
    st.markdown("<span class='search-pill'>🔍 Answer includes live web data</span>", unsafe_allow_html=True)

loader = st.empty()
loader.markdown(f"""<div style='display:flex; align-items:center; gap:12px; padding:8px 0;'>
    <div class='spiral-thinking'>{SPIRAL_SVG.format(size=28, id='load')}</div>
    <p style='color:#9b59ff; margin:0; font-size:0.9rem; font-weight:500;'>VectorWare is thinking...</p>
</div>""", unsafe_allow_html=True)

memory_ctx = ""
if st.session_state.memory_facts:
    memory_ctx = f"\n\nWhat you know about {st.session_state.user_name}: {', '.join(st.session_state.memory_facts)}"

mood_instruction = ""
if st.session_state.mood and st.session_state.mood in MOODS:
    mood_instruction = f"\n\nTone instruction: {MOODS[st.session_state.mood]}"

system_prompt = (
    f"You are VectorWare AI, a highly intelligent, professional and friendly AI assistant "
    f"built by VectorWare Inc. The user's name is {st.session_state.user_name}. "
    f"Address them by name naturally where it feels right. Be concise, insightful, and professional."
    f"{memory_ctx}{search_context}{mood_instruction}"
)

api_messages = [{"role": "system", "content": system_prompt}]
for m in st.session_state.messages:
    content = m["content"]
    if isinstance(content, dict):
        content = content.get("text", "")
    api_messages.append({"role": m["role"], "content": content})

stream = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=api_messages,
    max_tokens=2048,
    stream=True
)

thinking_ph.empty()
loader.empty()

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

st.session_state.messages.append({"role": "assistant", "content": full_response})

if len(st.session_state.messages) == 2:
    title = prompt[:26] + "..." if len(prompt) > 26 else prompt
    st.session_state.chat_histories.insert(0, {
        "title": title,
        "messages": list(st.session_state.messages),
        "time": datetime.now().strftime("%H:%M"),
        "date": datetime.now()
    })
    st.rerun()
```
