import streamlit as st
import google.generativeai as genai
import time

# ---- Cyberpunk theme ----
CYBERPUNK_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="stApp"] {
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
.stTextInput > div > div > input {
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
    word-break: break-word;
}
.user-message {
    background: rgba(0,255,150,0.15);
    border: 1px solid rgba(0,255,150,0.4);
}
.bot-message {
    background: rgba(0,200,255,0.15);
    border: 1px solid rgba(0,200,255,0.4);
}
.copy-btn {
    background: rgba(0,255,255,0.2);
    border: none;
    color: cyan;
    padding: 3px 8px;
    font-size: 12px;
    border-radius: 6px;
    cursor: pointer;
    float: right;
}
.copy-btn:hover {
    background: rgba(0,255,255,0.35);
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}
.blink {
    animation: blinker 1s linear infinite;
}
@keyframes blinker { 50% { opacity: 0.4; } }
</style>
"""

st.set_page_config(page_title="Cyberpunk Gemini Chatbot", layout="wide")
st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

# --- Gemini Setup (API Key from Secrets) ----
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# --- Chat State ----
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<h1 style="font-family:Orbitron,sans-serif;text-align:center;color:cyan;">🤖 Cyberpunk Gemini Chatbot</h1>', unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role_class = "user-message" if msg["role"] == "user" else "bot-message"
    content_safe = msg["content"].replace("`", "\\`")
    copy_button = f'<button class="copy-btn" onclick="navigator.clipboard.writeText(`{content_safe}`)">Copy</button>' if msg["role"] == "assistant" else ""
    st.markdown(f'<div class="message {role_class}">{copy_button}{msg["content"]}</div>', unsafe_allow_html=True)

user_input = st.text_input("Type your message...", key="user_input", placeholder="Ask me anything...")

def show_typing():
    st.markdown(
        '<div class="message bot-message"><span class="blink">Gemini is typing<span>.</span><span>.</span><span>.</span></span></div>',
        unsafe_allow_html=True
    )

def stream_reply(prompt):
    response = model.generate_content(prompt)
    text = response.text
    words = text.split()
    displayed = ""
    placeholder = st.empty()
    for word in words:
        displayed += word + " "
        placeholder.markdown(f'<div class="message bot-message">{displayed}</div>', unsafe_allow_html=True)
        time.sleep(0.035)
    return text

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    show_typing()
    ai_reply = stream_reply(user_input)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)
