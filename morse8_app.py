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
from morse_utils import bandpass_filter, extract_morse_units

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
    .css-1bzp7po {{
        justify-content: center !important;
    }}
    .nav-container {{
        display: flex;
        justify-content: center;
        gap: 40px;
        padding: 10px 0;
        background-color: rgba(0, 0, 0, 0.5);
        border-bottom: 2px solid #ffffff33;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
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
tabs = st.tabs(["⚙️ DECODER", "💡 DETAILS", "📞 CONTACT US"])

# ----------- Tab: DECODER -----------
with tabs[0]:
    st.title("Morse Code Translator")

    st.markdown("""
    <div class='info-box'>
        <h3>🔤 Translate between English and Morse Code</h3>
        <p>Choose your direction, enter your message, and click <b>Translate</b> to see the result.</p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Select translation mode:", ["TEXT to MORSE", "MORSE to TEXT", "IMAGE to MORSE/TEXT", "AUDIO to TEXT"])

    if mode == "TEXT to MORSE":
        st.subheader("🔤 Text to Morse Translation")
        text_input = st.text_input("Enter English text:")
        if text_input:
            # Replace space with slash to explicitly mark word boundaries
            formatted_input = text_input.strip().replace(" ", " / ")
            morse_output = text_to_morse(formatted_input)
            st.code(morse_output, language='text')

    elif mode == "MORSE to TEXT":
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
                    
    elif mode == "IMAGE to MORSE/TEXT":
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
                
    elif mode == "AUDIO to TEXT":
        st.subheader("📡 Morse Audio to Text")

        st.warning(
            "⚠️ This decoder only works with WAV files that meet the following specs:\n"
            "- Speed: 20 WPM\n"
            "- Farnsworth speed: 15 WPM\n"
            "- Tone pitch: ~550 Hz\n"
            "- Volume: 40% to 100% for best clarity"
        )

        audio_file = st.file_uploader("Upload a Morse code WAV audio file", type=["wav"])

        if audio_file is not None:
            st.audio(audio_file, format="audio/wav")
            fs, data = wavfile.read(audio_file)

            if data.ndim > 1:
                data = data.mean(axis=1)  # Convert stereo to mono

            # Add pre-roll silence (200ms)
            preroll_duration = 0.2  # seconds
            preroll_samples = int(fs * preroll_duration)
            preroll = np.zeros(preroll_samples)
            data = np.concatenate([preroll, data])

            st.info(
                "🔍 Extracting and filtering tone at ~550Hz...\n"
                "📏 Detecting Morse timing (Farnsworth speed = 15 WPM)..."
            )
            filtered = bandpass_filter(data, fs)
            morse_code = extract_morse_units(filtered, fs, wpm=15)

            st.success("🔊 Morse Detected:")
            st.code(morse_code)

            try:
                text = morse_to_text(morse_code)
                st.write("📄 Decoded Text:")
                st.code(text)
            except Exception as e:
                st.error(f"❌ Error decoding Morse: {e}")
                
# ----------- Tab: FACTS -----------
with tabs[1]:
    st.title("📚 Facts about Morse Code")

    col1, col2 = st.columns([2, 1])  # Text left, image right

    with col1:
        st.markdown("""
        <div class='info-box'>
            <ul>
                <li>Morse code was developed in the 1830s by Samuel Morse and Alfred Vail.</li>
                <li>Originally designed for use with the telegraph, it became the first widely adopted digital communication method.</li>
                <li>Each letter and number is represented by a unique sequence of short and long signals: dots (.) and dashes (-).</li>
                <li>It's still used in aviation, maritime, and amateur radio communications where voice isn't practical.</li>
                <li>The distress signal <strong>SOS</strong> ("... --- ...") was chosen for its unmistakable pattern and ease of transmission.</li>
                <li>Modern Morse code supports both English and non-English characters (via extensions like International Morse).</li>
                <li>Even today, Morse remains a favorite among enthusiasts for its simplicity and elegance.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.image("img1.jpg", caption="International Morse Code Chart", use_column_width=True)

st.markdown("---")
st.title("❓ Decoder Input Guidelines & FAQs")

st.markdown("""
<div class='info-box'>
""", unsafe_allow_html=True)

with st.expander("🔤 TEXT to MORSE - What should I enter?"):
    st.markdown("""
    &nbsp;&nbsp;- Input can include **A-Z**, **0-9**, and basic punctuation (`. , ? /`).
    
    &nbsp;&nbsp;- Unsupported characters will be ignored.
    
    &nbsp;&nbsp;- Output is encoded using International Morse Code.
    
    &nbsp;&nbsp;- Uses `'/'` for **word separator** and spaces between **letters**.
    """, unsafe_allow_html=True)
    
with st.expander("📡 AUDIO to TEXT - How should I format the audio file?"):
    st.markdown("""
    &nbsp;&nbsp;- Format: **WAV (.wav)** only.
    
    &nbsp;&nbsp;- Tone: Approximately **550 Hz** sine wave.
    
    &nbsp;&nbsp;- Speed: **20 WPM** (Farnsworth speed = **15 WPM**).
    
    &nbsp;&nbsp;- Volume: Recommended **40–100%**.
    
    &nbsp;&nbsp;- Audio must be clear and not distorted or noisy.
    
    &nbsp;&nbsp;- Real-time decoding is not yet supported.
    """, unsafe_allow_html=True)

with st.expander("🖼️ IMAGE to TEXT - What kind of image can I use?"):
    st.markdown("""
    &nbsp;&nbsp;- Use a clearly printed or typed **Morse code image** (dots and dashes).
    
    &nbsp;&nbsp;- High contrast and sharpness improve accuracy.
    
    &nbsp;&nbsp;- Avoid handwriting, noise, or overlapping symbols.
    
    &nbsp;&nbsp;- Works best with clean digital or scanned inputs.
    """, unsafe_allow_html=True)

with st.expander("🌐 MORSE to TEXT - What Morse format can I paste?"):
    st.markdown("""
    &nbsp;&nbsp;- Use **dots (.)** and **dashes (-)** to represent Morse letters.
    
    &nbsp;&nbsp;- Separate **letters with spaces** and **words with ' / '**.
    
    &nbsp;&nbsp;- Example: `.... . .-.. .-.. --- / .-- --- .-. .-.. -..` → `HELLO WORLD`
    
    &nbsp;&nbsp;- Avoid unknown symbols — they may break decoding.
    """, unsafe_allow_html=True)

st.subheader("🛠️ General Troubleshooting")

with st.expander("Why is my Morse not decoding correctly?"):
    st.markdown("""
    &nbsp;&nbsp;- Check for incorrect speed, missing spaces, or unsupported characters.
    
    &nbsp;&nbsp;- Ensure audio input has a clear 550 Hz tone at 20 WPM.
    
    &nbsp;&nbsp;- For image input, use crisp and high-contrast visuals.
    """, unsafe_allow_html=True)

with st.expander("Can I use audio from YouTube or MP3s?"):
    st.markdown("""
    &nbsp;&nbsp;- Convert to **WAV format** using Audacity or online tools.
    
    &nbsp;&nbsp;- Ensure the Morse tone is around **550 Hz** and clearly audible.
    
    &nbsp;&nbsp;- Avoid compression artifacts from MP3 that degrade clarity.
    """, unsafe_allow_html=True)

with st.expander("What’s the difference between WPM and Farnsworth speed?"):
    st.markdown("""
    &nbsp;&nbsp;- **WPM** controls character rate (dot/line length).
    
    &nbsp;&nbsp;- **Farnsworth speed** adds **extra spacing** between characters and words.
    
    &nbsp;&nbsp;- Helps beginners decode more easily by slowing gaps but keeping character timing.
    """, unsafe_allow_html=True)

with st.expander("Can I decode Morse live or from a microphone?"):
    st.markdown("""
    &nbsp;&nbsp;- No — this prototype supports **only uploaded files** for now.
    
    &nbsp;&nbsp;- Real-time microphone decoding would require **audio streaming** and latency control.
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ----------- Tab: CONTACT -----------
with tabs[2]:
    st.title("📬 Contact Us")
    st.markdown("""
    <div class='info-box'>
        <p><strong>Developed by:</strong> Group 1 - Adrian Bangalando, Keith Del Carmen, Denisse Escape, and Louie Rizo</p>
        <p><strong>GitHub</strong>: <a href='https://github.com/shinkairu' target='_blank'>github.com/shinkairu</a></p>
        <p><strong>Email</strong>: group1_BDER@gmail.com</p>
        <blockquote>This project is specifically for our DSP Course! All thanks to Dr. Jonathan Taylar for guiding us! Thank you!</blockquote>
    </div>
    """, unsafe_allow_html=True)
