import streamlit as st
from morse_utils import text_to_morse, morse_to_text

st.set_page_config(page_title="Morse Code Translator", layout="centered")

st.title("📡 Morse Code Translator")

option = st.radio("Choose translation mode:", ("Text to Morse", "Morse to Text"))

if option == "Text to Morse":
    text_input = st.text_input("Enter text:")
    if text_input:
        morse_output = text_to_morse(text_input)
        st.code(morse_output, language="text")

elif option == "Morse to Text":
    morse_input = st.text_input("Enter Morse code (use spaces between letters and / for spaces):")
    if morse_input:
        text_output = morse_to_text(morse_input)
        st.code(text_output, language="text")

st.markdown("---")
st.markdown("🔤 A-Z, 0-9 supported\n📍 Use `/` for space in Morse")
