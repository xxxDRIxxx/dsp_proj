import streamlit as st

import io
import os
import sys
import base64

import time
import easyocr
from PIL import Image
import requests

import numpy as np
from scipy.io import wavfile
from morse_utils import text_to_morse, morse_to_text, morse_table, ocr_image_from_url

# ----------- Page config -----------
st.set_page_config(page_title="Morse Code Translator 📡", layout="wide")

# ----------- Background image -----------
@st.cache_data
def get_base64_of_bin_file(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_path):
    bin_str = get_base64_of_bin_file(image_path)
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    .block-container {{
        padding-top: 2rem;
    }}
    /* Center the entire tab layout */
    [data-testid="stTabs"] > div {{
        display: flex;
        justify-content: center;
    }}

    /* Style the actual tabs */
    button[data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.65);
        border: 2px solid #7b1fa2;
        color: #4A0072;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 12px;
        margin: 5px;
        transition: all 0.3s ease;
    }}
    button[data-baseweb="tab"]:hover {{
        background-color: #e1bee7;
        border-color: #4a0072;
        color: #2e003e;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: #7b1fa2;
        color: white;
        border-color: #4a0072;
    }}

    h1, h2, h3 {{
        color: #ffffff;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        font-size: 2.5em;
    }}
    body, html, p, div {{
        color: #ffffff !important;
        font-size: 18px;
        font-family: 'Segoe UI', sans-serif;
    }}
    .stButton > button {{
        background-color: #00b4d8;
        color: #ffffff;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: #0077b6;
    }}
    textarea, input {{
        background-color: rgba(255,255,255,0.9) !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }}
    .info-box {{
        background: rgba(255, 255, 255, 0.85);
        border-left: 6px solid #00b4d8;
        padding: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        color: #000000 !important;
    }}
    .info-box h1, .info-box h2, .info-box h3, .info-box p, .info-box li {{
        color: #000000 !important;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

bg_path = os.path.join(os.path.dirname(__file__), "bg.jpg")
if os.path.exists(bg_path):
    set_background(bg_path)

reader = easyocr.Reader(['en'])  

# ----------- Tabs Setup -----------
tabs = st.tabs(["🤖 DECODER", "💬 FACTS", "🔧 CONTACT"])

# ----------- Tab: DECODER -----------
with tabs[0]:
    st.title("📋🔤🤖 Morse Code Translator")

    st.markdown("""
    <div class='info-box'>
        <h3>🔤 Translate between English and Morse Code</h3>
        <p>Choose your direction, enter your message, and click <b>Translate</b> to see the result.</p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Select translation mode:", ["Text to Morse", "Morse to Text", "Image to Morse/Text", "Morse Audio to Text"])

    if mode == "🧾 Text to Morse":
        st.subheader("Text to Morse Translation")
        text_input = st.text_input("Enter English text:")
        if text_input:
            # Replace space with slash to explicitly mark word boundaries
            formatted_input = text_input.strip().replace(" ", " / ")
            morse_output = text_to_morse(formatted_input)
            st.code(morse_output, language='text')

    elif mode == "🔤 Morse to Text":
        st.subheader("🌐 Morse Input to Text Decoder")

        col1, col2 = st.columns([1.2, 1.8])

        with col1:
            st.markdown("### Morse Code Table")
            with st.container(border=True):
                st.markdown(f"""
                <div class='morse-table'>{morse_table}</div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("### Input Morse Code")
            morse_input = st.text_area("Use `/` for word gaps, space for letters.", height=120)
            if morse_input:
                text_output = morse_to_text(morse_input)
                st.success("✅ Decoded Text")
                st.code(text_output, language='text')
                    
    elif mode == "Image to Morse/Text":
        st.subheader("📷 Image to Morse/Text")

        uploaded_image = st.file_uploader(
            "⚠️ Upload an image containing Morse or English text",
            type=["png", "jpg", "jpeg"]
        )

        if uploaded_image:
            image = Image.open(uploaded_image).convert("RGB")
            st.image(image, caption="Uploaded Image", use_container_width=True)

            try:
                np_image = np.array(image)

                with st.spinner("🔍 Extracting text from image..."):
                    start_time = time.time()
                    result = reader.readtext(np_image, detail=0)
                    extracted_text = " ".join(result).strip()
                    elapsed = time.time() - start_time

                if not extracted_text:
                    st.error("⚠️ No text detected in the image.")
                else:
                    st.success(f"✅ Text extracted in {elapsed:.2f}s")
                    st.write("🔍 **Extracted Text:**")
                    st.code(extracted_text)

                    is_morse = all(c in ".-/ \n" for c in extracted_text if c.strip())

                    try:
                        if is_morse:
                            decoded = morse_to_text(extracted_text)
                            st.write("🔤 **Decoded English Text:**")
                            st.code(decoded)
                        else:
                            morse_output = text_to_morse(extracted_text)
                            st.write("📡 **Encoded Morse Code:**")
                            st.code(morse_output)
                    except Exception as e:
                        st.error(f"❌ Error during translation: {e}")

            except Exception as e:
                st.error(f"❌ OCR or image processing failed: {e}")
                
    elif mode == "Morse Audio to Text":
        st.subheader("Morse Audio to Text")
        audio_file = st.file_uploader("Upload a Morse code WAV audio file", type=["wav"])
    
        if audio_file is not None:
            st.audio(audio_file, format="audio/wav")

            sample_rate, data = wavfile.read(audio_file)

            if data.ndim > 1:  # Stereo to mono
                data = data.mean(axis=1)

            duration = len(data) / sample_rate
            t = np.linspace(0., duration, len(data))

            volume_threshold = 200
            tone_mask = np.abs(data) > volume_threshold
            tone_times = t[tone_mask]

            if len(tone_times) == 0:
                st.warning("No Morse tones detected. Check the volume threshold or input.")
            else:
                intervals = np.diff(tone_times)
                unit = np.median(intervals)  # Estimate dot duration

                symbols = []
                gap_time = 0.3 * unit  # Slight tolerance for gaps

                last_time = tone_times[0]
                current_symbol = '-'

                for current_time in tone_times[1:]:
                    gap = current_time - last_time
                    if gap < gap_time:
                        current_symbol += '-'
                    else:
                        symbols.append(current_symbol)
                        current_symbol = '-'
                    last_time = current_time
                symbols.append(current_symbol)

                morse_sequence = ' '.join(symbols)
                st.write("🔊 Detected Morse:")
                st.code(morse_sequence)

                translated = morse_to_text(morse_sequence)
                st.write("📄 Decoded Text:")
                st.code(translated)
        else:
            st.info("💡 Please upload a `.wav` file to decode Morse audio.")


# ----------- Tab: FACTS -----------
with tabs[1]:
    st.title("📚 Fun Morse Code Facts")
    st.markdown("""
    <div class='info-box'>
        <ul>
            <li>Morse code was developed in the 1830s by Samuel Morse and Alfred Vail.</li>
            <li>It was first used for telegraph communication.</li>
            <li>Morse code is still used in aviation and amateur radio today.</li>
            <li>The distress signal SOS is "... --- ...", chosen for its simplicity.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------- Tab: CONTACT -----------
with tabs[2]:
    st.title("📬📞 Contact Us")
    st.markdown("""
    <div class='info-box'>
        <p><strong>Developed by:</strong> Group 1 - Adrian Bangalando, Keith Del Carmen, Denisse Escape, and Louie Rizo</p>
        <p><strong>GitHub</strong>: <a href='https://github.com/shinkairu' target='_blank'>github.com/shinkairu</a></p>
        <p><strong>Email</strong>: group1_BDER@gmail.com</p>
        <blockquote>This project is specifically for our DSP Course! All thanks to Dr. Jonathan Taylar for guiding us! Thank you!</blockquote>
    </div>
    """, unsafe_allow_html=True)
