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
        color: white;
    }
    .stChatInput input {
        background-color: #2a0050 !important;
        color: white !important;
        border: 2px solid #7b2fff !important;
        border-radius: 25px !important;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid #7b2fff !important;
        border-radius: 15px !important;
        padding: 10px !important;
        box-shadow: 0 0 20px rgba(123, 47, 255, 0.5) !important;
        color: white !important;
    }
    .stChatMessage p {
        color: white !important;
        text-align: left !important;
    }
    [data-testid="stChatMessageContent"] p {
        color: white !important;
    }
    [data-testid="stChatMessageContent"] li {
        color: white !important;
    }
    [data-testid="stChatMessageContent"] strong {
        color: #cc99ff !important;
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
    }
    .tagline {
        color: #bb88ff;
        font-size: 1em;
        letter-spacing: 2px;
        margin-top: 5px;
    }
    .glow-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #7b2fff, #bf00ff, transparent);
        margin: 20px 0;
        box-shadow: 0 0 10px #7b2fff;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-container">
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
