import streamlit as st
import google.generativeai as genai
import os
import time
import base64

# == Gemini Model and Quotas ==
MODEL = "gemini-2.5-flash"
DAY_LIMIT = 25
WAIT_SECONDS = 12

# == Secure API Key - Use Streamlit Secrets ==
API_KEY = st.secrets["GEMINI_API_KEY"]  # Set in Streamlit Cloud only!
os.environ["GOOGLE_API_KEY"] = API_KEY
genai.configure(api_key=API_KEY)

# == Avatars ==
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712101.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3177/3177440.png"

# == Themes ==
CYBERPUNK_CSS = """
<style>
body {background: #161A23;}
.theme-bar {
    background: linear-gradient(92deg, #232857 50%, #02fff0 180%);
    padding: 14px 20px 8px 20px; border-radius: 18px 18px 0 0; box-shadow: 0 2px 14px #00ffe088;
    color: #fff; font-size:1.45em; font-family: 'Fira Mono', monospace; letter-spacing:.04em;}
.technote {color: #03fff6; margin-top: 0.28em;}
.chat-bubble-user {background: linear-gradient(95deg, #141828 80%, #0fa 180%);
    color: #12fff7; border-radius: 16px; padding: 10px 18px 10px 18px; max-width: 70%; align-self: flex-end;
    font-family: 'Fira Mono', monospace; font-size: 1.11em;
    border-bottom-right-radius: 3px; border-top-left-radius: 3px;
    box-shadow: 0 1.5px 8px #00ffe033; border: 1px solid #2acfcf77;}
.chat-bubble-bot {background: linear-gradient(95deg,#212121 70%,#ffe57f44 160%);
    color: #ffe57f; border-radius: 16px; padding: 10px 20px 10px 18px; max-width: 70%; align-self: flex-start;
    font-family: 'Fira Mono', monospace; font-size: 1.11em;
    border-bottom-left-radius: 3px; border-top-right-radius: 3px;
    box-shadow: 0 1.5px 8px #fff6b022; border: 1px solid #ffe57f64;}
.hr-sep {border: 0; height: 1.7px; background: #232d3b; margin: 1.0em 0;}
.stTextInput > div > div > input {background: #191c33 !important;
  color: #abfaff !important; border: 1px solid #12fff788 !important; font-family: 'Fira Mono', monospace;}
</style>
"""
LIGHT_CSS = """
<style>
body {background: #f7faff;}
.theme-bar {background: linear-gradient(92deg, #e0e9e9 60%, #9ecbee 100%);
    padding:16px; border-radius:18px 18px 0 0; color: #283147; font-size:1.42em;}
.technote {color:#1e77e6;}
.chat-bubble-user {background: #c0ffff; color: #284e5a;
    border-radius:14px; padding: 9px 16px; margin:11px 0 7px 28%; max-width:70%;
    border-bottom-right-radius:3px; border-top-left-radius: 3px;}
.chat-bubble-bot {background: #fdf7de; color: #cba323;
    border-radius:14px; padding: 9px 16px; margin:7px 28% 9px 0; max-width:70%;
    border-bottom-left-radius:3px; border-top-right-radius: 3px;}
.hr-sep {border: 0; height:1.2px; background:#e3e8e2; margin:1.0em 0;}
.stTextInput > div > div > input {background:#fff !important;}
</style>
"""
CLASSIC_CSS = """
<style>
body {background: #21242b;}
.theme-bar {background: #23293b; padding:13px 18px; font-size:1.38em; color: #fff;
    border-radius:18px 18px 0 0;}
.technote {color: #89adff;}
.chat-bubble-user {background: #333d66; color: #aabeff; border-radius:13px;
    padding:9px 14px; margin:7px 0 7px 28%; max-width:70%; border-bottom-right-radius:4px;}
.chat-bubble-bot {background: #242b37; color: #ffeebb; border-radius:13px;
    padding:9px 14px; margin:7px 28% 9px 0; max-width:70%; border-bottom-left-radius:4px;}
.hr-sep {border:0;height:1.3px; background:#282b39; margin:1.0em 0;}
.stTextInput > div > div > input {background:#23263a!important;color:#c6dfff!important;}
</style>
"""

# == Session state resets ==
if "theme" not in st.session_state:
    st.session_state.theme = "Cyberpunk"
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # (who, msg)
if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

# == Theme selector ==
theme = st.radio("Theme", ["Cyberpunk", "Light", "Classic"], horizontal=True,
                 index=["Cyberpunk", "Light", "Classic"].index(st.session_state.theme),
                 key="theme_select")
if theme == "Cyberpunk":
    st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)
elif theme == "Light":
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)
else:
    st.markdown(CLASSIC_CSS, unsafe_allow_html=True)
st.session_state.theme = theme

# == Fancy header ==
st.markdown(
    f"<div class='theme-bar'>"
    f"<span>🤖 Gemini {'Cyber' if theme=='Cyberpunk' else ('Classic' if theme=='Classic' else 'Lite')} Chatbot</span><br>"
    f"<span class='technote'>AI chat & Build By Nihak</span></div>",
    unsafe_allow_html=True,
)
st.markdown("<hr class='hr-sep' />", unsafe_allow_html=True)

# == "Typing..." indicator (fancy blinking dots) ==
TYPING_HTML = """
<div id="typing-indicator" style="font-family: monospace; color: #12fff7; font-size: 1.05em;">
  Gemini is typing<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
</div>
<style>
@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.2; }
  100% { opacity: 1; }
}
.dot:nth-child(1) {animation: blink 1s infinite;}
.dot:nth-child(2) {animation: blink 1s 0.3s infinite;}
.dot:nth-child(3) {animation: blink 1s 0.6s infinite;}
</style>
"""

# == Sound notification (short chime, inline base64 wav) ==
def play_notification_sound():
    chime_b64 = (
    "UklGRqABAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YYABAAD///8AAAAw4ZT/lsP/AKz/k5kA/wDv//44//8AAPA57gyw"
    "w8Dy/P7/NOLw9XPy4vSl09j7H5bnPXoAAAAAAB9AAflexgAiAAJ6gAELDwAA6z++QAAgAAAAAAAAA==")
    audio_html = f"""
    <audio autoplay>
      <source src="data:audio/wav;base64,{chime_b64}" type="audio/wav">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# == Message rendering: Avatars and bubbles! ==
def styled_message(msg, sender):
    avatar = (
        f"<img src='{USER_AVATAR}' height='36' style='vertical-align:middle;border-radius:50%;margin-right:10px;border:1.5px solid #12fff7;'>"
        if sender == "user"
        else f"<img src='{BOT_AVATAR}' height='36' style='vertical-align:middle; border-radius:50%; margin-right:10px; border:1.5px solid #ffe57f;'>"
    )
    bubble_class = "chat-bubble-user" if sender == "user" else "chat-bubble-bot"
    alignment = "right" if sender == "user" else "left"
    st.markdown(
        f"<div style='display:flex; align-items:center; justify-content:flex-{alignment};margin-bottom:4px;'>"
        f"{avatar}<div class='{bubble_class}'>{msg}</div></div>",
        unsafe_allow_html=True,
    )

# == Reset UI ==
if st.button("♻️ Reset chat & quota"):
    st.session_state.chat_history = []
    st.session_state.request_count = 0

# == Render chat history ==
for who, msg in st.session_state.chat_history:
    styled_message(msg, who)

# == User input ==
user_input = st.text_input("Type a message and press Enter...", key="user_input", max_chars=600)
if user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    styled_message(user_input, "user")
    # Show typing indicator (disappear after reply)
    typing_placeholder = st.empty()
    typing_placeholder.markdown(TYPING_HTML, unsafe_allow_html=True)
    # Get Gemini response
    now = time.time()
    if (now - st.session_state.last_request_time) < WAIT_SECONDS:
        wait = round(WAIT_SECONDS - (now - st.session_state.last_request_time), 1)
        st.warning(f"⚡ Rate limited for free safety. Wait {wait} seconds.")
        st.stop()
    if st.session_state.request_count >= DAY_LIMIT-1:
        st.error("🛑 Daily Gemini free quota reached. Come back tomorrow.")
        st.stop()
    chat = genai.Chat(model=MODEL)
    try:
        response = chat.send_message(user_input)
        reply = response.text
    except Exception as e:
        reply = f"API error: {e}"
    typing_placeholder.empty()  # Remove typing dots
    play_notification_sound()
    st.session_state.last_request_time = now
    st.session_state.request_count += 1
    st.session_state.chat_history.append(("bot", reply.strip()))
    styled_message(reply.strip(), "bot")

st.markdown("<hr class='hr-sep' />", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#232d8c;font-size:0.93em;text-align:center;'>"
    "All conversation &bull; <b>API key is secret</b> &bull; "
    "If Gemini errors, check free quota or API key.<br>"
    "Developed in Python/Streamlit – change theme and style anytime."
    "</p>", unsafe_allow_html=True
)
