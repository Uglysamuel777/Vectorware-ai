import streamlit as st
from groq import Groq
from datetime import datetime
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VectorWare AI",
    page_icon="🌀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- MODERN ULTRA-DARK THEME & ANIMATIONS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Core App Reset */
    * { font-family: 'Inter', sans-serif !important; }
    
    .stApp {
        background-color: #05050a;
        color: #f3f4f6 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #090914 !important;
        border-right: 1px solid rgba(123, 47, 255, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    
    /* Elegant Chat Input */
    .stChatInputContainer {
        padding: 0 !important;
        background: transparent !important;
    }
    
    .stChatInput input {
        background-color: #0f0f1e !important;
        color: #ffffff !important;
        border: 1px solid rgba(123, 47, 255, 0.2) !important;
        border-radius: 24px !important;
        padding: 12px 20px !important;
    }
    
    .stChatInput input:focus {
        border-color: rgba(123, 47, 255, 0.6) !important;
        box-shadow: 0 0 15px rgba(123, 47, 255, 0.2) !important;
    }
    
    /* Chat Messages Styles */
    .stChatMessage {
        background-color: transparent !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        padding: 20px 0 !important;
    }
    
    [data-testid="stChatMessageContent"] p {
        color: #e2e8f0 !important;
        line-height: 1.75 !important;
        font-size: 102rem !important;
    }
    
    [data-testid="stChatMessageContent"] strong {
        color: #c084fc !important;
        font-weight: 600;
    }
    
    /* Continuous Spiral Logo Glow Pulse */
    @keyframes spiralGlow {
        0%, 100% { filter: drop-shadow(0 0 8px rgba(147, 51, 234, 0.4)); }
        50% { filter: drop-shadow(0 0 22px rgba(6, 182, 212, 0.6)); }
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
    
    /* Typography Overrides */
    .greeting-title {
        font-size: 2.5rem;
        font-weight: 300;
        color: #ffffff;
        margin-bottom: 0px;
        letter-spacing: -0.025em;
    }
    
    .greeting-sub {
        font-size: 2.8rem;
        font-weight: 600;
        background: linear-gradient(135deg, #a855f7, #ec4899, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 0px;
        margin-bottom: 10px;
        letter-spacing: -0.025em;
    }
    
    /* Modular Interface Containers */
    .about-card {
        background: rgba(123, 47, 255, 0.04);
        border: 1px solid rgba(123, 47, 255, 0.12);
        border-radius: 16px;
        padding: 16px;
        margin-top: 20px;
    }
    
    .founder-pill {
        background: rgba(147, 51, 234, 0.1);
        border: 1px solid rgba(147, 51, 234, 0.2);
        border-radius: 8px;
        padding: 6px 12px;
        margin-top: 6px;
        font-size: 0.8rem;
        color: #d8b4fe !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Voice Controller Utilities */
    .mic-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        padding-top: 4px;
    }

    .mic-btn {
        background: #0f0f1e;
        border: 1px solid rgba(123, 47, 255, 0.25);
        border-radius: 50%;
        width: 44px;
        height: 44px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    
    .mic-btn:hover {
        background: rgba(123, 47, 255, 0.15);
        border-color: rgba(123, 47, 255, 0.6);
        box-shadow: 0 0 12px rgba(123, 47, 255, 0.3);
    }
    
    .mic-svg {
        width: 18px;
        height: 18px;
        fill: #a78bfa;
    }
    
    /* Clean System Button Adjustments */
    .stButton > button {
        border-radius: 12px !important;
        font-size: 0.9rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE STATE INITIALIZERS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []

# --- SIDEBAR COMPONENT ---
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 20px 0;'>
            <div class='spiral-idle'>
                <svg width="40" height="40" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="sideGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#a855f7"/>
                            <stop offset="100%" style="stop-color:#06b6d4"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#sideGlow)" stroke-width="16" 
                          stroke-linecap="round"/>
                </svg>
            </div>
            <h2 style='font-size:1.15rem; color:#ffffff; margin:8px 0 0 0; font-weight:500; letter-spacing:0.5px;'>VectorWare AI</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("✦ New Session", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.sidebar.success("New context started.")
        st.rerun()
    
    st.markdown("<hr style='margin: 15px 0; border:0; border-top:1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280; font-size:0.75rem; font-weight:600; margin-bottom:8px;'>RECENT CHATS</p>", unsafe_allow_html=True)
    
    if not st.session_state.chat_histories:
        st.markdown("<p style='color:#4b5563; font-size:0.8rem; font-style:italic;'>No history saved</p>", unsafe_allow_html=True)
    else:
        for idx, chat in enumerate(st.session_state.chat_histories[:6]):
            if st.button(f"🕒 {chat['title']}", key=f"hist_{idx}", use_container_width=True):
                st.session_state.messages = chat["messages"]
                st.rerun()
                
    st.markdown("""
        <div class='about-card'>
            <p style='color:#a855f7; font-size:0.85rem; font-weight:600; margin:0 0 6px 0;'>🏢 Corporate Identity</p>
            <p style='color:#9ca3af; font-size:0.78rem; line-height:1.5; margin:0 0 12px 0;'>
            Next-generation AI & cloud platforms engineered to deliver highly optimized autonomous enterprise processes.
            </p>
            <p style='color:#4b5563; font-size:0.7rem; font-weight:600; margin:0 0 4px 0; letter-spacing:0.5px;'>FOUNDERS</p>
            <div class='founder-pill'>⚡ Samuel Frimpong</div>
            <div class='founder-pill'>💡 Cardinal Kofi Nsiah</div>
            <p style='color:#374151; font-size:0.65rem; text-align:center; margin:15px 0 0 0;'>© 2026 VectorWare Inc.</p>
        </div>
    """, unsafe_allow_html=True)


# --- MAIN RUNTIME INTERFACE ---
# Initialize internal client instance
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Missing configuration: Ensure GROQ_API_KEY is defined inside your secrets container.")
    st.stop()

# Empty Landing Stage Display
if not st.session_state.messages:
    st.markdown("""
        <div style='padding-top: 40px; padding-bottom: 20px;'>
            <div class='spiral-idle' style='margin-bottom: 15px;'>
                <svg width="55" height="55" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="mainGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#a855f7"/>
                            <stop offset="50%" style="stop-color:#ec4899"/>
                            <stop offset="100%" style="stop-color:#06b6d4"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#mainGlow)" stroke-width="16" 
                          stroke-linecap="round"/>
                </svg>
            </div>
            <h1 class='greeting-title'>Welcome to Next-Gen Compute,</h1>
            <h1 class='greeting-sub'>I am VectorWare AI</h1>
            <p style='color:#6b7280; font-size:1rem; margin-bottom: 30px;'>What system architectures or applications are we developing today?</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Suggestion Dashboard Matrix
    suggestions = [
        ("🎨", "Design a modern UI layout for a corporate fintech site"),
        ("📈", "Analyze key trading indicators for systematic forex engines"),
        ("🤖", "Explain deployment patterns for enterprise AI automation"),
        ("✍️", "Draft a high-converting pitch deck intro for engineering startups")
    ]
    
    s_col1, s_col2 = st.columns(2)
    for index, (icon, text) in enumerate(suggestions):
        target_col = s_col1 if index % 2 == 0 else s_col2
        if target_col.button(f"{icon} &nbsp; {text}", key=f"sug_btn_{index}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": text})
            st.rerun()

# Render Static Active History Stack
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- PERSISTENT FOOTER LAYOUT (INPUT + CONTROLS) ---
input_layout, mic_layout = st.columns([0.88, 0.12])

with mic_layout:
    st.markdown("""
        <div class="mic-wrap">
            <button class='mic-btn' id='micBtn' onclick='triggerSpeechEngine()'>
                <svg class='mic-svg' viewBox="0 0 24 24">
                    <path d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4zm0 2a2 2 0 0 1 2 2v6a2 2 0 0 1-4 0V5a2 2 0 0 1 2-2zm-1 15.93V21h2v-2.07A8 8 0 0 0 20 11h-2a6 6 0 0 1-12 0H4a8 8 0 0 0 7 7.93z"/>
                </svg>
            </button>
        </div>
        
        <script>
        function triggerSpeechEngine() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) { 
                alert('Web Speech API is unavailable in this browser. Please verify system permissions or shift to Chrome.'); 
                return; 
            }
            const engine = new SpeechRec();
            engine.lang = 'en-US';
            engine.interimResults = false;
            const targetBtn = document.getElementById('micBtn');
            
            engine.onstart = () => {
                targetBtn.style.background = 'rgba(236, 72, 153, 0.2)';
                targetBtn.style.borderColor = '#ec4899';
            };
            engine.onresult = (event) => {
                const speechOutput = event.results[0][0].transcript;
                const nativeField = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if (nativeField) {
                    nativeField.value = speechOutput;
                    nativeField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            engine.onerror = (err) => { console.error('Speech Engine Error Handled:', err.error); };
            engine.onend = () => {
                targetBtn.style.background = '#0f0f1e';
                targetBtn.style.borderColor = 'rgba(123, 47, 255, 0.25)';
            };
            engine.start();
        }
        </script>
    """, unsafe_allow_html=True)

with input_layout:
    prompt = st.chat_input("Ask VectorWare AI anything...")

# --- RESPONSE BLOCK MANAGEMENT ---
if prompt:
    # Append input statement instantly
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Inject Context-Aware Spinning Thinking State Loader
    thinking_indicator = st.empty()
    thinking_indicator.markdown("""
        <div style='display:flex; align-items:center; gap:14px; padding: 15px 0;'>
            <div class='spiral-thinking'>
                <svg width="30" height="30" viewBox="0 0 200 200">
                    <defs>
                        <linearGradient id="thinkGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#a855f7"/>
                            <stop offset="100%" style="stop-color:#06b6d4"/>
                        </linearGradient>
                    </defs>
                    <path d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 
                             C90,165 50,140 40,100 C25,50 60,15 100,15 
                             C150,15 185,55 185,100 C185,155 140,190 90,185"
                          fill="none" stroke="url(#thinkGlow)" stroke-width="16" 
                          stroke-linecap="round"/>
                </svg>
            </div>
            <p style='color:#a855f7; margin:0; font-size:0.9rem; font-weight: 500; letter-spacing: 0.3px;'>Synthesizing response vector...</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Fire LLM Stream Request
    try:
        network_stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True
        )
    except Exception as e:
        thinking_indicator.empty()
        st.error(f"Upstream Engine connectivity error: {str(e)}")
        st.stop()
        
    thinking_indicator.empty()
    
    # Process Word-By-Word Claude Style Fluid Display Output
    with st.chat_message("assistant"):
        ui_placeholder = st.empty()
        collected_content = ""
        
        for payload_chunk in network_stream:
            chunk_text = payload_chunk.choices[0].delta.content
            if chunk_text:
                # To bring word-by-word/line-by-line cadence instead of raw fast dumping
                for character in chunk_text:
                    collected_content += character
                    ui_placeholder.markdown(collected_content + "▌")
                    time.sleep(0.006)  # Controlled natural typing throttle delay
                    
        ui_placeholder.markdown(collected_content)
        
    # Commit responses to session storage array
    st.session_state.messages.append({"role": "assistant", "content": collected_content})
    
    # Automatically compute new chat headers
    if len(st.session_state.messages) == 2:
        computed_title = prompt if len(prompt) <= 24 else f"{prompt[:24]}..."
        st.session_state.chat_histories.insert(0, {
            "title": computed_title,
            "messages": list(st.session_state.messages),
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()
