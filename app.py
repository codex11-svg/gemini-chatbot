import streamlit as st
import google.generativeai as genai
import re
import time

# ========================
# Cyberpunk Theme CSS
# ========================
CYBERPUNK_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="stApp"] {
    margin: 0;
    font-family: 'Orbitron', sans-serif !important;
    background: linear-gradient(270deg, #0f0c29, #302b63, #24243e);
    background-size: 600% 600%;
    animation: gradientShift 20s ease infinite;
    color: #fff !important;
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stTextInput > div > div > input, .stPasswordInput > div > div > input {
    background: rgba(0,0,0,0.6);
    color: cyan !important;
    border: 1px solid cyan;
    border-radius: 8px;
}
.stButton > button {
    background: rgba(0,255,255,0.1);
    border: 1px solid cyan;
    color: cyan;
    font-weight: bold;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background: rgba(0,255,255,0.3);
    box-shadow: 0 0 10px cyan;
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
<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
}
</script>
"""

# ========================
# Authentication
# ========================
VALID_USERS = {
    "admin": "1126",
    "Nihal": "1126",
    "nihal": "1126",
    "Zainab": "1126",
    "zainab": "1126"
}

st.set_page_config(page_title="Cyberpunk Chatbot", layout="wide")
st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Cyberpunk Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# ========================
# Chatbot Setup
# ========================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display past messages
for msg in st.session_state.messages:
    role_class = "user-message" if msg["role"] == "user" else "bot-message"
    copy_button = f'<button class="copy-btn" onclick="copyToClipboard(`{msg["content"]}`)">Copy</button>' if msg["role"] == "assistant" else ""
    st.markdown(f'<div class="message {role_class}">{copy_button}{msg["content"]}</div>', unsafe_allow_html=True)

# ========================
# Input + AI reply
# ========================
user_input = st.text_input("Type your message...", key="user_input", placeholder="Ask me anything...")

def stream_reply(prompt):
    response = model.generate_content(prompt)
    text = response.text
    words = text.split()
    displayed = ""
    placeholder = st.empty()
    for word in words:
        displayed += word + " "
        placeholder.markdown(f'<div class="message bot-message">{displayed}</div>', unsafe_allow_html=True)
        time.sleep(0.05)
    return text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    ai_reply = stream_reply(user_input)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)
