import streamlit as st
import google.generativeai as genai
import time
import re

# ===================
# Page Config
# ===================
st.set_page_config(page_title="Cyberpunk Gemini Chat", layout="centered", page_icon="🤖")

# ===================
# Load API Key
# ===================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY not found in Streamlit secrets. Please add it in settings.")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

MODEL = "gemini-1.5-flash"

# ===================
# Login System
# ===================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:#00ffcc;'>🔐 Cyberpunk Gemini Chat</h1>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.secrets.get("CHAT_USERNAMES", ["admin"]) and password == st.secrets.get("CHAT_PASSWORD", "1234"):

            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

# ===================
# Cyberpunk Theme + Animation
# ===================
CYBERPUNK_CSS = """
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.chat-bubble {
    animation: fadeIn 0.4s ease forwards;
}
body {
    background: linear-gradient(135deg, #0f0f0f, #1a0033);
    color: #00ffcc;
    font-family: 'Segoe UI', sans-serif;
}
.chat-bubble {
    background: rgba(0,255,204,0.07);
    border: 1px solid #00ffcc;
    box-shadow: 0 0 15px rgba(0,255,204,0.4);
    border-radius: 15px;
    padding: 12px;
    margin: 6px;
    max-width: 80%;
    position: relative;
}
.copy-btn {
    position: absolute;
    top: 5px;
    right: 8px;
    background: none;
    border: none;
    color: #00ffcc;
    cursor: pointer;
    font-size: 14px;
}
.stTextInput>div>div>input {
    background: rgba(0,0,0,0.5);
    color: #00ffcc;
    border-radius: 25px;
    padding: 12px;
    border: 1px solid #00ffcc;
    transition: all 0.3s ease;
}
.stTextInput>div>div>input:focus {
    box-shadow: 0 0 15px #00ffcc;
}
</style>
"""
st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

# ===================
# Session State
# ===================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===================
# Gemini Streaming
# ===================
def stream_gemini_reply(prompt):
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt, stream=True)
        reply_text = ""
        placeholder = st.empty()
        for chunk in response:
            if hasattr(chunk, "text") and chunk.text:
                reply_text += chunk.text
                placeholder.markdown(
                    f"<div class='chat-bubble'><b>🤖</b> {reply_text}▌</div>",
                    unsafe_allow_html=True
                )
                time.sleep(0.02)
        placeholder.markdown(format_with_copy_button(f"🤖 {reply_text}"), unsafe_allow_html=True)
        return reply_text.strip()
    except Exception as e:
        return f"⚠️ **Error from Gemini API:** {str(e)}"

# ===================
# Format with Copy Button
# ===================
def format_with_copy_button(text):
    escaped = text.replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
    return f"""
    <div class='chat-bubble'>
        <b>{text[0:2]}</b> {text[2:]}
        <button class='copy-btn' onclick="navigator.clipboard.writeText('{escaped}')">📋</button>
    </div>
    """

# ===================
# Display Messages
# ===================
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(format_with_copy_button(f"🤖 {message['content']}"), unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble'><b>👤</b> {message['content']}</div>", unsafe_allow_html=True)

# ===================
# Chat Input
# ===================
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Type your message...")
    send = st.form_submit_button("Send 🚀")

if send and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply_text = stream_gemini_reply(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    st.rerun()
    
