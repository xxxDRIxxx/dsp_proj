import streamlit as st
from morse_utils import text_to_morse, morse_to_text
from PIL import Image
import requests
import numpy as np
from scipy.io import wavfile
import io

st.set_page_config(page_title="Morse Code Translator", layout="centered")

# Header
st.markdown(
    """
    <style>
    .main { background: linear-gradient(135deg, #1f2937, #111827); color: white; }
    h1, h2, .stTextInput, .stTextArea, .stFileUploader, .stRadio label {
        color: #60a5fa;
    }
    .stCodeBlock { background-color: #1f2937 !important; color: #10b981 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center;'>📡 Morse Code Translator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Convert Morse code from <b>Text</b>, <b>Image</b>, or <b>Audio</b> to English.</p>", unsafe_allow_html=True)
st.markdown("---")

# Tabs for input methods
tabs = st.tabs(["📝 Text Input", "🖼️ Image Input", "🎧 Audio Input"])

# --- Tab 1: Text Input ---
with tabs[0]:
    mode = st.radio("Select translation mode:", ["Text to Morse", "Morse to Text"])

    if mode == "Text to Morse":
        text_input = st.text_input("Enter English text:")
        if text_input:
            morse_output = text_to_morse(text_input)
            st.code(morse_output, language='text')

    elif mode == "Morse to Text":
        morse_input = st.text_input("Enter Morse code (space for letters, `/` for words):")
        if morse_input:
            text_output = morse_to_text(morse_input)
            st.code(text_output, language='text')

# --- Tab 2: Image Input ---
with tabs[1]:
    def ocr_image_from_url(image_bytes):
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'filename': image_bytes},
            data={'apikey': 'helloworld', 'language': 'eng'}
        )
        result = response.json()
        return result['ParsedResults'][0]['ParsedText'] if 'ParsedResults' in result else ''

    uploaded_image = st.file_uploader("Upload an image with Morse or English text", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

        raw_text = ocr_image_from_url(uploaded_image)
        st.write("🔍 Raw Extracted Text:")
        st.code(raw_text.strip())

        # Clean text to only Morse symbols and spaces
        cleaned_text = ''.join(c for c in raw_text if c in ['.', '-', ' ', '/'])
        cleaned_text = cleaned_text.strip()

        if len(cleaned_text) > 0:
            st.write("🔎 Cleaned Morse candidate:")
            st.code(cleaned_text)

            # If cleaned_text contains only Morse symbols, decode it
            if all(c in ['.', '-', ' ', '/'] for c in cleaned_text):
                decoded_text = morse_to_text(cleaned_text)
                st.write("🔤 Decoded English Text:")
                st.code(decoded_text)
            else:
                # If not valid Morse, treat as English text and encode
                morse_code = text_to_morse(raw_text)
                st.write("📡 Encoded Morse Code:")
                st.code(morse_code)
        else:
            st.write("❗ No valid Morse code detected in image.")


# --- Tab 3: Audio Input ---
with tabs[2]:
    uploaded_audio = st.file_uploader("Upload a Morse code audio (.wav)", type=["wav"])
    if uploaded_audio:
        rate, data = wavfile.read(io.BytesIO(uploaded_audio.read()))
        if data.ndim > 1:
            data = data[:, 0]
        signal = np.abs(data)
        threshold = 0.3 * np.max(signal)

        bits = (signal > threshold).astype(int)
        dot_length = rate // 10
        samples_per_symbol = []
        current = bits[0]
        count = 0
        for bit in bits:
            if bit == current:
                count += 1
            else:
                samples_per_symbol.append((current, count))
                current = bit
                count = 1
        samples_per_symbol.append((current, count))

        morse = ""
        for val, dur in samples_per_symbol:
            if val == 1:
                if dur < dot_length * 2:
                    morse += "."
                else:
                    morse += "-"
            else:
                if dur > dot_length * 5:
                    morse += " / "
                elif dur > dot_length * 2:
                    morse += " "

        st.write("📡 Morse Code:")
        st.code(morse)
        st.write("🔤 Translated Text:")
        st.code(morse_to_text(morse))

# Footer
st.markdown("---")
st.write("© 2025 MorseDecoder. Developed by B.D.E.R.")
