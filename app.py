import streamlit as st
from groq import Groq
from datetime import datetime
import time
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VectorWare AI",
    page_icon="🌀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL MODERN PURPLE ACCENT THEME ---
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
    
    .mic-icon-btn {
        background: #160f33;
        border: 1px solid rgba(147, 85, 255, 0.35);
        border-radius: 50%;
        width: 44px;
        height: 44px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .mic-icon-btn:hover {
        background: rgba(147, 85, 255, 0.2);
        border-color: rgba(147, 85, 255, 0.7);
        box-shadow: 0 0 10px rgba(147, 85, 255, 0.3);
    }
    
    .mic-svg {
        width: 18px;
        height: 18px;
        fill: #c084fc;
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

    /* Image upload zone styling */
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

    /* Hide default Streamlit file uploader chrome */
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

    /* Image preview pill */
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
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None  # stores {base64, mime_type, name}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 20px 0 15px 0;'>
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
            <p style='font-size:1rem; color:#ffffff; margin:8px 0 0 0; font-weight:500; letter-spacing:0.3px;'>VectorWare AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✦ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_image = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280; font-size:0.75rem; font-weight:600; margin:0;'>RECENT CHATS</p>", unsafe_allow_html=True)
    
    if not st.session_state.chat_histories:
        st.markdown("<p style='color:#4b5563; font-size:0.8rem; margin-top:5px;'>No conversations yet</p>", unsafe_allow_html=True)
    else:
        for i, chat in enumerate(st.session_state.chat_histories[:6]):
            if st.button(f"↩ {chat['title']}", key=f"history_item_{i}", use_container_width=True):
                st.session_state.messages = chat["messages"]
                st.rerun()

    # Model badge in sidebar
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


# --- API INITIALIZATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- HELPER: encode uploaded image to base64 ---
def encode_image(uploaded_file):
    bytes_data = uploaded_file.read()
    b64 = base64.b64encode(bytes_data).decode("utf-8")
    mime = uploaded_file.type  # e.g. "image/png"
    return b64, mime


# --- WELCOME DASHBOARD ---
if not st.session_state.messages:
    st.markdown("""
        <div style='padding: 40px 0 20px 0;'>
            <div class='spiral-idle' style='display:block; margin-bottom:15px;'>
                <svg width="55" height="55" viewBox="0 0 200 200">
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
            <p class='greeting'>Hello, I'm</p>
            <p class='greeting-sub'>VectorWare AI</p>
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

# --- RENDER CHAT HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            # If message has an image preview saved, show it
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


# --- IMAGE UPLOAD ZONE (above input bar) ---
st.markdown("<div class='upload-zone'>", unsafe_allow_html=True)
st.markdown("<span class='upload-label'>🖼️ Attach an image for VectorWare to analyze</span>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="upload",
    type=["png", "jpg", "jpeg", "gif", "webp"],
    label_visibility="collapsed",
    key="image_uploader"
)
st.markdown("</div>", unsafe_allow_html=True)

# Store uploaded image in session state
if uploaded_file is not None:
    b64, mime = encode_image(uploaded_file)
    st.session_state.pending_image = {
        "base64": b64,
        "mime_type": mime,
        "name": uploaded_file.name
    }
    st.markdown(f"""
        <div class='img-preview-pill'>
            🖼️ {uploaded_file.name} attached — ask anything about it below
        </div>
    """, unsafe_allow_html=True)


# --- CONTROL BAR ---
col_input, col_mic = st.columns([0.88, 0.12])

with col_mic:
    st.markdown("""
        <div class="mic-container">
            <button class='mic-icon-btn' id='micBtn' onclick='startVoiceCapture()'>
                <svg class='mic-svg' viewBox="0 0 24 24">
                    <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm0 2a2 2 0 0 0-2 2v6a2 2 0 0 0 4 0V5a2 2 0 0 0-2-2zm-1 15.93V21h2v-2.07A8 8 0 0 0 20 11h-2a6 6 0 0 1-12 0H4a8 8 0 0 0 7 7.93z"/>
                </svg>
            </button>
        </div>
        <script>
        function startVoiceCapture() {
            const SpeechEngine = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechEngine) { alert('Voice capture is supported primarily on Chrome browsers.'); return; }
            const rec = new SpeechEngine();
            rec.lang = 'en-US';
            rec.interimResults = false;
            const btn = document.getElementById('micBtn');
            rec.onstart = () => {
                btn.style.background = 'rgba(155, 89, 255, 0.25)';
                btn.style.borderColor = '#9b59ff';
            };
            rec.onresult = (e) => {
                const capturedText = e.results[0][0].transcript;
                const nativeInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if (nativeInput) {
                    nativeInput.value = capturedText;
                    nativeInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            rec.onend = () => {
                btn.style.background = '#160f33';
                btn.style.borderColor = 'rgba(147, 85, 255, 0.35)';
            };
            rec.start();
        }
        </script>
    """, unsafe_allow_html=True)

with col_input:
    prompt = st.chat_input("Ask VectorWare AI anything... or attach an image above ↑")


# --- MESSAGE PROCESSING ---
if prompt:
    # Build the user message — multimodal if image is attached
    if st.session_state.pending_image:
        img = st.session_state.pending_image
        user_message_content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['mime_type']};base64,{img['base64']}"
                }
            }
        ]
        # Display user message with image preview
        with st.chat_message("user"):
            st.write(prompt)
            st.image(base64.b64decode(img["base64"]), width=260)

        st.session_state.messages.append({
            "role": "user",
            "content": user_message_content
        })
        st.session_state.pending_image = None  # Clear after sending

    else:
        # Plain text message
        user_message_content = prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

    # --- THINKING LOADER ---
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

    # --- API CALL: Llama 4 Scout with vision support ---
    # Build messages for API — serialize content correctly
    api_messages = []
    for m in st.session_state.messages:
        api_messages.append({
            "role": m["role"],
            "content": m["content"]  # already correct format (str or list)
        })

    stream = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  # ⬆️ UPGRADED
        messages=api_messages,
        max_tokens=2048,
        stream=True
    )

    thinking.empty()

    # --- TYPEWRITER RESPONSE ---
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

    # Save to history
    if len(st.session_state.messages) == 2:
        title = prompt[:26] + "..." if len(prompt) > 26 else prompt
        st.session_state.chat_histories.insert(0, {
            "title": title,
            "messages": list(st.session_state.messages),
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()
