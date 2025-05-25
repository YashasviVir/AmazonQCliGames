import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
GRID_SIZE = 4
CELL_SIZE = 100
GRID_PADDING = 10
GRID_OFFSET_X = (SCREEN_WIDTH - (CELL_SIZE * GRID_SIZE + GRID_PADDING * (GRID_SIZE - 1))) // 2
GRID_OFFSET_Y = 150
FPS = 60

# Colors
BACKGROUND_COLOR = (250, 248, 239)
GRID_COLOR = (187, 173, 160)
EMPTY_CELL_COLOR = (205, 193, 180)
TEXT_COLOR = (119, 110, 101)
LIGHT_TEXT = (249, 246, 242)

# Tile colors - from original 2048 game
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (52, 235, 195),
}

# Text colors based on tile value
TEXT_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
    4096: (249, 246, 242),
    8192: (249, 246, 242),
}

class Tile:
    def __init__(self, value=0):
        self.value = value
        self.merged = False
        self.new = value != 0
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.moving = False
        self.move_speed = 20
        
    def update(self):
        if self.moving:
            # Move towards target position
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            
            if abs(dx) < self.move_speed:
                self.x = self.target_x
            else:
                self.x += self.move_speed if dx > 0 else -self.move_speed
                
            if abs(dy) < self.move_speed:
                self.y = self.target_y
            else:
                self.y += self.move_speed if dy > 0 else -self.move_speed
                
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False
                return False
            return True
        return False
        
    def draw(self, screen, x, y):
        # Draw tile background
        if self.value == 0:
            pygame.draw.rect(screen, EMPTY_CELL_COLOR, 
                            (x, y, CELL_SIZE, CELL_SIZE), 
                            border_radius=6)
            return
            
        # Draw tile with value
        pygame.draw.rect(screen, TILE_COLORS.get(self.value, (60, 58, 50)), 
                        (x, y, CELL_SIZE, CELL_SIZE), 
                        border_radius=6)
        
        # Draw value text
        if self.value > 0:
            # Choose font size based on the number of digits
            if self.value < 100:
                font_size = 48
            elif self.value < 1000:
                font_size = 40
            else:
                font_size = 32
                
            font = pygame.font.SysFont(None, font_size, bold=True)
            text_color = TEXT_COLORS.get(self.value, LIGHT_TEXT)
            text = font.render(str(self.value), True, text_color)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            screen.blit(text, text_rect)

class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.grid = [[Tile() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.won = False
        self.font = pygame.font.SysFont(None, 36, bold=True)
        self.small_font = pygame.font.SysFont(None, 24)
        self.toast_message = ""
        self.toast_timer = 0
        self.toast_duration = 1.5  # seconds
        self.moving_tiles = False
        
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()
        
    def add_random_tile(self):
        # Find all empty cells
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].value == 0:
                    empty_cells.append((row, col))
        
        if empty_cells:
            # Choose a random empty cell
            row, col = random.choice(empty_cells)
            # 90% chance for a 2, 10% chance for a 4
            self.grid[row][col] = Tile(2 if random.random() < 0.9 else 4)
            self.grid[row][col].new = True
            
            # Set position for animation
            self.grid[row][col].x = GRID_OFFSET_X + col * (CELL_SIZE + GRID_PADDING)
            self.grid[row][col].y = GRID_OFFSET_Y + row * (CELL_SIZE + GRID_PADDING)
            self.grid[row][col].target_x = self.grid[row][col].x
            self.grid[row][col].target_y = self.grid[row][col].y
            
            return True
        return False
    
    def reset_merged_flags(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row][col].merged = False
                self.grid[row][col].new = False
    
    def is_game_over(self):
        # Check if there are any empty cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].value == 0:
                    return False
        
        # Check if there are any possible merges
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = self.grid[row][col].value
                
                # Check right
                if col < GRID_SIZE - 1 and self.grid[row][col + 1].value == value:
                    return False
                
                # Check down
                if row < GRID_SIZE - 1 and self.grid[row + 1][col].value == value:
                    return False
        
        return True
    
    def check_win(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].value == 2048:
                    return True
        return False
    
    def move_left(self):
        moved = False
        self.reset_merged_flags()
        
        for row in range(GRID_SIZE):
            for col in range(1, GRID_SIZE):
                if self.grid[row][col].value != 0:
                    # Move tile as far left as possible
                    current_col = col
                    while current_col > 0:
                        # If the cell to the left is empty, move there
                        if self.grid[row][current_col - 1].value == 0:
                            self.grid[row][current_col - 1] = self.grid[row][current_col]
                            self.grid[row][current_col] = Tile()
                            current_col -= 1
                            moved = True
                            
                            # Set animation target
                            self.grid[row][current_col].target_x = GRID_OFFSET_X + current_col * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col].target_y = GRID_OFFSET_Y + row * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col].moving = True
                            self.moving_tiles = True
                        
                        # If the cell to the left has the same value and hasn't been merged yet, merge them
                        elif (self.grid[row][current_col - 1].value == self.grid[row][current_col].value and 
                              not self.grid[row][current_col - 1].merged and 
                              not self.grid[row][current_col].merged):
                            
                            self.grid[row][current_col - 1].value *= 2
                            self.grid[row][current_col - 1].merged = True
                            self.score += self.grid[row][current_col - 1].value
                            self.best_score = max(self.best_score, self.score)
                            self.grid[row][current_col] = Tile()
                            moved = True
                            
                            # Set animation target
                            self.grid[row][current_col - 1].target_x = GRID_OFFSET_X + (current_col - 1) * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col - 1].target_y = GRID_OFFSET_Y + row * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col - 1].moving = True
                            self.moving_tiles = True
                            
                            break
                        else:
                            break
        
        return moved
    
    def move_right(self):
        moved = False
        self.reset_merged_flags()
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2, -1, -1):
                if self.grid[row][col].value != 0:
                    # Move tile as far right as possible
                    current_col = col
                    while current_col < GRID_SIZE - 1:
                        # If the cell to the right is empty, move there
                        if self.grid[row][current_col + 1].value == 0:
                            self.grid[row][current_col + 1] = self.grid[row][current_col]
                            self.grid[row][current_col] = Tile()
                            current_col += 1
                            moved = True
                            
                            # Set animation target
                            self.grid[row][current_col].target_x = GRID_OFFSET_X + current_col * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col].target_y = GRID_OFFSET_Y + row * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col].moving = True
                            self.moving_tiles = True
                        
                        # If the cell to the right has the same value and hasn't been merged yet, merge them
                        elif (self.grid[row][current_col + 1].value == self.grid[row][current_col].value and 
                              not self.grid[row][current_col + 1].merged and 
                              not self.grid[row][current_col].merged):
                            
                            self.grid[row][current_col + 1].value *= 2
                            self.grid[row][current_col + 1].merged = True
                            self.score += self.grid[row][current_col + 1].value
                            self.best_score = max(self.best_score, self.score)
                            self.grid[row][current_col] = Tile()
                            moved = True
                            
                            # Set animation target
                            self.grid[row][current_col + 1].target_x = GRID_OFFSET_X + (current_col + 1) * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col + 1].target_y = GRID_OFFSET_Y + row * (CELL_SIZE + GRID_PADDING)
                            self.grid[row][current_col + 1].moving = True
                            self.moving_tiles = True
                            
                            break
                        else:
                            break
        
        return moved
    
    def move_up(self):
        moved = False
        self.reset_merged_flags()
        
        for col in range(GRID_SIZE):
            for row in range(1, GRID_SIZE):
                if self.grid[row][col].value != 0:
                    # Move tile as far up as possible
                    current_row = row
                    while current_row > 0:
                        # If the cell above is empty, move there
                        if self.grid[current_row - 1][col].value == 0:
                            self.grid[current_row - 1][col] = self.grid[current_row][col]
                            self.grid[current_row][col] = Tile()
                            current_row -= 1
                            moved = True
                            
                            # Set animation target
                            self.grid[current_row][col].target_x = GRID_OFFSET_X + col * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row][col].target_y = GRID_OFFSET_Y + current_row * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row][col].moving = True
                            self.moving_tiles = True
                        
                        # If the cell above has the same value and hasn't been merged yet, merge them
                        elif (self.grid[current_row - 1][col].value == self.grid[current_row][col].value and 
                              not self.grid[current_row - 1][col].merged and 
                              not self.grid[current_row][col].merged):
                            
                            self.grid[current_row - 1][col].value *= 2
                            self.grid[current_row - 1][col].merged = True
                            self.score += self.grid[current_row - 1][col].value
                            self.best_score = max(self.best_score, self.score)
                            self.grid[current_row][col] = Tile()
                            moved = True
                            
                            # Set animation target
                            self.grid[current_row - 1][col].target_x = GRID_OFFSET_X + col * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row - 1][col].target_y = GRID_OFFSET_Y + (current_row - 1) * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row - 1][col].moving = True
                            self.moving_tiles = True
                            
                            break
                        else:
                            break
        
        return moved
    
    def move_down(self):
        moved = False
        self.reset_merged_flags()
        
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 2, -1, -1):
                if self.grid[row][col].value != 0:
                    # Move tile as far down as possible
                    current_row = row
                    while current_row < GRID_SIZE - 1:
                        # If the cell below is empty, move there
                        if self.grid[current_row + 1][col].value == 0:
                            self.grid[current_row + 1][col] = self.grid[current_row][col]
                            self.grid[current_row][col] = Tile()
                            current_row += 1
                            moved = True
                            
                            # Set animation target
                            self.grid[current_row][col].target_x = GRID_OFFSET_X + col * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row][col].target_y = GRID_OFFSET_Y + current_row * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row][col].moving = True
                            self.moving_tiles = True
                        
                        # If the cell below has the same value and hasn't been merged yet, merge them
                        elif (self.grid[current_row + 1][col].value == self.grid[current_row][col].value and 
                              not self.grid[current_row + 1][col].merged and 
                              not self.grid[current_row][col].merged):
                            
                            self.grid[current_row + 1][col].value *= 2
                            self.grid[current_row + 1][col].merged = True
                            self.score += self.grid[current_row + 1][col].value
                            self.best_score = max(self.best_score, self.score)
                            self.grid[current_row][col] = Tile()
                            moved = True
                            
                            # Set animation target
                            self.grid[current_row + 1][col].target_x = GRID_OFFSET_X + col * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row + 1][col].target_y = GRID_OFFSET_Y + (current_row + 1) * (CELL_SIZE + GRID_PADDING)
                            self.grid[current_row + 1][col].moving = True
                            self.moving_tiles = True
                            
                            break
                        else:
                            break
        
        return moved
    
    def update_tiles(self):
        still_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].update():
                    still_moving = True
        return still_moving
    
    def draw_grid(self):
        # Draw grid background
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        (GRID_OFFSET_X - GRID_PADDING, 
                         GRID_OFFSET_Y - GRID_PADDING, 
                         GRID_SIZE * CELL_SIZE + GRID_PADDING * (GRID_SIZE + 1), 
                         GRID_SIZE * CELL_SIZE + GRID_PADDING * (GRID_SIZE + 1)), 
                        border_radius=10)
        
        # Draw tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * (CELL_SIZE + GRID_PADDING)
                y = GRID_OFFSET_Y + row * (CELL_SIZE + GRID_PADDING)
                
                # Draw empty cell
                if self.grid[row][col].value == 0:
                    pygame.draw.rect(self.screen, EMPTY_CELL_COLOR, 
                                    (x, y, CELL_SIZE, CELL_SIZE), 
                                    border_radius=6)
                else:
                    # Draw tile at its current position (for animation)
                    self.grid[row][col].draw(self.screen, 
                                           self.grid[row][col].x, 
                                           self.grid[row][col].y)
    
    def draw_score(self):
        # Draw score box
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        (SCREEN_WIDTH - 230, 20, 100, 60), 
                        border_radius=6)
        
        # Draw best score box
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        (SCREEN_WIDTH - 120, 20, 100, 60), 
                        border_radius=6)
        
        # Draw score labels
        score_label = self.small_font.render("SCORE", True, TEXT_COLOR)
        best_label = self.small_font.render("BEST", True, TEXT_COLOR)
        
        self.screen.blit(score_label, (SCREEN_WIDTH - 180 - score_label.get_width() // 2, 30))
        self.screen.blit(best_label, (SCREEN_WIDTH - 70 - best_label.get_width() // 2, 30))
        
        # Draw score values
        score_value = self.font.render(str(self.score), True, LIGHT_TEXT)
        best_value = self.font.render(str(self.best_score), True, LIGHT_TEXT)
        
        self.screen.blit(score_value, (SCREEN_WIDTH - 180 - score_value.get_width() // 2, 55))
        self.screen.blit(best_value, (SCREEN_WIDTH - 70 - best_value.get_width() // 2, 55))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 72, bold=True)
        title = title_font.render("2048", True, TEXT_COLOR)
        self.screen.blit(title, (GRID_OFFSET_X, 30))
    
    def draw_game_over(self):
        if self.game_over:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Draw game over message
            game_over_font = pygame.font.SysFont(None, 72, bold=True)
            game_over_text = game_over_font.render("Game Over!", True, TEXT_COLOR)
            
            # Draw restart button
            restart_font = pygame.font.SysFont(None, 36, bold=True)
            restart_text = restart_font.render("Try Again", True, LIGHT_TEXT)
            
            pygame.draw.rect(self.screen, GRID_COLOR, 
                            (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20, 160, 50), 
                            border_radius=6)
            
            self.screen.blit(game_over_text, 
                            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 50))
            
            self.screen.blit(restart_text, 
                            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 + 35))
    
    def draw_win(self):
        if self.won:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Draw win message
            win_font = pygame.font.SysFont(None, 72, bold=True)
            win_text = win_font.render("You Win!", True, TEXT_COLOR)
            
            # Draw continue button
            continue_font = pygame.font.SysFont(None, 36, bold=True)
            continue_text = continue_font.render("Continue", True, LIGHT_TEXT)
            
            pygame.draw.rect(self.screen, GRID_COLOR, 
                            (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20, 160, 50), 
                            border_radius=6)
            
            self.screen.blit(win_text, 
                            (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 - 50))
            
            self.screen.blit(continue_text, 
                            (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 + 35))
    
    def draw_toast(self):
        if self.toast_message and pygame.time.get_ticks() < self.toast_timer + self.toast_duration * 1000:
            # Calculate alpha based on remaining time (fade out effect)
            remaining = (self.toast_timer + self.toast_duration * 1000) - pygame.time.get_ticks()
            alpha = min(255, int(255 * remaining / (self.toast_duration * 500)))
            
            # Create toast background
            toast_surface = pygame.Surface((300, 40), pygame.SRCALPHA)
            pygame.draw.rect(toast_surface, (0, 0, 0, min(180, alpha)), (0, 0, 300, 40), border_radius=10)
            
            # Create toast text
            toast_text = self.small_font.render(self.toast_message, True, (255, 255, 255, alpha))
            text_width = toast_text.get_width()
            
            # Position toast in center bottom of screen
            toast_surface.blit(toast_text, ((300 - text_width) // 2, 10))
            self.screen.blit(toast_surface, ((SCREEN_WIDTH - 300) // 2, SCREEN_HEIGHT - 80))
        else:
            self.toast_message = ""
    
    def show_toast(self, message):
        self.toast_message = message
        self.toast_timer = pygame.time.get_ticks()
    
    def reset_game(self):
        self.grid = [[Tile() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.game_over = False
        self.won = False
        self.moving_tiles = False
        
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()
    
    def run(self):
        running = True
        game_state = "idle"  # States: idle, moving, game_over, win
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if game_state == "idle" and not self.game_over and not self.won:
                    if event.type == pygame.KEYDOWN:
                        moved = False
                        
                        if event.key == pygame.K_LEFT:
                            moved = self.move_left()
                        elif event.key == pygame.K_RIGHT:
                            moved = self.move_right()
                        elif event.key == pygame.K_UP:
                            moved = self.move_up()
                        elif event.key == pygame.K_DOWN:
                            moved = self.move_down()
                        
                        if moved:
                            game_state = "moving"
                
                # Handle game over or win screen clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over or self.won:
                        # Check if restart/continue button was clicked
                        x, y = event.pos
                        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 20, 160, 50)
                        
                        if button_rect.collidepoint(x, y):
                            if self.game_over:
                                self.reset_game()
                                game_state = "idle"
                            else:  # won
                                self.won = False
                                game_state = "idle"
            
            # Game logic based on state
            if game_state == "moving":
                # Wait for tiles to finish moving
                if not self.update_tiles() and not self.moving_tiles:
                    # Add a new tile
                    if self.add_random_tile():
                        # Check for win or game over
                        if self.check_win() and not self.won:
                            self.won = True
                            self.show_toast("You reached 2048!")
                        elif self.is_game_over():
                            self.game_over = True
                            self.show_toast("Game Over!")
                    
                    game_state = "idle"
                else:
                    self.moving_tiles = self.update_tiles()
            
            # Drawing
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_grid()
            self.draw_score()
            self.draw_toast()
            
            if self.game_over:
                self.draw_game_over()
            elif self.won:
                self.draw_win()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game2048()
    game.run()
