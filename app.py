import streamlit as st
from groq import Groq
from datetime import datetime, timedelta
import time
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VectorWare AI",
    page_icon="🌀",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp button, .stApp textarea, .stApp input { 
        font-family: 'Inter', sans-serif !important; 
    }
    
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] div,
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] div {
        font-size: 0px !important;
        color: transparent !important;
    }

    [data-testid="stChatMessageAvatarUser"] div::before {
        content: "👤";
        font-size: 1.2rem !important;
    }
    [data-testid="stChatMessageAvatarAssistant"] div::before {
        content: "🌀";
        font-size: 1.2rem !important;
    }
    
    .stApp {
        background: radial-gradient(circle at top center, #150a3a 0%, #05030d 100%);
        color: #f3f4f6 !important;
    }
    
    section[data-testid="stSidebar"] {
        background: #090615 !important;
        border-right: 1px solid rgba(147, 85, 255, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    
    .stChatInputContainer {
        background: transparent !important;
        padding: 0 !important;
    }
    
    .stChatInput input {
        background-color: #160f33 !important;
        color: #ffffff !important;
        border: 1px solid rgba(147, 85, 255, 0.3) !important;
        border-radius: 24px !important;
        padding: 12px 20px !important;
    }
    
    .stChatInput input:focus {
        border-color: rgba(147, 85, 255, 0.7) !important;
        box-shadow: 0 0 15px rgba(147, 85, 255, 0.3) !important;
    }
    
    [data-testid="stChatMessageContent"] p {
        color: #e2e8f0 !important;
        line-height: 1.75 !important;
    }
    
    [data-testid="stChatMessageContent"] strong {
        color: #d8b4fe !important;
    }
    
    @keyframes spiralGlow {
        0%, 100% { filter: drop-shadow(0 0 6px #9b59ff) drop-shadow(0 0 12px #9b59ff); }
        50% { filter: drop-shadow(0 0 16px #00d4ff) drop-shadow(0 0 25px #9b59ff); }
    }
    
    @keyframes spiralSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .spiral-idle {
        animation: spiralGlow 4s ease-in-out infinite;
        display: inline-block;
    }
    
    .spiral-thinking {
        animation: spiralSpin 1.2s linear infinite, spiralGlow 1.5s ease-in-out infinite;
        display: inline-block;
    }
    
    .greeting {
        font-size: 2.4rem;
        font-weight: 300;
        color: #ffffff !important;
        margin: 0;
    }
    
    .greeting-sub {
        font-size: 2.4rem;
        font-weight: 600;
        background: linear-gradient(90deg, #9b59ff, #bf00ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 15px 0;
    }
    
    .about-section {
        background: rgba(147, 85, 255, 0.06);
        border: 1px solid rgba(147, 85, 255, 0.2);
        border-radius: 14px;
        padding: 14px;
        margin-top: 15px;
    }
    
    .founder-tag {
        background: rgba(147, 85, 255, 0.15);
        border-radius: 8px;
        padding: 6px 10px;
        margin: 5px 0;
        font-size: 0.8rem;
        color: #d8b4fe !important;
        display: block;
    }

    .mic-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        padding-top: 5px;
    }

    .stButton button {
        background: rgba(147, 85, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(147, 85, 255, 0.25) !important;
        border-radius: 12px !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background: rgba(147, 85, 255, 0.25) !important;
        border-color: rgba(147, 85, 255, 0.6) !important;
    }

    .upload-zone {
        border: 1px dashed rgba(147, 85, 255, 0.4);
        border-radius: 14px;
        padding: 12px 16px;
        background: rgba(147, 85, 255, 0.04);
        margin-bottom: 10px;
    }

    .upload-label {
        color: #9b59ff;
        font-size: 0.78rem;
        font-weight: 500;
        margin-bottom: 4px;
        display: block;
    }

    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .img-preview-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(147, 85, 255, 0.15);
        border: 1px solid rgba(147, 85, 255, 0.3);
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 0.78rem;
        color: #d8b4fe;
        margin-bottom: 8px;
    }

    /* Name onboarding card */
    .name-card {
        background: rgba(147, 85, 255, 0.06);
        border: 1px solid rgba(147, 85, 255, 0.25);
        border-radius: 20px;
        padding: 32px 28px;
        margin: 20px 0;
        text-align: center;
    }

    /* History section labels */
    .history-label {
        color: #6b7280;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin: 12px 0 4px 0;
        padding-left: 2px;
    }

    /* Name badge in sidebar */
    .name-badge {
        background: rgba(147, 85, 255, 0.12);
        border: 1px solid rgba(147, 85, 255, 0.25);
        border-radius: 10px;
        padding: 7px 12px;
        margin-bottom: 10px;
        font-size: 0.8rem;
        color: #d8b4fe;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "name_input_temp" not in st.session_state:
    st.session_state.name_input_temp = ""

# --- HELPER: encode image ---
def encode_image(uploaded_file):
    bytes_data = uploaded_file.read()
    b64 = base64.b64encode(bytes_data).decode("utf-8")
    mime = uploaded_file.type
    return b64, mime

# --- HELPER: group chat histories by date ---
def group_histories_by_date(histories):
    now = datetime.now()
    today, yesterday, this_week, older = [], [], [], []
    for chat in histories:
        chat_date = chat.get("date", now)
        diff = (now - chat_date).days
        if diff == 0:
            today.append(chat)
        elif diff == 1:
            yesterday.append(chat)
        elif diff <= 7:
            this_week.append(chat)
        else:
            older.append(chat)
    return today, yesterday, this_week, older

# --- HELPER: get greeting based on time ---
def get_time_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# --- API INITIALIZATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============================================================
# NAME ONBOARDING SCREEN
# ============================================================
if st.session_state.user_name is None:
    st.markdown("""
        <div style='padding: 40px 0 10px 0; text-align: center;'>
            <div class='spiral-idle' style='display:block; margin-bottom:15px;'>
                <svg width="60" height="60" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="spiralMain" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#bf00ff"/>
                            <stop offset="100%" style="stop-color:#7b2fff"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#spiralMain)" stroke-width="18" 
                          stroke-linecap="round"/>
                </svg>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='name-card'>
            <p style='font-size:1.6rem; font-weight:300; color:#ffffff; margin:0;'>Welcome to</p>
            <p style='font-size:1.8rem; font-weight:700; background: linear-gradient(90deg, #9b59ff, #bf00ff, #00d4ff);
                      -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin:0 0 8px 0;'>
                VectorWare AI
            </p>
            <p style='color:#9ca3af; font-size:0.95rem; margin:0 0 24px 0;'>
                Before we begin — what's your name?
            </p>
        </div>
    """, unsafe_allow_html=True)

    name_col1, name_col2, name_col3 = st.columns([0.15, 0.7, 0.15])
    with name_col2:
        name_input = st.text_input(
            label="your name",
            placeholder="Enter your name...",
            label_visibility="collapsed",
            key="name_field"
        )
        if st.button("Let's Go →", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")

    st.stop()  # Don't render anything else until name is entered


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 20px 0 10px 0;'>
            <div class='spiral-idle'>
                <svg width="38" height="38" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#bf00ff"/>
                            <stop offset="100%" style="stop-color:#7b2fff"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#sg)" stroke-width="18" 
                          stroke-linecap="round"/>
                </svg>
            </div>
            <p style='font-size:1rem; color:#ffffff; margin:8px 0 0 0; font-weight:500;'>VectorWare AI</p>
        </div>
    """, unsafe_allow_html=True)

    # Show user name badge
    st.markdown(f"""
        <div class='name-badge'>
            👤 {st.session_state.user_name}
        </div>
    """, unsafe_allow_html=True)

    if st.button("✦ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_image = None
        st.rerun()

    # Change name button
    if st.button("✎ Change Name", use_container_width=True):
        st.session_state.user_name = None
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GROUPED CHAT HISTORY ---
    today, yesterday, this_week, older = group_histories_by_date(st.session_state.chat_histories)

    def render_history_section(label, chats, offset=0):
        if chats:
            st.markdown(f"<p class='history-label'>{label}</p>", unsafe_allow_html=True)
            for i, chat in enumerate(chats[:5]):
                if st.button(f"↩ {chat['title']}", key=f"hist_{label}_{offset}_{i}", use_container_width=True):
                    st.session_state.messages = chat["messages"]
                    st.rerun()

    if not st.session_state.chat_histories:
        st.markdown("<p style='color:#4b5563; font-size:0.8rem; margin-top:5px;'>No conversations yet</p>", unsafe_allow_html=True)
    else:
        render_history_section("TODAY", today, 0)
        render_history_section("YESTERDAY", yesterday, 10)
        render_history_section("THIS WEEK", this_week, 20)
        render_history_section("OLDER", older, 30)

    # Model badge
    st.markdown("""
        <div style='margin-top: 12px; padding: 8px 12px; background: rgba(0,212,255,0.07); 
             border: 1px solid rgba(0,212,255,0.2); border-radius: 10px;'>
            <p style='color:#00d4ff; font-size:0.7rem; font-weight:600; margin:0 0 2px 0;'>⚡ ACTIVE MODEL</p>
            <p style='color:#e5e7eb; font-size:0.75rem; margin:0;'>Llama 4 Scout 17B</p>
            <p style='color:#6b7280; font-size:0.65rem; margin:2px 0 0 0;'>Vision · Fast · Multilingual</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='about-section'>
            <p style='color:#9b59ff; font-size:0.82rem; font-weight:600; margin:0 0 6px 0;'>🏢 Corporate Engine</p>
            <p style='color:#9ca3af; font-size:0.75rem; line-height:1.5; margin:0 0 10px 0;'>
            Next-generation AI architecture delivering high-throughput autonomous enterprise capabilities globally.
            </p>
            <p style='color:#6b7280; font-size:0.7rem; font-weight:600; margin:0 0 4px 0;'>FOUNDERS</p>
            <span class='founder-tag'>🚀 Samuel Frimpong</span>
            <span class='founder-tag'>💡 Cardinal Kofi Nsiah</span>
            <span class='founder-tag'>⚡ Gabriel Ahwireng</span>
            <span class='founder-tag'>⚙️ Gideon Ahwireng</span>
            <p style='color:#4b5563; font-size:0.65rem; text-align:center; margin:12px 0 0 0;'>©️ 2026 VectorWare Inc.</p>
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# WELCOME DASHBOARD
# ============================================================
if not st.session_state.messages:
    greeting = get_time_greeting()
    st.markdown(f"""
        <div style='padding: 40px 0 20px 0;'>
            <div class='spiral-idle' style='display:block; margin-bottom:15px;'>
                <svg width="55" height="55" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="spiralMain2" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#bf00ff"/>
                            <stop offset="100%" style="stop-color:#7b2fff"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#spiralMain2)" stroke-width="18" 
                          stroke-linecap="round"/>
                </svg>
            </div>
            <p class='greeting'>{greeting},</p>
            <p class='greeting-sub'>{st.session_state.user_name} 👋</p>
            <p style='color:#9ca3af; font-size:0.95rem; margin-top:0;'>How can I help you today?</p>
        </div>
    """, unsafe_allow_html=True)

    suggestions = [
        ("🎨", "Help me design a website for my business"),
        ("📈", "Explain forex trading strategies"),
        ("🤖", "What can AI automation do for my company"),
        ("✍️", "Write an executive pitch proposal for me"),
    ]

    col1, col2 = st.columns(2)
    for idx, (icon, text) in enumerate(suggestions):
        with col1 if idx % 2 == 0 else col2:
            if st.button(f"{icon}  {text}", key=f"suggest_{idx}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()


# ============================================================
# RENDER CHAT HISTORY
# ============================================================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            if isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if block["type"] == "text":
                        st.write(block["text"])
                    elif block["type"] == "image_url":
                        st.image(
                            base64.b64decode(block["image_url"]["url"].split(",")[1]),
                            width=260
                        )
            else:
                st.write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])


# ============================================================
# IMAGE UPLOAD ZONE
# ============================================================
st.markdown("<div class='upload-zone'>", unsafe_allow_html=True)
st.markdown("<span class='upload-label'>🖼️ Attach an image for VectorWare to analyze</span>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="upload",
    type=["png", "jpg", "jpeg", "gif", "webp"],
    label_visibility="collapsed",
    key="image_uploader"
)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    b64, mime = encode_image(uploaded_file)
    st.session_state.pending_image = {"base64": b64, "mime_type": mime, "name": uploaded_file.name}
    st.markdown(f"""
        <div class='img-preview-pill'>
            🖼️ {uploaded_file.name} attached — ask anything about it below
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# CONTROL BAR — INPUT + MIC
# ============================================================
col_input, col_mic = st.columns([0.88, 0.12])

with col_mic:
    st.markdown("""
        <div class="mic-container">
            <button id='micBtn' onclick='startVoiceCapture()'
                style='background:#160f33; border:1px solid rgba(147,85,255,0.35);
                       border-radius:50%; width:44px; height:44px; cursor:pointer;
                       font-size:1.2rem; display:flex; align-items:center;
                       justify-content:center; transition: all 0.2s ease;'>
                🎤
            </button>
        </div>

        <script>
        function startVoiceCapture() {
            const SpeechEngine = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechEngine) {
                alert('Please use Chrome for voice input.');
                return;
            }
            const rec = new SpeechEngine();
            rec.lang = 'en-US';
            rec.interimResults = false;
            rec.maxAlternatives = 1;
            const btn = document.getElementById('micBtn');

            rec.onstart = () => {
                btn.innerHTML = '🔴';
                btn.style.borderColor = '#ff4444';
                btn.style.boxShadow = '0 0 12px rgba(255,68,68,0.5)';
            };

            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                const textarea = window.parent.document.querySelector(
                    'textarea[data-testid="stChatInputTextArea"]'
                );
                if (textarea) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value'
                    ).set;
                    setter.call(textarea, text);
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    textarea.focus();
                }
            };

            rec.onerror = (e) => {
                btn.innerHTML = '🎤';
                btn.style.borderColor = 'rgba(147,85,255,0.35)';
                btn.style.boxShadow = 'none';
                if (e.error === 'not-allowed') {
                    alert('Mic access denied. Allow microphone in browser settings.');
                }
            };

            rec.onend = () => {
                btn.innerHTML = '🎤';
                btn.style.borderColor = 'rgba(147,85,255,0.35)';
                btn.style.boxShadow = 'none';
            };

            rec.start();
        }
        </script>
    """, unsafe_allow_html=True)

with col_input:
    prompt = st.chat_input(f"Ask VectorWare AI anything, {st.session_state.user_name}...")


# ============================================================
# MESSAGE PROCESSING
# ============================================================
if prompt:
    if st.session_state.pending_image:
        img = st.session_state.pending_image
        user_message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{img['mime_type']};base64,{img['base64']}"}}
        ]
        with st.chat_message("user"):
            st.write(prompt)
            st.image(base64.b64decode(img["base64"]), width=260)
        st.session_state.messages.append({"role": "user", "content": user_message_content})
        st.session_state.pending_image = None
    else:
        user_message_content = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

    # Thinking loader
    thinking = st.empty()
    thinking.markdown("""
        <div style='display:flex; align-items:center; gap:12px; padding:12px 0;'>
            <div class='spiral-thinking'>
                <svg width="32" height="32" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="st" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#bf00ff"/>
                            <stop offset="100%" style="stop-color:#00d4ff"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#st)" stroke-width="18" 
                          stroke-linecap="round"/>
                </svg>
            </div>
            <p style='color:#9b59ff; margin:0; font-size:0.9rem; font-weight:500;'>VectorWare is thinking...</p>
        </div>
    """, unsafe_allow_html=True)

    # System prompt that knows the user's name
    system_prompt = f"""You are VectorWare AI, a highly intelligent, professional and friendly AI assistant built by VectorWare Inc.
The user's name is {st.session_state.user_name}. Address them by name naturally and warmly where appropriate — not every message, just when it feels right.
Be concise, helpful, and professional. You can analyze images, answer questions, write content, and help with business tasks."""

    api_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    stream = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=api_messages,
        max_tokens=2048,
        stream=True
    )

    thinking.empty()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in stream:
            content_chunk = chunk.choices[0].delta.content
            if content_chunk:
                for char in content_chunk:
                    full_response += char
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(0.005)
        response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Save to history with date
    if len(st.session_state.messages) == 2:
        title = prompt[:26] + "..." if len(prompt) > 26 else prompt
        st.session_state.chat_histories.insert(0, {
            "title": title,
            "messages": list(st.session_state.messages),
            "time": datetime.now().strftime("%H:%M"),
            "date": datetime.now()
        })
        st.rerun()
