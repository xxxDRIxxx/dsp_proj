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

def text_to_morse(text):
    return ' '.join(morse_dict.get(char.upper(), '') for char in text if char.upper() in morse_dict)

def morse_to_text(code):
    words = code.strip().split(' / ')
    decoded_words = []
    for word in words:
        letters = word.strip().split()
        decoded_words.append(''.join(inverse_dict.get(l, '') for l in letters))
    return ' '.join(decoded_words)
