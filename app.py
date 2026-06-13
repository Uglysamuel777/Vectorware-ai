import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(
    page_title="VectorWare AI",
    page_icon="🌀",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    .stApp {
        background: #080810;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] {
        background: #0d0d1a !important;
        border-right: 1px solid rgba(123, 47, 255, 0.15) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .stChatInput input {
        background-color: #12121f !important;
        color: white !important;
        border: 1px solid rgba(123, 47, 255, 0.25) !important;
        border-radius: 30px !important;
        font-size: 1em !important;
    }
    
    .stChatInput input:focus {
        border: 1px solid rgba(123, 47, 255, 0.6) !important;
        box-shadow: 0 0 15px rgba(123, 47, 255, 0.15) !important;
    }
    
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 5px 0 !important;
    }
    
    [data-testid="stChatMessageContent"] * {
        color: white !important;
        line-height: 1.7 !important;
    }
    
    [data-testid="stChatMessageContent"] strong {
        color: #bb88ff !important;
    }
    
    .stMarkdown p { color: white !important; }
    
    @keyframes spiralGlow {
        0% { filter: drop-shadow(0 0 5px #7b2fff) drop-shadow(0 0 10px #7b2fff); }
        25% { filter: drop-shadow(0 0 15px #bf00ff) drop-shadow(0 0 30px #bf00ff); }
        50% { filter: drop-shadow(0 0 25px #00d4ff) drop-shadow(0 0 50px #7b2fff); }
        75% { filter: drop-shadow(0 0 15px #bf00ff) drop-shadow(0 0 30px #bf00ff); }
        100% { filter: drop-shadow(0 0 5px #7b2fff) drop-shadow(0 0 10px #7b2fff); }
    }
    
    @keyframes spiralSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .spiral-idle {
        animation: spiralGlow 3s ease-in-out infinite;
        display: inline-block;
    }
    
    .spiral-thinking {
        animation: spiralSpin 1s linear infinite, spiralGlow 1s ease-in-out infinite;
        display: inline-block;
    }
    
    .greeting {
        font-size: 2.2em;
        font-weight: 300;
        color: white !important;
        margin: 0;
        line-height: 1.2;
    }
    
    .greeting-sub {
        font-size: 2.2em;
        font-weight: 600;
        background: linear-gradient(90deg, #9b59ff, #bf00ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .suggestion-btn {
        background: #12121f;
        border: 1px solid rgba(123, 47, 255, 0.2);
        border-radius: 15px;
        padding: 14px 18px;
        color: white !important;
        font-size: 0.9em;
        cursor: pointer;
        width: 100%;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: 8px;
    }
    
    .suggestion-btn:hover {
        background: rgba(123, 47, 255, 0.15);
        border-color: rgba(123, 47, 255, 0.5);
        box-shadow: 0 0 10px rgba(123, 47, 255, 0.2);
    }
    
    .bottom-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 8px;
    }
    
    .mic-icon-btn {
        background: transparent;
        border: 1px solid rgba(123, 47, 255, 0.3);
        border-radius: 50%;
        width: 42px;
        height: 42px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }
    
    .mic-icon-btn:hover {
        background: rgba(123, 47, 255, 0.15);
        border-color: rgba(123, 47, 255, 0.6);
    }
    
    .mic-svg {
        width: 18px;
        height: 18px;
        fill: rgba(180, 140, 255, 0.8);
    }
    
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 0;
        margin-bottom: 10px;
    }
    
    .logo-small {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9em;
        color: #9b8ec4 !important;
        font-weight: 500;
    }
    
    .sidebar-item {
        background: rgba(123, 47, 255, 0.08);
        border: 1px solid rgba(123, 47, 255, 0.15);
        border-radius: 10px;
        padding: 10px 12px;
        margin: 4px 0;
        font-size: 0.82em;
        color: #ccc !important;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .sidebar-item:hover {
        background: rgba(123, 47, 255, 0.2);
    }
    
    .about-section {
        background: rgba(123, 47, 255, 0.06);
        border: 1px solid rgba(123, 47, 255, 0.15);
        border-radius: 12px;
        padding: 14px;
        margin-top: 8px;
    }
    
    .founder-tag {
        background: rgba(123, 47, 255, 0.12);
        border-radius: 8px;
        padding: 6px 10px;
        margin: 4px 0;
        font-size: 0.78em;
        color: #bb88ff !important;
        display: block;
    }

    .stButton button {
        background: rgba(123, 47, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(123, 47, 255, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background: rgba(123, 47, 255, 0.25) !important;
        border-color: rgba(123, 47, 255, 0.5) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 15px 0 10px 0;'>
            <div class='spiral-idle' style='display:inline-block;'>
                <svg width="35" height="35" viewBox="0 0 200 200">
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
            <p style='font-size:0.95em; color:#9b8ec4; margin:5px 0 0 0; 
            font-weight:500;'>VectorWare AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✦ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#555; font-size:0.75em; margin:0;'>RECENT</p>", 
                unsafe_allow_html=True)
    
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []
    
    if len(st.session_state.chat_histories) == 0:
        st.markdown("<p style='color:#444; font-size:0.8em;'>No conversations yet</p>", 
                    unsafe_allow_html=True)
    
    for i, chat in enumerate(st.session_state.chat_histories[:8]):
        if st.button(f"↩ {chat['title']}", key=f"h_{i}", use_container_width=True):
            st.session_state.messages = chat["messages"]
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='about-section'>
            <p style='color:#9b59ff; font-size:0.8em; font-weight:600; margin:0 0 8px 0;'>
            🏢 VectorWare</p>
            <p style='color:#888; font-size:0.75em; line-height:1.5; margin:0 0 10px 0;'>
            Next-generation AI & technology company delivering cutting-edge solutions worldwide.
            </p>
            <p style='color:#555; font-size:0.72em; margin:0 0 5px 0;'>FOUNDERS</p>
            <span class='founder-tag'>🚀 Samuel Frimpong</span>
            <span class='founder-tag'>💡 Cardinal Kofi Nsiah</span>
            <p style='color:#333; font-size:0.68em; text-align:center; margin:10px 0 0 0;'>
            © 2025 VectorWare Inc.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#333; font-size:0.7em;'>● Online &nbsp; v1.0.0</p>", 
                unsafe_allow_html=True)

# Main area
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show greeting if no messages
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div style='padding: 50px 0 30px 0;'>
            <div class='spiral-idle' style='display:block; margin-bottom:20px;'>
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
            <p class='greeting'>Hello, I'm</p>
            <p class='greeting-sub'>VectorWare AI</p>
            <p style='color:#555; font-size:0.95em; margin-top:8px;'>
            How can I help you today?</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Suggestion buttons
    suggestions = [
        ("🎨", "Help me design a website for my business"),
        ("📈", "Explain forex trading strategies"),
        ("🤖", "What can AI automation do for my company"),
        ("✍️", "Write anything for me"),
    ]
    
    col1, col2 = st.columns(2)
    for i, (icon, text) in enumerate(suggestions):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"{icon}  {text}", key=f"sug_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()

# Chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Bottom input bar with mic
col_input, col_mic = st.columns([10, 1])

with col_mic:
    st.markdown("""
        <button class='mic-icon-btn' id='micBtn' onclick='startVoice()' 
        style='margin-top:5px;'>
            <svg class='mic-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm0 2a2 2 0 0 0-2 2v6a2 2 0 0 0 4 0V5a2 2 0 0 0-2-2zm-1 15.93V21h2v-2.07A8 8 0 0 0 20 11h-2a6 6 0 0 1-12 0H4a8 8 0 0 0 7 7.93z"/>
            </svg>
        </button>
        
        <script>
        function startVoice() {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SR) { alert('Use Chrome for voice!'); return; }
            const r = new SR();
            r.lang = 'en-US';
            r.interimResults = false;
            const btn = document.getElementById('micBtn');
            
            r.onstart = () => {
                btn.style.background = 'rgba(191, 0, 255, 0.2)';
                btn.style.borderColor = '#bf00ff';
            };
            r.onresult = (e) => {
                const text = e.results[0][0].transcript;
                const input = document.querySelector('input');
                if (input) {
                    Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype,'value'
                    ).set.call(input, text);
                    input.dispatchEvent(new Event('input',{bubbles:true}));
                }
                btn.style.background = 'transparent';
                btn.style.borderColor = 'rgba(123,47,255,0.3)';
            };
            r.onerror = (e) => {
                alert('Error: ' + e.error);
                btn.style.background = 'transparent';
            };
            r.onend = () => {
                btn.style.background = 'transparent';
                btn.style.borderColor = 'rgba(123,47,255,0.3)';
            };
            r.start();
        }
        </script>
    """, unsafe_allow_html=True)

prompt = st.chat_input("Ask VectorWare AI anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Glowing spiral while thinking
    thinking = st.empty()
    thinking.markdown("""
        <div style='display:flex; align-items:center; gap:12px; padding:10px 0;'>
            <div class='spiral-thinking'>
                <svg width="35" height="35" viewBox="0 0 200 200">
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
            <p style='color:#9b59ff; margin:0; font-size:0.9em;'>
            VectorWare is thinking...</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stream response line by line
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=st.session_state.messages,
        stream=True
    )
    
    thinking.empty()
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response
    })
    
    if len(st.session_state.messages) == 2:
        title = prompt[:28] + "..." if len(prompt) > 28 else prompt
        st.session_state.chat_histories.insert(0, {
            "title": title,
            "messages": st.session_state.messages.copy(),
            "time": datetime.now().strftime("%H:%M")
        })
