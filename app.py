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
        background: rgba(20, 0, 40, 0.98) !important;
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
        width: 45px;
        height: 45px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 0 12px rgba(191, 0, 255, 0.6);
        transition: all 0.3s ease;
    }
    
    .mic-btn:hover {
        box-shadow: 0 0 25px rgba(191, 0, 255, 0.9);
        transform: scale(1.1);
    }
    
    .mic-label {
        color: #bb88ff;
        font-size: 0.7em;
        margin-top: 3px;
        text-align: center;
    }

    .about-card {
        background: rgba(123, 47, 255, 0.1);
        border: 1px solid rgba(123, 47, 255, 0.4);
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
    }
    
    .about-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9em;
        background: linear-gradient(90deg, #bf00ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .about-text {
        color: #bb88ff !important;
        font-size: 0.78em;
        line-height: 1.6;
    }
    
    .founder-badge {
        background: rgba(123, 47, 255, 0.2);
        border: 1px solid #7b2fff;
        border-radius: 8px;
        padding: 5px 10px;
        margin: 4px 0;
        font-size: 0.75em;
        color: white !important;
    }

    .dash-card {
        background: rgba(123, 47, 255, 0.1);
        border: 1px solid rgba(123, 47, 255, 0.3);
        border-radius: 12px;
        padding: 12px 15px;
        text-align: center;
    }
    
    .dash-card h3 {
        font-size: 1.5em;
        color: #bf00ff !important;
        margin: 0;
    }
    
    .dash-card p {
        font-size: 0.75em;
        color: #bb88ff !important;
        margin: 3px 0 0 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 10px 0 5px 0;'>
            <p style='font-family: Orbitron; font-size: 1.1em; 
            background: linear-gradient(90deg, #bf00ff, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin:0;'>
            🌀 VectorWare AI</p>
            <p style='color:#bb88ff; font-size:0.7em; margin:2px 0 10px 0;'>
            Building the Future</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**💬 Chat History**")
    
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []
    
    if len(st.session_state.chat_histories) == 0:
        st.markdown("<small style='color:#666'>No chats yet</small>", unsafe_allow_html=True)
    
    for i, chat in enumerate(st.session_state.chat_histories):
        if st.button(f"🕐 {chat['title']}", key=f"hist_{i}", use_container_width=True):
            st.session_state.messages = chat["messages"]
            st.rerun()
    
    st.markdown("---")
    
    # System Info
    st.markdown("**⚙️ System**")
    st.markdown("<small style='color:#bb88ff'>Model: llama-3.1-8b</small>", unsafe_allow_html=True)
    st.markdown("<small style='color:#00ff88'>● Status: Online</small>", unsafe_allow_html=True)
    st.markdown("<small style='color:#bb88ff'>Version: 1.0.0</small>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # About Section
    st.markdown("""
        <div class="about-card">
            <p class="about-title">🏢 About VectorWare</p>
            <p class="about-text">
                VectorWare is a next-generation AI and technology company delivering 
                cutting-edge web design, game development, and AI automation solutions 
                to clients worldwide.
            </p>
            <br/>
            <p style='color:#7b2fff; font-size:0.75em; margin-bottom:5px;'>👥 Founders</p>
            <div class="founder-badge">🚀 Samuel Frimpong</div>
            <div class="founder-badge">💡 Cardinal Kofi Nsiah</div>
            <br/>
            <p style='color:#666; font-size:0.7em; text-align:center;'>
            © 2025 VectorWare. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

# Dashboard stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
        <div class="dash-card">
            <h3>🌀</h3>
            <p>VectorWare AI</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="dash-card">
            <h3>⚡</h3>
            <p>Fast Mode Active</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class="dash-card">
            <h3>🔒</h3>
            <p>Encrypted & Secure</p>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
        <div class="dash-card">
            <h3>🌐</h3>
            <p>Available Worldwide</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main header
st.markdown("""
    <div class="header-container">
        <div class="spiral-container">
            <svg width="75" height="75" viewBox="0 0 200 200">
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
""", unsafe_allow_html=True)

# Status bar + mic on right
st.markdown("""
    <div style="display: flex; align-items: center; 
    justify-content: space-between; padding: 0 5px; margin-bottom: 15px;">
        <div class="status-bar" style="flex:1; margin-right:10px;">
            <span>🟢 AI Online</span>
            <span>⚡ Fast Mode</span>
            <span>🔒 Secure</span>
            <span>🌐 Worldwide</span>
        </div>
        <div style="text-align:center;">
            <button class="mic-btn" id="micBtn" 
            onclick="startVoice()" title="Voice Search">🎤</button>
            <p class="mic-label">Voice</p>
        </div>
    </div>
    
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
            btn.style.boxShadow = '0 0 12px rgba(191, 0, 255, 0.6)';
        };
        recognition.onerror = function(e) {
            alert('Mic error: ' + e.error + '. Allow microphone in Chrome settings!');
            btn.innerHTML = '🎤';
            btn.style.boxShadow = '0 0 12px rgba(191, 0, 255, 0.6)';
        };
        recognition.onend = function() {
            btn.innerHTML = '🎤';
            btn.style.boxShadow = '0 0 12px rgba(191, 0, 255, 0.6)';
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
