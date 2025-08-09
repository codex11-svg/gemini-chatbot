import streamlit as st
import google.generativeai as genai

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

# ===================
# Model Name
# ===================
MODEL = "gemini-1.5-flash"  # safer default than gemini-pro

# ===================
# Theme Switching
# ===================
if "theme" not in st.session_state:
    st.session_state.theme = "Cyberpunk"

theme_choice = st.sidebar.selectbox(
    "🎨 Choose Theme",
    ["Cyberpunk", "Minimalist", "Classic"],
    index=["Cyberpunk", "Minimalist", "Classic"].index(st.session_state.theme)
)

if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.rerun()

theme = st.session_state.theme

# ===================
# Theme CSS
# ===================
THEMES = {
    "Cyberpunk": """
        <style>
        body { background-color: #0f0f0f; color: #00ff9f; }
        .stChatMessage { background: #1a1a1a; border-radius: 12px; padding: 8px; }
        </style>
    """,
    "Minimalist": """
        <style>
        body { background-color: #ffffff; color: #000000; }
        .stChatMessage { background: #f5f5f5; border-radius: 12px; padding: 8px; }
        </style>
    """,
    "Classic": """
        <style>
        body { background-color: #f0f0f0; color: #333333; }
        .stChatMessage { background: #ffffff; border-radius: 12px; padding: 8px; }
        </style>
    """
}

st.markdown(THEMES[theme], unsafe_allow_html=True)

# ===================
# Session State for Chat
# ===================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===================
# Gemini Response Function
# ===================
def stream_gemini_reply(prompt):
    try:
        model = genai.GenerativeModel(MODEL)

        # Try streaming mode
        try:
            response = model.generate_content(prompt, stream=True)
            reply_text = ""
            for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    reply_text += chunk.text
            return reply_text.strip()

        except TypeError:
            # Fallback to non-streaming if streaming not supported
            response = model.generate_content(prompt)
            return response.text.strip()

    except Exception as e:
        return f"⚠️ **Error from Gemini API:** {str(e)}"

# ===================
# Show Previous Messages
# ===================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===================
# Chat Input UI
# ===================
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:", key="user_input")
    send = st.form_submit_button("Send 🚀")

if send and user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get model reply
    reply_text = stream_gemini_reply(user_input)

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    with st.chat_message("assistant"):
        st.markdown(reply_text)
