import streamlit as st
import base64
import os
from morse_utils import text_to_morse, morse_to_text, morse_table  # Custom utility module

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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

bg_path = os.path.join(os.path.dirname(__file__), "bg.jpg")
if os.path.exists(bg_path):
    set_background(bg_path)

# ----------- Tabs Setup -----------
tabs = st.tabs(["DECODER", "FACTS", "CONTACT"])

# ----------- Tab: DECODER -----------
with tabs[0]:
    st.title("Morse Code Translator")

    st.markdown("""
    <div class='info-box'>
        <h3>🔤 Translate between English and Morse Code</h3>
        <p>Choose your direction, enter your message, and click <b>Translate</b> to see the result.</p>
    </div>
    """, unsafe_allow_html=True)

    option = st.radio("Choose translation direction:", ("English to Morse", "Morse to English"))
    user_input = st.text_area("Enter your message:")

    if st.button("Translate"):
        if option == "English to Morse":
            translation = text_to_morse(user_input)
        else:
            translation = morse_to_text(user_input)
            st.markdown(morse_table, unsafe_allow_html=True)
        st.success(translation)

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
    st.title("📬 Contact Us")
    st.markdown("""
    <div class='info-box'>
        <p><strong>Developed by:</strong> Group 1 - Adrian Bangalando, Keith Del Carmen, Denisse Escape, and Louie Rizo</p>
        <p><strong>GitHub</strong>: <a href='https://github.com/shinkairu' target='_blank'>github.com/shinkairu</a></p>
        <p><strong>Email</strong>: group1_BDER@gmail.com</p>
        <blockquote>This project is specifically for our DSP Course! All thanks to Dr. Jonathan Taylar for guiding us! Thank you!</blockquote>
    </div>
    """, unsafe_allow_html=True)
