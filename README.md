# PyWordle

A Python implementation of the popular word-guessing game Wordle using Pygame. Players get six attempts to guess a five-letter word, with color-coded feedback for each guess.

Sidenote: This is my firsrt ever Python project, built in 60 minutes with the help of Claude.ai!

## Installation

1. Ensure you have Python 3.x installed
2. Install required dependencies:
```bash
pip install pygame
```

3. Place `words.csv` in the same directory as `pywordle.py`
4. Run the game:
```bash
python pywordle.py
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
The game uses a curated list of words from `words.csv` with two columns:
- `word`: The five-letter word
- `occurrence`: A float value representing the word's frequency in English. Adapted from https://github.com/steve-kasica/wordle-words/blob/master/wordle.csv

For a word to qualify as a potential target word, it must meet a minimum occurrence threshold. At 1E-7, words like 'allot' and 'allow' make the cut, but obscure words like 'almug' and 'alods' do not. You can adjust the OCCURRENCE_THRESHOLD constant at the top of the file:
```python
    OCCURRENCE_THRESHOLD = 1E-7 # Use 1E-6 to only use common English words
```

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
