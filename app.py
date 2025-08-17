import streamlit as st
import google.generativeai as genai
import time

# -- Cyberpunk Theme --
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Cyberpunk Gemini Chatbot", layout="wide")

# -- Configure Gemini --
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")  # <- use this (if works in your environment)

if "chat" not in st.session_state:
    st.session_state.chat = []

st.title("🤖 Cyberpunk Gemini Chatbot")
st.markdown("<div style='max-width:700px;margin:auto;'>",unsafe_allow_html=True)

for turn in st.session_state.chat:
    if turn['role'] == 'user':
        st.markdown(f"<div style='background:#222;border-radius:7px;padding:8px 13px;color:#28f6bf;margin-bottom:8px;'>{turn['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#23314B;border-radius:7px;padding:8px 13px;color:#20ddff;margin-bottom:14px;'>{turn['content']}</div>", unsafe_allow_html=True)

user_input = st.text_input("Type a message and press Enter...", key="user_input", placeholder="Say hi to Gemini!")

if user_input:
    st.session_state.chat.append({"role":"user", "content":user_input})
    wait_msg = st.empty()
    wait_msg.markdown("<span style='color:#19f9d8;'>Gemini is typing ...</span>", unsafe_allow_html=True)
    try:
        response = model.generate_content([user_input])
        ai_msg = getattr(response, "text", None) or str(response)
    except Exception as e:
        ai_msg = f"Error: {e}"
    wait_msg.empty()
    st.session_state.chat.append({"role":"bot","content":ai_msg})
    st.experimental_rerun()

st.markdown("</div>",unsafe_allow_html=True)
