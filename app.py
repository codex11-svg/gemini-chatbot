import streamlit as st
import google.generativeai as genai
import re
import time
from html import escape

# ---------- CONFIG ----------
st.set_page_config(page_title="Cyberpunk AI Chat", page_icon="🤖", layout="centered")

# Load secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
ALLOWED_USERS = st.secrets["CHAT_USERNAMES"]
PASSWORD = st.secrets["CHAT_PASSWORD"]

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ---------- CYBERPUNK CSS ----------
CYBERPUNK_CSS = """
<style>
body {
    margin: 0;
    background: linear-gradient(270deg, #0f0c29, #302b63, #24243e);
    background-size: 600% 600%;
    animation: gradientShift 20s ease infinite;
    font-family: 'Orbitron', sans-serif;
    color: #fff;
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.chat-container {
    max-width: 800px;
    margin: auto;
    background: rgba(25, 25, 35, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 255, 255, 0.4);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);
}
.message {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    animation: fadeIn 0.3s ease;
}
.user-message {
    background: rgba(0, 255, 150, 0.15);
    border: 1px solid rgba(0, 255, 150, 0.4);
}
.bot-message {
    background: rgba(0, 200, 255, 0.15);
    border: 1px solid rgba(0, 200, 255, 0.4);
}
.copy-btn {
    background: rgba(0, 255, 255, 0.2);
    border: none;
    color: cyan;
    padding: 3px 8px;
    font-size: 12px;
    border-radius: 6px;
    cursor: pointer;
    float: right;
}
.copy-btn:hover {
    background: rgba(0, 255, 255, 0.35);
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""

# ---------- LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;color:cyan;'>🔐 Cyberpunk AI Login</h1>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        if username in ALLOWED_USERS and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Access Granted ✅")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# ---------- CHAT ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;color:cyan;'>🤖 Cyberpunk AI Chat</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role_class = "user-message" if msg["role"] == "user" else "bot-message"
        if msg["role"] == "bot" and msg.get("is_code"):
            st.markdown(f"<div class='message {role_class}'><pre><code>{escape(msg['content'])}</code></pre><button class='copy-btn' onclick='navigator.clipboard.writeText(`{escape(msg['content'])}`)'>Copy</button></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='message {role_class}'>{escape(msg['content'])}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- INPUT ----------
user_input = st.chat_input("Type your message...")
if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.experimental_rerun()

# If last message is user -> get AI reply
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_msg = st.session_state.messages[-1]["content"]
    bot_msg = ""
    placeholder = st.empty()

    try:
        response = model.generate_content(user_msg, stream=True)
        for chunk in response:
            if chunk.text:
                words = chunk.text.split()
                for w in words:
                    bot_msg += w + " "
                    placeholder.markdown(f"<div class='message bot-message'>{escape(bot_msg)}</div>", unsafe_allow_html=True)
                    time.sleep(0.05)  # word-by-word delay
        # Detect if code
        is_code = bool(re.search(r"```[\s\S]*```", bot_msg))
        st.session_state.messages.append({"role": "bot", "content": bot_msg.strip(), "is_code": is_code})
        st.experimental_rerun()
    except Exception as e:
        st.session_state.messages.append({"role": "bot", "content": f"⚠️ Error: {str(e)}"})
        st.experimental_rerun()
                
