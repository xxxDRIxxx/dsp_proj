import streamlit as st
from morse_utils import text_to_morse, morse_to_text
from PIL import Image
import requests
import numpy as np
from scipy.io import wavfile
import io

st.set_page_config(page_title="Morse Code Translator", layout="centered")

# Custom CSS for header links to look like clickable text links
st.markdown(
    """
    <style>
    /* Header container */
    .header-nav {
        display: flex;
        justify-content: center;
        gap: 40px;
        background-color: #111827;
        padding: 15px 0;
        font-size: 18px;
        font-weight: bold;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Each link */
    .nav-link {
        color: #60a5fa;
        cursor: pointer;
        text-decoration: none;
        padding: 4px 8px;
        border-radius: 4px;
        user-select: none;
    }
    .nav-link:hover {
        color: #3b82f6;
        background-color: #1e40af;
    }
    .nav-link.selected {
        color: white;
        background-color: #2563eb;
    }
    /* Remove Streamlit default button styles */
    div.stButton > button {
        all: unset;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for page if not set
if "page" not in st.session_state:
    st.session_state.page = "translator"

# Custom function to render header navigation
def header_nav(current_page):
    pages = ["translator", "facts", "contact"]
    labels = ["Translator", "Facts", "Contact"]
    cols = st.columns(len(pages))
    for i, page in enumerate(pages):
        is_selected = page == current_page
        css_class = "nav-link selected" if is_selected else "nav-link"
        # Use st.button but style it as a text link using CSS classes
        with cols[i]:
            # We add a key so buttons are unique
            clicked = st.button(labels[i], key=f"nav_{page}", help=f"Go to {labels[i]}")
            # Using JavaScript event to add the class for selected is tricky, so we do it manually
            if clicked:
                st.session_state.page = page
            # Inject the span with CSS class for link styles (hacky but works)
            # This is just for the selected style, because Streamlit buttons can't directly have classes
            if is_selected:
                st.markdown(
                    f"<style>div.stButton > button[key='nav_{page}'] {{color: white !important; background-color: #2563eb !important;}}</style>",
                    unsafe_allow_html=True,
                )

# Render header navigation
header_nav(st.session_state.page)

st.markdown("---")

# PAGE CONTENTS
if st.session_state.page == "translator":
    st.title("📡 Morse Code Translator")
    st.markdown(
        "<p style='text-align:center;'>Convert Morse code from <b>Text</b>, <b>Image</b>, or <b>Audio</b> to English.</p>",
        unsafe_allow_html=True,
    )
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
                st.code(morse_output, language="text")

        elif mode == "Morse to Text":
            morse_input = st.text_input("Enter Morse code (space for letters, `/` for words):")
            if morse_input:
                text_output = morse_to_text(morse_input)
                st.code(text_output, language="text")

    # --- Tab 2: Image Input ---
    with tabs[1]:
        def ocr_image_from_url(image_bytes):
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={"filename": image_bytes},
                data={"apikey": "helloworld", "language": "eng"},
            )
            result = response.json()
            return result["ParsedResults"][0]["ParsedText"] if "ParsedResults" in result else ""

        uploaded_image = st.file_uploader("Upload an image with Morse or English text", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
            extracted_text = ocr_image_from_url(uploaded_image)
            st.write("🔍 Extracted Text:")
            st.code(extracted_text.strip())

            # Detect if extracted text looks like Morse code (only dots, dashes, spaces, slashes)
            morse_chars = set(".- /")
            extracted_set = set(extracted_text.strip())
            if extracted_set.issubset(morse_chars):
                # Convert Morse to text
                try:
                    text_output = morse_to_text(extracted_text.strip())
                    st.write("🔤 Translated Text:")
                    st.code(text_output)
                except Exception as e:
                    st.error(f"Error decoding Morse code: {e}")
            else:
                # Convert text to Morse
                try:
                    morse_output = text_to_morse(extracted_text.strip())
                    st.write("📡 Morse Code:")
                    st.code(morse_output)
                except Exception as e:
                    st.error(f"Error encoding text: {e}")

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
    st.title("📚 Facts about Morse Code")
    st.markdown(
        """
        - Morse code was invented in the 1830s by Samuel Morse and Alfred Vail.
        - It uses dots (.) and dashes (-) to encode letters and numbers.
        - Morse code was widely used in telegraph systems for long-distance communication.
        - The SOS distress signal in Morse is "... --- ...".
        - Morse code can be transmitted via sound, light, or visual signals.
        - It played a crucial role in maritime and aviation communication.
        """
    )

elif st.session_state.page == "contact":
    st.title("📞 Contact Information")
    st.markdown(
        """
        For inquiries or support, contact us at:

        - Email: morse@example.com  
        - Phone: +1 (555) 123-4567  
        - Website: [https://morsedecoder.example.com](https://morsedecoder.example.com)
        """
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray;'>© 2025 MorseDecoder. Developed by <a style='color:#60a5fa;' href='#'>YourName</a></div>",
    unsafe_allow_html=True,
)
