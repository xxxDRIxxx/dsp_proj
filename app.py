import streamlit as st
from morse_utils import text_to_morse, morse_to_text
from PIL import Image
import requests
import numpy as np
from scipy.io import wavfile
import io

# Page config
st.set_page_config(page_title="Morse Code Translator", layout="centered")

# --- CSS for header links ---
st.markdown(
    """
    <style>
    .header {
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 10px 20px;
        display: flex;
        gap: 30px;
        align-items: center;
        font-weight: bold;
        font-size: 18px;
    }
    .nav-button {
        background: none;
        border: none;
        color: #60a5fa;
        cursor: pointer;
        font-size: 18px;
        font-weight: bold;
        padding: 0;
        margin: 0;
        transition: color 0.3s ease;
    }
    .nav-button:hover {
        color: #3b82f6;
    }
    .nav-button:focus {
        outline: none;
        color: #2563eb;
    }
    .page-content {
        padding: 20px 0 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize page state ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Header navigation ---
cols = st.columns([1,1,1])
with cols[0]:
    if st.button("Home", key="nav_home", help="Go to Home"):
        st.session_state.page = "home"
with cols[1]:
    if st.button("Facts", key="nav_facts", help="Go to Facts"):
        st.session_state.page = "facts"
with cols[2]:
    if st.button("Contact", key="nav_contact", help="Go to Contact"):
        st.session_state.page = "contact"

st.markdown("<hr>", unsafe_allow_html=True)

# --- Page rendering ---

if st.session_state.page == "home":
    # Header
    st.markdown("<h1 style='text-align:center; color:#60a5fa;'>📡 Morse Code Translator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#9ca3af;'>Convert Morse code from <b>Text</b>, <b>Image</b>, or <b>Audio</b> to English.</p>", unsafe_allow_html=True)
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
            extracted_text = ocr_image_from_url(uploaded_image)
            st.write("🔍 Extracted Text:")
            st.code(extracted_text.strip())
            morse_output = text_to_morse(extracted_text)
            st.write("📡 Morse Code:")
            st.code(morse_output)

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

elif st.session_state.page == "facts":
    st.header("📚 Facts about Morse Code")
    facts = [
        "Morse code was developed in the 1830s and 1840s by Samuel Morse and Alfred Vail.",
        "It encodes text characters as sequences of dots (.) and dashes (-).",
        "Morse code was widely used in early radio communications and telegraphy.",
        "SOS (... --- ...) is the most famous Morse code distress signal.",
        "Morse code can be transmitted in sound, light, or visual signals.",
        "Amateur radio enthusiasts still use Morse code today.",
        "Morse code was officially used by the military and maritime services well into the 21st century.",
    ]
    for fact in facts:
        st.write("• " + fact)

elif st.session_state.page == "contact":
    st.header("📞 Contact Information")
    st.write("Feel free to reach out!")
    st.write("- Email: yourname@example.com")
    st.write("- Phone: +1 (555) 123-4567")
    st.write("- Twitter: [@yourhandle](https://twitter.com/yourhandle)")
    st.write("- GitHub: [yourusername](https://github.com/yourusername)")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray;'>© 2025 MorseDecoder. Developed by <a style='color:#60a5fa;' href='#'>YourName</a></div>",
    unsafe_allow_html=True,
)
