import streamlit as st
import google.generativeai as genai
import re
import time
import pyperclip

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
.code-block {
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid cyan;
    padding: 12px;
    border-radius: 8px;
    font-family: monospace;
    white-space: pre-wrap;
    position: relative;
}
.copy-btn {
    position: absolute;
    top: 5px;
    right: 5px;
    background: rgba(0, 255, 255, 0.2);
    border: none;
    color: cyan;
    padding: 3px 8px;
    font-size: 12px;
    border-radius: 6px;
    cursor: pointer;
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

# ========================
# Config
# ========================
st.set_page_config(page_title="Cyberpunk AI Chat", page_icon="🤖", layout="wide")
st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
CHAT_USERNAMES = st.secrets["CHAT_USERNAMES"]
CHAT_PASSWORD = st.secrets["CHAT_PASSWORD"]

# ========================
# Session States
# ========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========================
# Login Page
# ========================
def login():
    st.title("🔐 Cyberpunk AI Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in CHAT_USERNAMES and password == CHAT_PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# ========================
# AI Reply Generator
# ========================
def stream_gemini_reply(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# ========================
# Typewriter Effect with Code Block Handling
# ========================
def display_message_with_code_support(message):
    code_blocks = re.findall(r"```(.*?)```", message, re.DOTALL)
    text_parts = re.split(r"```.*?```", message, flags=re.DOTALL)

    for i, part in enumerate(text_parts):
        if part.strip():
            typewriter_effect(part.strip())
        if i < len(code_blocks):
            code = code_blocks[i].strip()
            show_code_block(code)

def typewriter_effect(text):
    placeholder = st.empty()
    words = text.split(" ")
    output = ""
    for w in words:
        output += w + " "
        placeholder.markdown(output)
        time.sleep(0.05)

def show_code_block(code):
    st.markdown(
        f"""
        <div class="code-block">
            <button class="copy-btn" onclick="navigator.clipboard.writeText(`{code}`)">Copy</button>
            <pre>{code}</pre>
        </div>
        """,
        unsafe_allow_html=True
    )

# ========================
# Main Chat UI
# ========================
def chat_ui():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.title("💬 Cyberpunk AI Chatbot")
    
    for msg in st.session_state.messages:
        role_class = "user-message" if msg["role"] == "user" else "bot-message"
        st.markdown(f'<div class="message {role_class}">', unsafe_allow_html=True)
        if msg["role"] == "bot":
            display_message_with_code_support(msg["content"])
        else:
            st.markdown(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    user_input = st.text_input("Type your message...")
    if st.button("Send") and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = stream_gemini_reply(user_input)
        st.session_state.messages.append({"role": "bot", "content": reply})
        st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========================
# App Logic
# ========================
if not st.session_state.authenticated:
    login()
else:
    chat_ui()
    
                
