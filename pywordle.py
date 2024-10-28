import pygame
import csv
import random
import time
import math
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Obscure words exclusion 
OCCURRENCE_THRESHOLD = 1E-7 # Use 1E-6 to only use common English words

# Constants
WINDOW_SIZE = 720
GRID_SIZE = 5
NUM_ATTEMPTS = 6
SQUARE_SIZE = 62
SQUARE_SPACING = 5
GRID_OFFSET_X = (WINDOW_SIZE - (GRID_SIZE * (SQUARE_SIZE + SQUARE_SPACING))) // 2
GRID_OFFSET_Y = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
ABSENT = (58, 58, 60)    # Dark gray
PRESENT = (181, 159, 59)  # Yellow
CORRECT = (88, 163, 81)   # Green

# Font setup
FONT_SIZE = 48
LETTER_FONT = pygame.font.Font(None, FONT_SIZE)
TOAST_FONT = pygame.font.Font(None, 48)
BUTTON_FONT = pygame.font.Font(None, 28)

# Button styling
BUTTON_RADIUS = 15
BUTTON_PADDING = 20
TOAST_SPACING = 60

class TileAnimation:
    def __init__(self, letter: str, x: int, y: int, size: int, start_color: tuple, end_color: tuple):
        self.letter = letter
        self.x = x
        self.y = y
        self.size = size
        self.start_color = start_color
        self.end_color = end_color
        self.progress = 0.0
        self.duration = 500  # milliseconds
        self.started = False
        self.completed = False
        
    def start(self):
        self.started = True
        self.start_time = pygame.time.get_ticks()
            
    def update(self, current_time: int):
        if not self.started or self.completed:
            return
            
        elapsed = current_time - self.start_time
        self.progress = min(elapsed / self.duration, 1.0)
        
        if self.progress >= 1.0:
            self.completed = True
            
    def draw(self, screen, font):
        if self.progress < 0.5:
            scale = math.cos(self.progress * math.pi)
            color = self.start_color
        else:
            scale = abs(math.cos(self.progress * math.pi))
            color = self.end_color
            
        scaled_height = int(self.size * scale)
        y_offset = (self.size - scaled_height) // 2
        
        rect = pygame.Rect(
            self.x,
            self.y + y_offset,
            self.size,
            scaled_height
        )
        pygame.draw.rect(screen, color, rect)
        
        if scale > 0.2:
            text = font.render(self.letter, True, WHITE)
            text_scale = pygame.transform.scale(
                text,
                (
                    int(text.get_width() * scale),
                    int(text.get_height() * scale)
                )
            )
            text_rect = text_scale.get_rect(center=(
                self.x + self.size // 2,
                self.y + self.size // 2
            ))
            screen.blit(text_scale, text_rect)

class WordAnimation:
    def __init__(self, word: str, x: int, y: int, tile_size: int, colors: list[tuple]):
        self.tiles = []
        self.current_tile_index = 0
        
        for i, (letter, color) in enumerate(zip(word, colors)):
            tile = TileAnimation(
                letter=letter,
                x=x + i * (tile_size + SQUARE_SPACING),
                y=y,
                size=tile_size,
                start_color=GRAY,
                end_color=color
            )
            self.tiles.append(tile)
        
        if self.tiles:
            self.tiles[0].start()
    
    def update(self, current_time: int):
        if self.current_tile_index < len(self.tiles):
            current_tile = self.tiles[self.current_tile_index]
            current_tile.update(current_time)
            
            if current_tile.completed:
                self.current_tile_index += 1
                if self.current_tile_index < len(self.tiles):
                    self.tiles[self.current_tile_index].start()
    
    def draw(self, screen, font):
        for tile in self.tiles:
            tile.draw(screen, font)
    
    @property
    def completed(self):
        return self.current_tile_index >= len(self.tiles)

class WordleGame:
    def __init__(self, screen):
        self.screen = screen
        self.current_attempt = 0
        self.current_guess = ""
        self.game_over = False
        self.show_toast = False
        self.toast_message = ""
        self.letters_state = [[None for _ in range(GRID_SIZE)] for _ in range(NUM_ATTEMPTS)]
        self.valid_words = self.load_valid_words()
        self.target_word = self.get_random_word()
        self.jiggle_start = None
        self.current_animation = None
        print(f"Target word: {self.target_word}")
        
    def load_valid_words(self) -> set:
        valid_words = set()
        try:
            with open('words.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        if float(row['occurrence']) >= OCCURRENCE_THRESHOLD:
                            valid_words.add(row['word'].upper())
                    except (ValueError, KeyError):
                        continue
        except FileNotFoundError:
            print("Error: words.csv not found")
            pygame.quit()
            exit(1)
        
        if not valid_words:
            print("Error: No valid words loaded")
            pygame.quit()
            exit(1)
            
        return valid_words
    
    def get_random_word(self) -> str:
        return random.choice(list(self.valid_words))
    
    def is_valid_word(self, word: str) -> bool:
        return word.upper() in self.valid_words
    
    def check_guess(self, guess: str) -> List[Tuple[str, str]]:
        result = [(letter, None) for letter in guess]
        target_chars = list(self.target_word)
        guess_chars = list(guess)
        used_positions = set()
        
        for i in range(len(guess_chars)):
            if guess_chars[i] == target_chars[i]:
                result[i] = (guess_chars[i], "correct")
                target_chars[i] = None
                used_positions.add(i)
        
        for i in range(len(guess_chars)):
            if i in used_positions:
                continue
            
            letter = guess_chars[i]
            if letter in target_chars:
                result[i] = (letter, "present")
                target_chars[target_chars.index(letter)] = None
            else:
                result[i] = (letter, "absent")
        
        return result
    
    def handle_keydown(self, event):
        if self.game_over or (self.current_animation and not self.current_animation.completed):
            return
            
        if event.key == pygame.K_RETURN and len(self.current_guess) == GRID_SIZE:
            if self.is_valid_word(self.current_guess):
                self.submit_guess()
            else:
                self.jiggle_start = time.time()
        elif event.key == pygame.K_BACKSPACE:
            self.current_guess = self.current_guess[:-1]
        elif len(self.current_guess) < GRID_SIZE and event.unicode.isalpha():
            self.current_guess += event.unicode.upper()
    
    def submit_guess(self):
        result = self.check_guess(self.current_guess)
        self.letters_state[self.current_attempt] = result
        
        # Create animation for the current guess
        colors = []
        for _, state in result:
            if state == "correct":
                colors.append(CORRECT)
            elif state == "present":
                colors.append(PRESENT)
            else:
                colors.append(ABSENT)
                
        self.current_animation = WordAnimation(
            word=self.current_guess,
            x=GRID_OFFSET_X,
            y=GRID_OFFSET_Y + self.current_attempt * (SQUARE_SIZE + SQUARE_SPACING),
            tile_size=SQUARE_SIZE,
            colors=colors
        )
        
        if self.current_guess == self.target_word:
            self.show_toast = True
            self.toast_message = "Great!"
            self.game_over = True
        elif self.current_attempt == NUM_ATTEMPTS - 1:
            self.show_toast = True
            self.toast_message = self.target_word
            self.game_over = True
            
        self.current_attempt += 1
        self.current_guess = ""
    
    def calculate_jiggle_offset(self) -> int:
        if self.jiggle_start is None:
            return 0
            
        elapsed_time = time.time() - self.jiggle_start
        if elapsed_time > 0.5:
            self.jiggle_start = None
            return 0
            
        progress = elapsed_time / 0.5
        decay = 1 - progress
        offset = 10 * decay * math.sin(20 * math.pi * progress)
        return int(offset)
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        x, y, width, height = rect
        
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    def draw(self):
        self.screen.fill(WHITE)
        current_time = pygame.time.get_ticks()
        
        # Draw completed rows
        for row in range(self.current_attempt):
            if row == self.current_attempt - 1 and self.current_animation and not self.current_animation.completed:
                continue  # Skip drawing the current row if it's being animated
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * (SQUARE_SIZE + SQUARE_SPACING)
                y = GRID_OFFSET_Y + row * (SQUARE_SIZE + SQUARE_SPACING)
                
                if self.letters_state[row] and self.letters_state[row][col]:
                    letter, state = self.letters_state[row][col]
                    if state == "correct":
                        color = CORRECT
                    elif state == "present":
                        color = PRESENT
                    else:
                        color = ABSENT
                    
                    pygame.draw.rect(self.screen, color, 
                                   (x, y, SQUARE_SIZE, SQUARE_SIZE))
                    text = LETTER_FONT.render(letter, True, WHITE)
                    text_rect = text.get_rect(center=(x + SQUARE_SIZE/2, y + SQUARE_SIZE/2))
                    self.screen.blit(text, text_rect)
        
        # Draw animation if active
        if self.current_animation:
            self.current_animation.update(current_time)
            self.current_animation.draw(self.screen, LETTER_FONT)
        
        # Draw current guess and empty rows
        for row in range(self.current_attempt, NUM_ATTEMPTS):
            jiggle_offset = self.calculate_jiggle_offset() if row == self.current_attempt else 0
            
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * (SQUARE_SIZE + SQUARE_SPACING) + jiggle_offset
                y = GRID_OFFSET_Y + row * (SQUARE_SIZE + SQUARE_SPACING)
                
                pygame.draw.rect(self.screen, GRAY, 
                               (x, y, SQUARE_SIZE, SQUARE_SIZE))
                
                if row == self.current_attempt and col < len(self.current_guess):
                    text = LETTER_FONT.render(self.current_guess[col], True, WHITE)
                    text_rect = text.get_rect(center=(x + SQUARE_SIZE/2, y + SQUARE_SIZE/2))
                    self.screen.blit(text, text_rect)
        
        # Draw toast and button
        if self.show_toast:
            grid_height = NUM_ATTEMPTS * (SQUARE_SIZE + SQUARE_SPACING)
            toast_y = GRID_OFFSET_Y + grid_height + TOAST_SPACING
            
            toast = TOAST_FONT.render(self.toast_message, True, BLACK)
            toast_rect = toast.get_rect(center=(WINDOW_SIZE/2, toast_y))
            self.screen.blit(toast, toast_rect)
            
            button_text = BUTTON_FONT.render("Play Again", True, BLACK)
            button_width = button_text.get_rect().width + BUTTON_PADDING * 2
            button_height = button_text.get_rect().height + BUTTON_PADDING
            button_x = (WINDOW_SIZE - button_width) // 2
            button_y = toast_y + TOAST_SPACING // 2
            
            button_rect = (button_x, button_y, button_width, button_height)
            self.draw_rounded_rect(self.screen, LIGHT_GRAY, button_rect, BUTTON_RADIUS)
            
            text_rect = button_text.get_rect(center=(WINDOW_SIZE/2, button_y + button_height/2))
            self.screen.blit(button_text, text_rect)

def main():
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("PyWordle")
    clock = pygame.time.Clock()
    
    game = WordleGame(screen)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and game.game_over:
                x, y = pygame.mouse.get_pos()
                button_width = 100 + BUTTON_PADDING * 2
                button_height = 30 + BUTTON_PADDING
                button_x = (WINDOW_SIZE - button_width) // 2
                button_y = GRID_OFFSET_Y + (NUM_ATTEMPTS * (SQUARE_SIZE + SQUARE_SPACING)) + TOAST_SPACING * 1.5
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                if button_rect.collidepoint(x, y):
                    game = WordleGame(screen)
        
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()