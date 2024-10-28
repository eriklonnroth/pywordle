# PyWordle

A Python implementation of the popular word-guessing game Wordle using Pygame. Players get six attempts to guess a five-letter word, with color-coded feedback for each guess.

Sidenote: This is my first ever Python project, built in 60 minutes with the help of Claude.ai!

## Installation

1. Ensure you have Python 3.x installed
2. Clone the repo and install required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure `words.csv` is in the same directory as `pywordle.py`
4. Launch the game (takes a few seconds to load):
```bash
python pywordle.py
```

## Build app bundle

Instead of launching the game from the command line, you can create an app bundle (i.e. click to open).

First, get pyinstaller:
```bash
pip install pyinstaller
```

*Option 1: Install the app without an icon*
This will generate an app bundle with the standard black executable icon
```bash
pyinstaller --onefile --add-data "words.csv:." --windowed pywordle.py
```

*Option 2: Install the app with an icon*
`cd` into the project folder and run the following commands to generate an app icon:
```bash
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset -o PyWordle.icns
```

Once you have generated the `PyWordle.icns` icon set, you can install the app bundle: 
```bash
pyinstaller --onefile --add-data "words.csv:." --windowed --icon=PyWordle.icns --name "PyWordle" pywordle.py
```


## How to Play

- Type a five-letter word and press Enter to submit
- Each guess must be a valid English word (as determined by words.csv)
- After submitting a guess, the letter tiles will flip to reveal:
  - 🟩 Green: Letter is correct and in the right spot
  - 🟨 Yellow: Letter is in the word but in the wrong spot
  - ⬛ Gray: Letter is not in the word

## Technical Details

### Word Selection
Kudos to https://github.com/steve-kasica/wordle-words/blob/master/wordle.csv for providing the original Wordle wordlist.
The game uses a curated list of words from `words.csv` with two columns:
- `word`: The five-letter word
- `occurrence`: A float value representing the word's frequency among printed works in English. 

For a word to qualify as a potential target word, it must meet a minimum occurrence threshold. At 1E-7, words like 'allot' and 'allow' make the cut, but obscure words like 'almug' and 'alods' do not. You can adjust the OCCURRENCE_THRESHOLD constant at the top of the file:
```python
    OCCURRENCE_THRESHOLD = 1E-7 # Use 1E-6 to only include common English words
```
The occurrence threshold only affects the selection of target words, and has no impact on words that will be accepted as guesses. 

### Core Functions

#### Word Validation (`load_valid_words`)
```python
def load_valid_words(self) -> set:
    """
    Loads and filters words from words.csv based on occurrence threshold.
    Returns a set of valid uppercase words.
    """
```

#### Guess Checking (`check_guess`)
```python
def check_guess(self, guess: str) -> List[Tuple[str, str]]:
    """
    Takes a guess string and returns a list of (letter, state) tuples.
    States can be "correct", "present", or "absent".
    """
```

#### Animation System
The game uses two main classes for animations:
- `TileAnimation`: Handles individual tile flip animations
- `WordAnimation`: Manages sequential flipping of an entire word's tiles

### Additional Features

1. Invalid Word Handling:
   - Guesses must match words in the word list
   - Invalid guesses trigger a row jiggle animation

2. Game Over States:
   - Win: "Great!" message appears
   - Loss: Reveals the target word
   - Play Again button appears in both cases

3. Visual Feedback:
   - Sequential tile flipping animations
   - Row jiggle for invalid words
   - Rounded corners on buttons
   - Clean, minimal interface

## File Structure

```
pywordle/
│
├── pywordle.py      # Main game file
├── words.csv        # Word list with occurrence rates
└── README.md        # This file
```

## Dependencies

- Python 3.x
- Pygame
- CSV module (standard library)

## Contributing

Feel free to fork the repository and submit pull requests. Some areas for potential improvement:
- Keyboard display
- Difficulty levels
- Statistics tracking
- WordleBot to analyze strength of guesses
- Play against Bot

## License

This project is open source and available under the MIT License.
