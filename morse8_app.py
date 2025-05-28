# morse app ver. 2 by kit
import streamlit as st
import base64
import os
from morse_utils import text_to_morse, morse_to_text, morse_table 

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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

bg_path = os.path.join(os.path.dirname(__file__), "bg.jpg")
if os.path.exists(bg_path):
    set_background(bg_path)

# ----------- Custom CSS -----------
custom_css = """
<style>
.nav-container {
    display: flex;
    justify-content: center;
    gap: 40px;
    padding: 10px 0;
    background: linear-gradient(135deg, #1f2937, #111827);
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

h1, h2, h3 {
    color: #4A0072;
    text-shadow: 1px 1px #ffffff;
    font-size: 2.5em;
}

html, body, p, div {
    color: #2e003e !important;
    font-size: 18px !important;
    font-family: 'Segoe UI', sans-serif;
}

.stButton>button {
    background-color: #7b1fa2;
    color: white;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 20px;
    font-weight: bold;
    transition: background-color 0.3s ease;
}

.stButton>button:hover {
    background-color: #4a0072;
}

.info-box {
    background: rgba(255, 255, 255, 0.65);
    border-left: 6px solid #7b1fa2;
    padding: 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ----------- Session state page manager -----------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ----------- Navigation -----------
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Decoder", key="nav_home"):
        st.session_state.page = "home"
with col2:
    if st.button("Facts", key="nav_facts"):
        st.session_state.page = "facts"
with col3:
    if st.button("Contact", key="nav_contact"):
        st.session_state.page = "contact"
st.markdown('</div>', unsafe_allow_html=True)

# ----------- App Pages -----------

def home():
    st.title("Morse Code Translator")
    option = st.radio("Choose translation direction:", ("English to Morse", "Morse to English"))

    user_input = st.text_area("Enter your message:")
    if st.button("Translate"):
        if option == "English to Morse":
            translation = text_to_morse(user_input)
        else:
            translation = morse_to_text(user_input)
        st.success(translation)

def facts():
    st.title("Fun Morse Code Facts")
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

    st.markdown(morse_table, unsafe_allow_html=True)

def contact():
    st.title("Contact")
    st.markdown("""
    <div class='info-box'>
    If you have questions, feedback, or suggestions, feel free to reach out at:<br><br>
    📧 Email: example@email.com<br>
    🌐 Website: [example.com](https://example.com)
    </div>
    """, unsafe_allow_html=True)

# ----------- Render Selected Page -----------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "facts":
    facts()
elif st.session_state.page == "contact":
    contact()
