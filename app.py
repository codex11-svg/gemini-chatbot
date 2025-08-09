import streamlit as st
import google.generativeai as genai
import time

# ===================
# Page Config
# ===================
st.set_page_config(page_title="Gemini Chatbot", layout="centered", page_icon="🤖")

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
# Theme Selection
# ===================
if "theme" not in st.session_state:
    st.session_state.theme = "Cyberpunk"

theme_choice = st.sidebar.radio(
    "🎨 Choose Theme",
    ["Cyberpunk", "Minimalist", "Classic"],
    index=["Cyberpunk", "Minimalist", "Classic"].index(st.session_state.theme)
)

if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.rerun()

THEMES = {
    "Cyberpunk": """
        <style>
        body { background: linear-gradient(135deg, #0f0f0f, #1a0033); color: #00ffcc; font-family: 'Segoe UI', sans-serif; }
        .chat-bubble { background: rgba(0,255,204,0.07); border: 1px solid #00ffcc; box-shadow: 0 0 15px rgba(0,255,204,0.4); }
        .stTextInput>div>div>input { background: rgba(0,0,0,0.5); color: #00ffcc; border-radius: 25px; padding: 12px; border: 1px solid #00ffcc; transition: all 0.3s ease; }
        .stTextInput>div>div>input:focus { box-shadow: 0 0 15px #00ffcc; }
        </style>
    """,
    "Minimalist": """
        <style>
        body { background-color: #f9f9f9; color: #222; font-family: 'Segoe UI', sans-serif; }
        .chat-bubble { background: white; border: 1px solid #ddd; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
        .stTextInput>div>div>input { background: white; color: #222; border-radius: 25px; padding: 12px; border: 1px solid #ccc; transition: all 0.3s ease; }
        .stTextInput>div>div>input:focus { border-color: #4a90e2; box-shadow: 0 0 10px rgba(74,144,226,0.5); }
        </style>
    """,
    "Classic": """
        <style>
        body { background-color: #ececec; color: #2b2b2b; font-family: 'Georgia', serif; }
        .chat-bubble { background: #fff8f0; border: 1px solid #ccc; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stTextInput>div>div>input { background: white; color: #2b2b2b; border-radius: 25px; padding: 12px; border: 1px solid #bbb; transition: all 0.3s ease; }
        .stTextInput>div>div>input:focus { border-color: #a67c52; box-shadow: 0 0 10px rgba(166,124,82,0.5); }
        </style>
    """
}

st.markdown(THEMES[st.session_state.theme], unsafe_allow_html=True)

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
        try:
            response = model.generate_content(prompt, stream=True)
            reply_text = ""
            placeholder = st.empty()
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    reply_text += chunk.text
                    placeholder.markdown(
                        f"<div class='chat-bubble' style='padding:12px; margin:6px; border-radius:15px; max-width:80%;'><b>🤖</b> {reply_text}▌</div>",
                        unsafe_allow_html=True
                    )
                    time.sleep(0.02)
            placeholder.markdown(
                f"<div class='chat-bubble' style='padding:12px; margin:6px; border-radius:15px; max-width:80%;'><b>🤖</b> {reply_text}</div>",
                unsafe_allow_html=True
            )
            return reply_text.strip()
        except TypeError:
            # Fallback if streaming unsupported
            response = model.generate_content(prompt)
            return response.text.strip()
    except Exception as e:
        return f"⚠️ **Error from Gemini API:** {str(e)}"

# ===================
# Display Messages
# ===================
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.container():
        st.markdown(
            f"<div class='chat-bubble' style='padding:12px; margin:6px; border-radius:15px; max-width:80%;'><b>{avatar}</b> {message['content']}</div>",
            unsafe_allow_html=True
        )

# ===================
# Chat Input
# ===================
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Type your message...", key="user_input")
    send = st.form_submit_button("Send 🚀")

if send and user_input:
    # User message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Bot reply (streamed)
    reply_text = stream_gemini_reply(user_input)
    st.session_state.messages.append({"role": "assistant", "content": reply_text})

    st.rerun()
