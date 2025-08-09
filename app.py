import streamlit as st
import google.generativeai as genai
import os
import time

# ==== CONFIG ====
MODEL = "gemini-2.5-flash"
DAY_LIMIT = 25
WAIT_SECONDS = 12

BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712101.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3177/3177440.png"

# ==== PAGE CONFIG ====
st.set_page_config("Gemini Chatbot", page_icon="🤖", layout="centered")

# ==== SESSION STATE ====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

# ==== CSS STYLE ====
st.markdown("""
<style>
body {background-color: #161A23;}
.chat-container {max-width: 700px; margin: auto;}
.chat-bubble-user {
    background: linear-gradient(95deg, #141828 80%, #0fa 180%);
    color: #12fff7;
    border-radius: 16px;
    padding: 10px 18px;
    max-width: 70%;
    font-family: monospace;
    font-size: 1.1em;
    border-bottom-right-radius: 3px;
    border-top-left-radius: 3px;
    box-shadow: 0 2px 6px #00ffe033;
    animation: fadeIn 0.4s ease-in-out;
}
.chat-bubble-bot {
    background: linear-gradient(95deg, #212121 70%, #ffe57f44 160%);
    color: #ffe57f;
    border-radius: 16px;
    padding: 10px 18px;
    max-width: 70%;
    font-family: monospace;
    font-size: 1.1em;
    border-bottom-left-radius: 3px;
    border-top-right-radius: 3px;
    box-shadow: 0 2px 6px #fff6b022;
    animation: fadeIn 0.4s ease-in-out;
}
@keyframes fadeIn {from {opacity: 0; transform: translateY(4px);} to {opacity: 1; transform: translateY(0);}}
.typing {
    font-family: monospace;
    color: #12fff7;
    font-size: 1.05em;
}
.typing span {animation: blink 1s infinite;}
.typing span:nth-child(2) {animation-delay: 0.2s;}
.typing span:nth-child(3) {animation-delay: 0.4s;}
@keyframes blink {0% {opacity: 1;} 50% {opacity: 0.2;} 100% {opacity: 1;}}
</style>
""", unsafe_allow_html=True)

# ==== FUNCTIONS ====
def styled_message(msg, sender):
    avatar = USER_AVATAR if sender == "user" else BOT_AVATAR
    bubble_class = "chat-bubble-user" if sender == "user" else "chat-bubble-bot"
    align = "flex-end" if sender == "user" else "flex-start"
    st.markdown(
        f"<div style='display:flex; align-items:flex-start; justify-content:{align}; margin-bottom:4px;'>"
        f"<img src='{avatar}' height='36' style='border-radius:50%; margin:4px;'>"
        f"<div class='{bubble_class}'>{msg}</div></div>",
        unsafe_allow_html=True
    )

def stream_gemini_reply(prompt):
    """Stream response from Gemini word-by-word."""
    API_KEY = st.secrets["GEMINI_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = API_KEY
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)

    stream_placeholder = st.empty()
    full_text = ""
    with model.stream_generate_content(prompt) as stream:
        for chunk in stream:
            if chunk.text:
                full_text += chunk.text
                stream_placeholder.markdown(full_text)  # Live update
                time.sleep(0.015)
    return full_text.strip()

# ==== HEADER ====
st.markdown("<h2 style='text-align:center;color:white;'>🤖 Gemini Chatbot</h2>", unsafe_allow_html=True)

# ==== RESET BUTTON ====
if st.button("♻️ Reset Chat"):
    st.session_state.chat_history.clear()
    st.session_state.request_count = 0

# ==== SHOW CHAT HISTORY ====
for who, msg in st.session_state.chat_history:
    styled_message(msg, who)

# ==== INPUT FORM ====
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([8, 1])
    user_input = cols[0].text_area("Type a message...", key="user_text", height=80, label_visibility="collapsed")
    send_button = cols[1].form_submit_button("Send")

# ==== HANDLE SEND ====
if send_button and user_input.strip():
    now = time.time()
    if now - st.session_state.last_request_time < WAIT_SECONDS:
        st.warning(f"⚡ Wait {round(WAIT_SECONDS - (now - st.session_state.last_request_time), 1)}s.")
        st.stop()
    if st.session_state.request_count >= DAY_LIMIT:
        st.error("🛑 Daily quota reached.")
        st.stop()

    # Show user message
    st.session_state.chat_history.append(("user", user_input))
    styled_message(user_input, "user")

    # Typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown('<div class="typing">Gemini is typing<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)

    # Stream bot reply
    reply_text = stream_gemini_reply(user_input)
    typing_placeholder.empty()

    st.session_state.chat_history.append(("bot", reply_text))
    styled_message(reply_text, "bot")

    st.session_state.last_request_time = now
    st.session_state.request_count += 1
        
