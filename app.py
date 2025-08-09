import streamlit as st
import google.generativeai as genai
import time

# ===================
# Streamlit Page Config
# ===================
st.set_page_config(page_title="Gemini Chatbot", layout="centered")

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
# Theme Setup
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
        body { background-color: #0d0d0d; color: #00ffcc; font-family: 'Segoe UI', sans-serif; }
        .chat-bubble { background: rgba(0,255,204,0.1); border: 1px solid #00ffcc; }
        .stTextInput>div>div>input { background: #111; color: #00ffcc; border-radius: 25px; padding: 10px; border: 1px solid #00ffcc; }
        </style>
    """,
    "Minimalist": """
        <style>
        body { background-color: #fefefe; color: #000; font-family: 'Segoe UI', sans-serif; }
        .chat-bubble { background: #f5f5f5; border: 1px solid #ddd; }
        .stTextInput>div>div>input { background: #fff; color: #000; border-radius: 25px; padding: 10px; border: 1px solid #ccc; }
        </style>
    """,
    "Classic": """
        <style>
        body { background-color: #e9ecef; color: #212529; font-family: 'Georgia', serif; }
        .chat-bubble { background: #fff; border: 1px solid #ccc; }
        .stTextInput>div>div>input { background: #fff; color: #212529; border-radius: 25px; padding: 10px; border: 1px solid #ccc; }
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
# Gemini API Call
# ===================
def stream_gemini_reply(prompt):
    try:
        model = genai.GenerativeModel(MODEL)
        try:
            response = model.generate_content(prompt, stream=True)
            reply_text = ""
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    reply_text += chunk.text
            return reply_text.strip()
        except TypeError:
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
        st.markdown(f"""
        <div class='chat-bubble' style='padding:12px; margin:6px; border-radius:15px; max-width:80%;'>
            <b>{avatar}</b> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

# ===================
# Chat Input
# ===================
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("💬 Type your message...", key="user_input")
    send = st.form_submit_button("Send 🚀")

if send and user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Typing indicator
    with st.container():
        typing_box = st.empty()
        typing_box.markdown(
            "<i>🤖 Gemini is typing...</i>",
            unsafe_allow_html=True
        )
        time.sleep(0.5)

    # Get model reply
    reply_text = stream_gemini_reply(user_input)
    typing_box.empty()

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    st.rerun()
    
