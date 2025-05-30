import requests
import numpy as np
import streamlit as st
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, hilbert

morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
}

morse_table = """
### Morse Code Reference Table

| Character | Morse Code | Character | Morse Code | Character | Morse Code |
|-----------|------------|-----------|------------|-----------|------------|
| A         | .-         | N         | -.         | 0         | -----      |
| B         | -...       | O         | ---        | 1         | .----      |
| C         | -.-.       | P         | .--.       | 2         | ..---      |
| D         | -..        | Q         | --.-       | 3         | ...--      |
| E         | .          | R         | .-.        | 4         | ....-      |
| F         | ..-.       | S         | ...        | 5         | .....      |
| G         | --.        | T         | -          | 6         | -....      |
| H         | ....       | U         | ..-        | 7         | --...      |
| I         | ..         | V         | ...-       | 8         | ---..      |
| J         | .---       | W         | .--        | 9         | ----.      |
| K         | -.-        | X         | -..-       |           |            |
| L         | .-..       | Y         | -.--       |           |            |
| M         | --         | Z         | --..       |           |            |
"""

inverse_dict = {v: k for k, v in morse_dict.items()}

def ocr_image_from_url(image_file):
    payload = {
        'apikey': 'helloworld',  # Replace with your own API key for better quota
        'language': 'eng',
    }
    files = {
        'filename': (image_file.name, image_file.getvalue(), image_file.type)
    }
    response = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
    result = response.json()
    if 'ParsedResults' in result and result['ParsedResults']:
        return result['ParsedResults'][0]['ParsedText']
    else:
        # Optionally log errors:
        # st.error("OCR API error: " + result.get('ErrorMessage', 'Unknown error'))
        return ''

def text_to_morse(text):
    words = text.strip().split()
    morse_words = []

    for word in words:
        morse_letters = [morse_dict.get(char.upper(), '') for char in word if char.upper() in morse_dict]
        morse_words.append(' '.join(morse_letters))

    return ' / '.join(morse_words)

def morse_to_text(code):
    words = code.strip().split(' / ')
    decoded_words = []
    for word in words:
        letters = word.strip().split()
        decoded_words.append(''.join(inverse_dict.get(l, '') for l in letters))
    return ' '.join(decoded_words)

def bandpass_filter(data, fs, lowcut=500, highcut=600, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def extract_morse_units(signal, fs, threshold=0.1, wpm=15):
    envelope = np.abs(hilbert(signal))
    on = envelope > (np.max(envelope) * threshold)

    dot_duration = 60 / (50 * wpm)  # dot duration in seconds
    unit_samples = int(dot_duration * fs)

    changes = np.diff(on.astype(int))
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]

    # Fix edge misalignment
    if ends.size > 0 and starts.size > 0:
        if ends[0] < starts[0]:
            ends = ends[1:]
        if starts.size > ends.size:
            starts = starts[:len(ends)]

    morse = []
    for i in range(len(starts)):
        duration = (ends[i] - starts[i]) / fs
        if duration < dot_duration * 1.5:
            morse.append('.')
        else:
            morse.append('-')

        if i < len(starts) - 1:
            gap = (starts[i + 1] - ends[i]) / fs
            if gap > dot_duration * 6:
                morse.append(' / ')  # Word gap
            elif gap > dot_duration * 2:
                morse.append(' ')    # Letter gap

    return ''.join(morse)
