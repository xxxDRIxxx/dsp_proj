import streamlit as st
from morse_utils import text_to_morse, morse_to_text
from PIL import Image
import requests
import numpy as np
from scipy.io import wavfile
import io

st.set_page_config(page_title="Morse Code Translator", layout="centered")

# Function to render clickable header navigation
def render_header_nav(selected_page):
    pages = ["Translator", "Facts", "Contact"]
    nav_html = "<div style='background-color:#1f2937; padding: 10px 20px; display:flex; justify-content:center; gap:30px;'>"
    for page in pages:
        color = "#60a5fa" if page == selected_page else "white"
        nav_html += f"""
            <a href='?page={page.lower()}' 
            style='color:{color}; text-decoration:none; font-weight:bold; font-size:18px;'>
            {page}
            </a>
        """
    nav_html += "</div><hr style='border-color:#111827;'/>"
    st.markdown(nav_html, unsafe_allow_html=True)

# Detect current page from URL query params using st.query_params
query_params = st.query_params
page = query_params.get("page", ["translator"])[0].lower()

# Render header nav bar
render_header_nav(page.capitalize())

# Page logic
if page == "translator":
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

    tabs = st.tabs(["📝 Text Input", "🖼️ Image Input", "🎧 Audio Input"])

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

            morse_chars = set(".-/ ")
            if set(extracted_text.strip()).issubset(morse_chars):
                text_output = morse_to_text(extracted_text.strip())
                st.write("🔤 Translated Text:")
                st.code(text_output)
            else:
                morse_output = text_to_morse(extracted_text.strip())
                st.write("📡 Morse Code:")
                st.code(morse_output)

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

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:gray;'>"
        "© 2025 MorseDecoder. Developed by "
        "<a style='color:#60a5fa;' href='#'>YourName</a>"
        "</div>",
        unsafe_allow_html=True
    )

elif page == "facts":
    st.title("📜 Facts about Morse Code")
    st.markdown("""
    - Morse code was invented by Samuel Morse and Alfred Vail in the 1830s.
    - It was originally designed for use with telegraph systems.
    - Morse code uses a series of dots (`.`) and dashes (`-`) to represent letters and numbers.
    - The length of a dot is the basic unit of time measurement in Morse code transmission.
    - The SOS distress signal in Morse code is `... --- ...`.
    - Morse code is still used in aviation and amateur radio.
    - It was a vital communication method during World War I and II.
    """)
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:gray;'>"
        "© 2025 MorseDecoder. Developed by "
        "<a style='color:#60a5fa;' href='#'>YourName</a>"
        "</div>",
        unsafe_allow_html=True
    )

elif page == "contact":
    st.title("📞 Contact Information")
    st.markdown("""
    If you have questions or want to get in touch, please contact us at:

    - Email: morse.decoder@example.com
    - Phone: +1 (555) 123-4567
    - Twitter: [@MorseDecoder](https://twitter.com/MorseDecoder)
    - GitHub: [github.com/yourname/MorseDecoder](https://github.com/yourname/MorseDecoder)
    """)
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:gray;'>"
        "© 2025 MorseDecoder. Developed by "
        "<a style='color:#60a5fa;' href='#'>YourName</a>"
        "</div>",
        unsafe_allow_html=True
    )
