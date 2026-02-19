import streamlit as st
import ollama
import base64
import os
from gtts import gTTS
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Boruto: Next Generation Bot",
    page_icon="🍥",
    layout="wide"
)

# --- Load Background Image as Base64 ---
bg_css = "background: radial-gradient(circle at top, #111827, #020617);"
bg_path = os.path.join(os.path.dirname(__file__), "uzumaki-boruto-b4-3840x2400.jpg")
if os.path.exists(bg_path):
    with open(bg_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    bg_css = f"""
        background: linear-gradient(
            rgba(2, 6, 23, 0.45),
            rgba(2, 6, 23, 0.55)
        ),
        url("data:image/jpeg;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    """

# --- Voice Assistant Function ---
def speak_text(text):
    """Converts text to speech and plays it in the Streamlit app."""
    try:
        tts = gTTS(text=text, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.error(f"Voice error: {e}")

# --- Custom CSS with Background Image and Blue Glow ---
st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

.stApp {{
    {bg_css}
    font-family: 'Poppins', sans-serif;
    color: #f9fafb;
}}

.main-header {{
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #3b82f6, #06b6d4, #3b82f6);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradient 3s linear infinite;
    margin-bottom: 5px;
}}

@keyframes gradient {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

hr {{
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    margin: 10px 0 25px 0;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(2, 6, 23, 0.95), rgba(0, 0, 0, 0.98));
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(59, 130, 246, 0.2);
}}

.boruto-bio {{
    background: rgba(59, 130, 246, 0.05);
    backdrop-filter: blur(16px);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(59, 130, 246, 0.2);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}}

.stChatMessage {{
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 15px;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: transform 0.2s ease;
}}

.stChatMessage:hover {{
    transform: translateY(-2px);
    border-color: rgba(59, 130, 246, 0.3);
}}

.stButton>button {{
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 12px 24px;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    transition: all 0.3s ease;
}}

.stButton>button:hover {{
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}}

/* BLUE GLOW ON CHAT INPUT */
[data-testid="stChatInput"] {{
    border-radius: 25px !important;
}}

[data-testid="stChatInput"] textarea {{
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: rgba(0,0,0,0.5) !important;
    color: white !important;
    padding: 12px 15px !important;
    transition: all 0.3s ease-in-out !important;
}}

[data-testid="stChatInput"] textarea:focus {{
    border: 1px solid #3b82f6 !important;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.6) !important;
    background: rgba(15, 23, 42, 0.8) !important;
}}

</style>
""", unsafe_allow_html=True)

# --- Sidebar: Character Bio & Settings ---
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🍥 Boruto Uzumaki</h2>", unsafe_allow_html=True)

    st.markdown("""
    <div class='boruto-bio'>
    <p style='margin: 0;'><b>Affiliation:</b> Konohagakure</p>
    <p style='margin: 5px 0;'><b>Team:</b> Team 7</p>
    <p style='margin: 5px 0;'><b>Specialty:</b> Karma, Vanishing Rasengan</p>
    <hr style='margin: 10px 0; background: rgba(59, 130, 246, 0.3);'>
    <i style='color: #94a3b8; font-size: 0.9rem;'>"I'm gonna be a shinobi who supports the Hokage from the shadows!"</i>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("⚙️ Jutsu Settings")
    temp = st.slider("Chakra Intensity (Temperature)", 0.0, 1.0, 0.7, 0.1)
    top_p = st.slider("Precision (Top P)", 0.0, 1.0, 0.9, 0.1)
    
    voice_enabled = st.checkbox("🔊 Voice Assistant", value=True)

    st.divider()

    if st.button("🔥 Reset Chakra (Clear Chat)", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "You are Boruto Uzumaki. Mimic his personality perfectly: confident, rebellious, but loyal. "
                    "Use catchphrases like '...ttebasa!'. Mention thunder burgers or your dad when relevant. "
                    "Keep it energetic and youthful."
                )
            }
        ]
        st.rerun()

# --- Main Interface ---
st.markdown("""
<div style='text-align: center;'>
    <h1 class='main-header'>🍥 Boruto: Next Generation AI</h1>
    <p style="color:#d1d5db; margin-top:-10px; font-size: 1.1rem; letter-spacing: 1px;">
    MASTER YOUR NINJA WAY WITH THE SON OF THE SEVENTH HOKAGE
    </p>
</div>
<hr>
""", unsafe_allow_html=True)

# Initialize chat memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are Boruto Uzumaki. Mimic his personality perfectly: confident, rebellious, but loyal. "
                "Use catchphrases like '...ttebasa!'. Mention thunder burgers or your dad when relevant. "
                "Keep it energetic and youthful."
            )
        }
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🍥" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# User input
if prompt := st.chat_input("What's the plan, ttebasa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🍥"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = ollama.chat(
                model="gemma3:latest",
                messages=st.session_state.messages,
                options={
                    "temperature": temp,
                    "top_p": top_p
                },
                stream=True,
            )
            for chunk in stream:
                full_response += chunk['message']['content']
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # --- Trigger Voice ---
            if voice_enabled:
                speak_text(full_response)

        except Exception as e:
            st.error(f"Error calling Ollama: {e}")
            full_response = "Ugh, my chakra's acting up... (Ollama error)"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
