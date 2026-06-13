import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="VectorWare AI",
    page_icon="🌀",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0d0015, #1a0030, #0d0015);
        color: white !important;
    }
    
    .stChatInput input {
        background-color: #2a0050 !important;
        color: white !important;
        border: 2px solid #bf00ff !important;
        border-radius: 25px !important;
        box-shadow: 0 0 15px rgba(191, 0, 255, 0.7),
                    0 0 30px rgba(123, 47, 255, 0.4) !important;
    }
    
    .stChatMessage {
        background: rgba(123, 47, 255, 0.15) !important;
        border: 1px solid #bf00ff !important;
        border-radius: 15px !important;
        padding: 10px !important;
        box-shadow: 0 0 25px rgba(191, 0, 255, 0.6), 
                    0 0 50px rgba(123, 47, 255, 0.3),
                    inset 0 0 20px rgba(123, 47, 255, 0.1) !important;
    }
    
    .stChatMessage p, .stChatMessage li, .stChatMessage span {
        color: white !important;
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
        padding: 30px 0 10px 0;
    }
    
    .logo-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8em;
        background: linear-gradient(90deg, #bf00ff, #7b2fff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .tagline {
        color: #bb88ff !important;
        font-size: 1em;
        letter-spacing: 2px;
        margin-top: 5px;
    }
    
    .glow-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #7b2fff, #bf00ff, #7b2fff, transparent);
        margin: 20px 0;
        box-shadow: 0 0 15px #7b2fff, 0 0 30px #bf00ff;
    }
    
    .spiral-container {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 20px #7b2fff);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { filter: drop-shadow(0 0 10px #7b2fff); }
        50% { filter: drop-shadow(0 0 30px #bf00ff); }
        100% { filter: drop-shadow(0 0 10px #7b2fff); }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-container">
        <div class="spiral-container">
            <svg width="110" height="110" viewBox="0 0 200 200">
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

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("🌀 Ask VectorWare AI anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
