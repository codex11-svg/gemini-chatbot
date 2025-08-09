import streamlit as st
import os
import time
import google.generativeai as genai

# ==== CONFIG ====
st.set_page_config(page_title="Gemini Chatbot", layout="wide")
MODEL = "gemini-pro"
TYPING_DELAY = 0.03

# ==== SESSION STATE ====
if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "Cyberpunk"

# ==== SIDEBAR THEME SELECT ====
theme_choice = st.sidebar.selectbox(
    "🎨 Choose Theme",
    ["Cyberpunk", "Minimalist", "Classic"],
    index=["Cyberpunk", "Minimalist", "Classic"].index(st.session_state.theme)
)

# If theme changed → rerun
if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.experimental_rerun()

theme = st.session_state.theme

# ==== THEME CSS ====
def apply_theme(theme):
    if theme == "Cyberpunk":
        st.markdown("""
            <style>
                body { background-color: #0a0f1e; color: #00fff7; }
                .stChatMessage {
                    background: linear-gradient(145deg, #111827, #0d1b2a);
                    color: #00fff7;
                    border-radius: 12px;
                    padding: 10px;
                    box-shadow: 0 0 10px #00fff7, 0 0 20px #ff00de;
                    font-family: monospace;
                }
                .stApp { background-color: #0a0f1e; }
            </style>
        """, unsafe_allow_html=True)
    elif theme == "Minimalist":
        st.markdown("""
            <style>
                body { background-color: #ffffff; color: #000000; }
                .stChatMessage {
                    background-color: #f3f4f6;
                    color: #000000;
                    border-radius: 12px;
                    padding: 10px;
                    box-shadow: none;
                    font-family: sans-serif;
                }
                .stApp { background-color: #ffffff; }
            </style>
        """, unsafe_allow_html=True)
    elif theme == "Classic":
        st.markdown("""
            <style>
                body { background-color: #f5f5dc; color: #333333; }
                .stChatMessage {
                    background-color: #fff8dc;
                    color: #333333;
                    border-radius: 12px;
                    padding: 10px;
                    font-family: serif;
                    box-shadow: inset 0 0 5px #aaa;
                }
                .stApp { background-color: #f5f5dc; }
            </style>
        """, unsafe_allow_html=True)

apply_theme(theme)

# ==== GEMINI REPLY FUNCTION ====
def stream_gemini_reply(prompt):
    API_KEY = st.secrets["GEMINI_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = API_KEY
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)

    # Try streaming if available
    if hasattr(model, "stream_generate_content"):
        placeholder = st.empty()
        full_text = ""
        try:
            with model.stream_generate_content(prompt) as stream:
                for chunk in stream:
                    if chunk.text:
                        full_text += chunk.text
                        placeholder.markdown(full_text)
                        time.sleep(TYPING_DELAY)
            return full_text.strip()
        except Exception as e:
            st.warning(f"Streaming failed ({e}), falling back...")
            placeholder.empty()

    # Fallback
    try:
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text.strip() if hasattr(response, "text") else str(response)
    except Exception as e:
        raise RuntimeError(f"Failed to get response: {e}")

# ==== CHAT DISPLAY ====
st.title("🤖 Gemini Chatbot")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==== USER INPUT ====
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        reply_text = stream_gemini_reply(user_input)
        st.markdown(reply_text)

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    
