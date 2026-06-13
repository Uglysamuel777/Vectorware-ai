import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(
    page_title="VectorWare AI",
    page_icon="🌀",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;500;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0d0015, #1a0030, #0d0015);
        color: white !important;
    }
    
    section[data-testid="stSidebar"] {
        background: rgba(20, 0, 40, 0.95) !important;
        border-right: 1px solid #7b2fff !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .stChatInput input {
        background-color: #1a0030 !important;
        color: white !important;
        border: 1px solid #7b2fff !important;
        border-radius: 25px !important;
        box-shadow: 0 0 8px rgba(123, 47, 255, 0.4) !important;
    }
    
    .stChatMessage {
        background: rgba(123, 47, 255, 0.08) !important;
        border: 1px solid rgba(123, 47, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 10px !important;
        box-shadow: 0 0 10px rgba(123, 47, 255, 0.15) !important;
        margin-bottom: 8px !important;
    }
    
    [data-testid="stChatMessageContent"] * {
        color: white !important;
    }
    
    [data-testid="stChatMessageContent"] strong {
        color: #cc99ff !important;
    }
    
    .stMarkdown p {
        color: white !important;
    }

    .header-container {
        text-align: center;
        padding: 20px 0 5px 0;
    }
    
    .logo-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2em;
        background: linear-gradient(90deg, #bf00ff, #7b2fff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .tagline {
        color: #bb88ff !important;
        font-size: 0.85em;
        letter-spacing: 2px;
        margin-top: 3px;
    }
    
    .glow-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #7b2fff, #bf00ff, transparent);
        margin: 15px 0;
        box-shadow: 0 0 8px #7b2fff;
    }
    
    .spiral-container {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
        animation: pulse 3s infinite;
    }
    
    @keyframes pulse {
        0% { filter: drop-shadow(0 0 8px #7b2fff); }
        50% { filter: drop-shadow(0 0 20px #bf00ff); }
        100% { filter: drop-shadow(0 0 8px #7b2fff); }
    }
    
    .status-bar {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 8px;
        background: rgba(123, 47, 255, 0.1);
        border-radius: 10px;
        margin-bottom: 15px;
        font-size: 0.75em;
        color: #bb88ff !important;
    }
    
    .mic-btn {
        background: linear-gradient(135deg, #7b2fff, #bf00ff);
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 22px;
        cursor: pointer;
        box-shadow: 0 0 15px rgba(191, 0, 255, 0.6);
        display: block;
        margin: 10px auto;
        transition: all 0.3s ease;
    }
    
    .mic-btn:hover {
        box-shadow: 0 0 25px rgba(191, 0, 255, 0.9);
        transform: scale(1.1);
    }
    
    .mic-label {
        text-align: center;
        color: #bb88ff;
        font-size: 0.75em;
        margin-top: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0;'>
            <p style='font-family: Orbitron; font-size: 1.1em; 
            background: linear-gradient(90deg, #bf00ff, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;'>
            🌀 VectorWare AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_histories = st.session_state.get("chat_histories", [])
        st.rerun()
    
    st.markdown("---")
    st.markdown("**💬 Chat History**")
    
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []
    
    for i, chat in enumerate(st.session_state.chat_histories):
        if st.button(f"🕐 {chat['title']}", key=f"hist_{i}", use_container_width=True):
            st.session_state.messages = chat["messages"]
            st.rerun()
    
    st.markdown("---")
    st.markdown("**⚡ Model**")
    st.markdown("<small style='color:#bb88ff'>llama-3.1-8b-instant</small>", unsafe_allow_html=True)
    st.markdown("**🔋 Status**")
    st.markdown("<small style='color:#00ff88'>● Online</small>", unsafe_allow_html=True)

# Main content
st.markdown("""
    <div class="header-container">
        <div class="spiral-container">
            <svg width="80" height="80" viewBox="0 0 200 200">
                <defs>
                    <linearGradient id="spiralGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#bf00ff"/>
                        <stop offset="100%" style="stop-color:#7b2fff"/>
                    </linearGradient>
                </defs>
                <path d="M100,100 
                         C100,60 140,40 160,70 
                         C180,100 160,140 130,150 
                         C90,165 50,140 40,100 
                         C25,50 60,15 100,15 
                         C150,15 185,55 185,100 
                         C185,155 140,190 90,185"
                      fill="none"
                      stroke="url(#spiralGrad)"
                      stroke-width="18"
                      stroke-linecap="round"/>
            </svg>
        </div>
        <p class="logo-title">🌀 VectorWare AI</p>
        <p class="tagline">✦ Building the Future, One Line at a Time ✦</p>
    </div>
    <hr class="glow-divider">
    
    <div class="status-bar">
        <span>🟢 AI Online</span>
        <span>⚡ Fast Mode</span>
        <span>🔒 Secure</span>
        <span>🌍 Ghana 🇬🇭</span>
    </div>
    
    <button class="mic-btn" id="micBtn" onclick="startVoice()" title="Voice Search">🎤</button>
    <p class="mic-label">Tap to speak (Chrome only)</p>
    
    <script>
    function startVoice() {
        const SpeechRecognition = window.SpeechRecognition || 
                                   window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Please open this app in Chrome for voice search!');
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        const btn = document.getElementById('micBtn');
        
        recognition.onstart = function() {
            btn.innerHTML = '🔴';
            btn.style.boxShadow = '0 0 25px red';
        };
        
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            const input = document.querySelector('input[type="text"]') || 
                          document.querySelector('input');
            if (input) {
                const nativeInputSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputSetter.call(input, text);
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
            btn.innerHTML = '🎤';
            btn.style.boxShadow = '0 0 15px rgba(191, 0, 255, 0.6)';
        };
        
        recognition.onerror = function(e) {
            alert('Mic error: ' + e.error + '. Allow microphone access in Chrome settings!');
            btn.innerHTML = '🎤';
            btn.style.boxShadow = '0 0 15px rgba(191, 0, 255, 0.6)';
        };
        
        recognition.onend = function() {
            btn.innerHTML = '🎤';
            btn.style.boxShadow = '0 0 15px rgba(191, 0, 255, 0.6)';
        };
        
        recognition.start();
    }
    </script>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("🌀 Ask VectorWare AI anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner(""):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages
        )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
    
    if len(st.session_state.messages) == 2:
        title = prompt[:30] + "..." if len(prompt) > 30 else prompt
        st.session_state.chat_histories.insert(0, {
            "title": title,
            "messages": st.session_state.messages.copy(),
            "time": datetime.now().strftime("%H:%M")
        })
    
    st.rerun()
