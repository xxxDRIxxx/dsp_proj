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
