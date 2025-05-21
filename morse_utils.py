morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
}

inverse_dict = {v: k for k, v in morse_dict.items()}

def text_to_morse(text):
    return ' '.join(morse_dict.get(char.upper(), '') for char in text if char.upper() in morse_dict)

def morse_to_text(code):
    words = code.strip().split(' / ')
    decoded_words = []
    for word in words:
        letters = word.strip().split()
        decoded_words.append(''.join(inverse_dict.get(l, '') for l in letters))
    return ' '.join(decoded_words)
