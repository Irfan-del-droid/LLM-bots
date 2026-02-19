import streamlit as st
from time import sleep
import ollama
import re

# Streamlit page config
st.set_page_config(page_title="Mini Bot", page_icon="🤖", layout="wide")

st.title("🤖 Mini Bot")
st.caption("Thinks deep, replies in 4 words.")

# --- Custom CSS: Robotic Font + Blue ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&display=swap');

.stApp {
    font-family: 'Orbitron', sans-serif;
    color: #3b82f6;
}

h1, h2, h3, p, label {
    font-family: 'Orbitron', sans-serif !important;
    color: #3b82f6 !important;
}

.stChatMessage {
    font-family: 'Orbitron', sans-serif;
    color: #60a5fa;
}

/* Keep avatars as emojis */
[data-testid="stChatMessageAvatarCustom"] {
    font-family: 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif !important;
    font-size: 1.5rem;
}

[data-testid="stChatInput"] textarea {
    font-family: 'Orbitron', sans-serif;
    color: #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# Sidebar options
st.sidebar.title("🤖 Mini Bot Settings")
jargon_mode = st.sidebar.checkbox("Enable Jargon Mode", value=False)
st.sidebar.info("Bot replies 4 words at a time, shows thinking.")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# System prompt based on jargon mode
def get_system_prompt():
    base = (
        "You must show your internal thinking process. "
        "Your response must follow this EXACT format:\n"
        "<thought>\nYour detailed reasoning here...\n</thought>\n"
        "Final response here.\n\n"
        "CRITICAL CONSTRAINTS:\n"
        "1. ALWAYS include <thought>...</thought> before your answer.\n"
        "2. Your final answer (outside thought tags) must be EXACTLY four words.\n"
    )
    if jargon_mode:
        base += "3. Use ONLY complex technical or corporate jargon for those 4 words (e.g., 'Synergize scalable cloud paradigms').\n"
    else:
        base += "3. Use simple, clear language for the 4 words.\n"
    return base

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            content = msg["content"]
            thought_match = re.search(r"<thought>(.*?)</thought>", content, re.DOTALL)
            if thought_match:
                thought_text = thought_match.group(1).strip()
                main_reply = re.sub(r"<thought>.*?</thought>", "", content, flags=re.DOTALL).strip()
                with st.expander("💭 Thinking Process"):
                    st.markdown(thought_text)
                st.markdown(f"**{main_reply}**")
            else:
                st.markdown(content)

# Chat input
if user_input := st.chat_input("You:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Build messages for Ollama (inject system prompt + history)
    ollama_messages = [{"role": "system", "content": get_system_prompt()}]
    for msg in st.session_state.messages:
        ollama_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant", avatar="🤖"):
        thinking_placeholder = st.empty()
        reply_placeholder = st.empty()
        full_response = ""

        try:
            # Show "thinking..." animation
            thinking_placeholder.markdown("🧠 *Thinking...*")
            sleep(0.5)

            response = ollama.chat(
                model="gemma3:latest",
                messages=ollama_messages,
            )
            full_response = response['message']['content']

            # Parse thinking vs final response
            thought_match = re.search(r"<thought>(.*?)</thought>", full_response, re.DOTALL)
            thinking_placeholder.empty()

            if thought_match:
                thought_text = thought_match.group(1).strip()
                main_reply = re.sub(r"<thought>.*?</thought>", "", full_response, flags=re.DOTALL).strip()

                with st.expander("💭 Thinking Process", expanded=True):
                    st.markdown(thought_text)

                # Stream the 4-word reply word by word
                words = main_reply.split()
                streamed = ""
                for word in words:
                    streamed += word + " "
                    reply_placeholder.markdown(f"**{streamed.strip()}**")
                    sleep(0.3)
            else:
                reply_placeholder.markdown(full_response)

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Error calling Ollama: {e}")
            full_response = "Backend connectivity failure detected."
            reply_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
