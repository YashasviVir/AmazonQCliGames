import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 7  # Reduced from 8 to 7
CELL_SIZE = 70
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2 + 30  # Added extra offset to move grid down
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (240, 240, 240)
GRID_COLOR = (200, 200, 200)
SELECTION_COLOR = (255, 140, 0)  # Bright orange for better visibility

# Gem colors - darker
GEM_COLORS = [
    (180, 60, 60),    # Darker Red
    (60, 140, 60),    # Darker Green
    (60, 60, 180),    # Darker Blue
    (180, 180, 60),   # Darker Yellow
    (180, 60, 180),   # Darker Magenta
    (60, 180, 180),   # Darker Cyan
]

class Gem:
    def __init__(self, row, col, color_idx):
        self.row = row
        self.col = col
        self.color_idx = color_idx
        self.color = GEM_COLORS[color_idx]
        self.x = GRID_OFFSET_X + col * CELL_SIZE
        self.y = GRID_OFFSET_Y + row * CELL_SIZE
        self.selected = False
        self.matched = False
        self.falling = False
        self.target_y = self.y
        self.target_x = self.x
        self.swapping = False
        self.swap_speed = 8
        
    def draw(self, screen):
        # Draw gem as a simple block with rounded corners
        pygame.draw.rect(screen, self.color, 
                        (self.x + 5, self.y + 5, CELL_SIZE - 10, CELL_SIZE - 10), 
                        border_radius=10)
        
        # Draw highlight for selected gem
        if self.selected:
            pygame.draw.rect(screen, SELECTION_COLOR, 
                            (self.x + 2, self.y + 2, CELL_SIZE - 4, CELL_SIZE - 4), 
                            3, border_radius=10)
    
    def update(self):
        moving = False
        
        # Handle falling animation
        if self.falling:
            # Move towards target position
            move_speed = 15
            if self.y < self.target_y:
                self.y += move_speed
                if self.y >= self.target_y:
                    self.y = self.target_y
                    self.falling = False
                moving = True
            elif self.y > self.target_y:
                self.y -= move_speed
                if self.y <= self.target_y:
                    self.y = self.target_y
                    self.falling = False
                moving = True
        
        # Handle swapping animation
        if self.swapping:
            # Move towards target position
            if abs(self.x - self.target_x) > self.swap_speed:
                self.x += self.swap_speed if self.x < self.target_x else -self.swap_speed
                moving = True
            elif abs(self.x - self.target_x) > 0:
                self.x = self.target_x
                moving = True
                
            if abs(self.y - self.target_y) > self.swap_speed:
                self.y += self.swap_speed if self.y < self.target_y else -self.swap_speed
                moving = True
            elif abs(self.y - self.target_y) > 0:
                self.y = self.target_y
                moving = True
                
            if self.x == self.target_x and self.y == self.target_y:
                self.swapping = False
                
        return moving

class Match3Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Match-3 Puzzle Game")
        self.clock = pygame.time.Clock()
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected_gem = None
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.toast_message = ""
        self.toast_timer = 0
        self.toast_duration = 1.5  # seconds
        self.initialize_grid()
        
    def initialize_grid(self):
        # Create initial grid with random gems
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color_idx = random.randint(0, len(GEM_COLORS) - 1)
                self.grid[row][col] = Gem(row, col, color_idx)
        
        # Check for initial matches and replace them
        while self.find_matches():
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col].matched:
                        color_idx = random.randint(0, len(GEM_COLORS) - 1)
                        self.grid[row][col] = Gem(row, col, color_idx)
    
    def draw_grid(self):
        # Draw grid background
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                pygame.draw.rect(self.screen, GRID_COLOR, 
                                (GRID_OFFSET_X + col * CELL_SIZE, 
                                 GRID_OFFSET_Y + row * CELL_SIZE, 
                                 CELL_SIZE, CELL_SIZE), 1)
        
        # Draw gems
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].draw(self.screen)
    
    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        # Position the score at the top center of the screen, above the grid
        text_width = score_text.get_width()
        self.screen.blit(score_text, ((SCREEN_WIDTH - text_width) // 2, GRID_OFFSET_Y - 40))
    
    def draw_toast(self):
        if self.toast_message and time.time() < self.toast_timer + self.toast_duration:
            # Calculate alpha based on remaining time (fade out effect)
            remaining = (self.toast_timer + self.toast_duration) - time.time()
            alpha = min(255, int(255 * remaining / (self.toast_duration / 2)))
            
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
        self.toast_timer = time.time()
    
    def get_gem_at_pos(self, pos):
        x, y = pos
        if (x < GRID_OFFSET_X or x >= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE or
            y < GRID_OFFSET_Y or y >= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):
            return None
        
        col = (x - GRID_OFFSET_X) // CELL_SIZE
        row = (y - GRID_OFFSET_Y) // CELL_SIZE
        
        return self.grid[row][col] if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE else None
    
    def are_adjacent(self, gem1, gem2):
        return ((abs(gem1.row - gem2.row) == 1 and gem1.col == gem2.col) or
                (abs(gem1.col - gem2.col) == 1 and gem1.row == gem2.row))
    
    def swap_gems(self, gem1, gem2):
        # Safety check to prevent crashes
        if not gem1 or not gem2:
            return
            
        # Update grid positions
        self.grid[gem1.row][gem1.col], self.grid[gem2.row][gem2.col] = self.grid[gem2.row][gem2.col], self.grid[gem1.row][gem1.col]
        
        # Update gem positions
        gem1.row, gem2.row = gem2.row, gem1.row
        gem1.col, gem2.col = gem2.col, gem1.col
        
        # Set target positions for animation
        gem1.target_x = GRID_OFFSET_X + gem1.col * CELL_SIZE
        gem1.target_y = GRID_OFFSET_Y + gem1.row * CELL_SIZE
        gem2.target_x = GRID_OFFSET_X + gem2.col * CELL_SIZE
        gem2.target_y = GRID_OFFSET_Y + gem2.row * CELL_SIZE
        
        # Enable swapping animation
        gem1.swapping = True
        gem2.swapping = True
    
    def find_matches(self):
        found_matches = False
        
        # Reset matched status
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].matched = False
        
        # Check horizontal matches
        for row in range(GRID_SIZE):
            col = 0
            while col < GRID_SIZE - 2:
                if (self.grid[row][col] and self.grid[row][col+1] and self.grid[row][col+2] and
                    self.grid[row][col].color_idx == self.grid[row][col+1].color_idx == self.grid[row][col+2].color_idx):
                    
                    # Mark gems as matched
                    match_length = 3
                    while col + match_length < GRID_SIZE and self.grid[row][col+match_length] and self.grid[row][col].color_idx == self.grid[row][col+match_length].color_idx:
                        match_length += 1
                    
                    for i in range(match_length):
                        self.grid[row][col+i].matched = True
                    
                    found_matches = True
                    col += match_length
                else:
                    col += 1
        
        # Check vertical matches
        for col in range(GRID_SIZE):
            row = 0
            while row < GRID_SIZE - 2:
                if (self.grid[row][col] and self.grid[row+1][col] and self.grid[row+2][col] and
                    self.grid[row][col].color_idx == self.grid[row+1][col].color_idx == self.grid[row+2][col].color_idx):
                    
                    # Mark gems as matched
                    match_length = 3
                    while row + match_length < GRID_SIZE and self.grid[row+match_length][col] and self.grid[row][col].color_idx == self.grid[row+match_length][col].color_idx:
                        match_length += 1
                    
                    for i in range(match_length):
                        self.grid[row+i][col].matched = True
                    
                    found_matches = True
                    row += match_length
                else:
                    row += 1
        
        return found_matches
    
    def remove_matches(self):
        match_count = 0
        
        # Count matches and update score
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] and self.grid[row][col].matched:
                    match_count += 1
        
        # Add score based on matches (more matches = exponentially more points)
        if match_count > 0:
            self.score += match_count * 10
        
        # Remove matched gems
        for col in range(GRID_SIZE):
            # Move from bottom to top
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] and self.grid[row][col].matched:
                    self.grid[row][col] = None
    
    def drop_gems(self):
        # For each column
        for col in range(GRID_SIZE):
            # Count empty spaces and move gems down
            empty_count = 0
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is None:
                    empty_count += 1
                elif empty_count > 0:
                    # Move this gem down by empty_count
                    self.grid[row + empty_count][col] = self.grid[row][col]
                    self.grid[row][col] = None
                    
                    # Update gem position
                    self.grid[row + empty_count][col].row = row + empty_count
                    self.grid[row + empty_count][col].falling = True
                    self.grid[row + empty_count][col].target_y = GRID_OFFSET_Y + (row + empty_count) * CELL_SIZE
            
            # Fill top with new gems
            for row in range(empty_count):
                color_idx = random.randint(0, len(GEM_COLORS) - 1)
                self.grid[row][col] = Gem(row, col, color_idx)
                # Start above the grid and fall into place
                self.grid[row][col].y = GRID_OFFSET_Y - CELL_SIZE
                self.grid[row][col].falling = True
                self.grid[row][col].target_y = GRID_OFFSET_Y + row * CELL_SIZE
    
    def update_gems(self):
        still_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    if self.grid[row][col].update():
                        still_moving = True
        return still_moving
    
    def run(self):
        running = True
        game_state = "idle"  # States: idle, selecting, swapping, matching, dropping
        swap_timer = 0
        last_swapped_gems = (None, None)  # Keep track of the last two gems that were swapped
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if game_state == "idle" or game_state == "selecting":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        gem = self.get_gem_at_pos(event.pos)
                        if gem:
                            if self.selected_gem is None:
                                # First selection
                                self.selected_gem = gem
                                gem.selected = True
                                game_state = "selecting"
                            else:
                                # Second selection - check if adjacent
                                if self.are_adjacent(self.selected_gem, gem):
                                    # Try the swap
                                    self.swap_gems(self.selected_gem, gem)
                                    # Store the gems that were swapped
                                    last_swapped_gems = (self.selected_gem, gem)
                                    self.selected_gem.selected = False
                                    self.selected_gem = None
                                    game_state = "swapping"
                                    swap_timer = time.time()
                                else:
                                    # Not adjacent, make this the new selection
                                    self.selected_gem.selected = False
                                    self.selected_gem = gem
                                    gem.selected = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Deselect current gem
                        if self.selected_gem:
                            self.selected_gem.selected = False
                            self.selected_gem = None
                            game_state = "idle"
            
            # Game logic based on state
            if game_state == "swapping":
                # Wait for swap animation to complete
                if not self.update_gems():
                    # Check if swap created matches
                    if self.find_matches():
                        game_state = "matching"
                    elif time.time() - swap_timer > 0.3:
                        try:
                            # Get the two gems that were last swapped
                            gem1, gem2 = last_swapped_gems
                            
                            # Swap them back if they're valid
                            if gem1 and gem2:
                                self.swap_gems(gem1, gem2)
                                self.show_toast("Not a valid match!")
                            
                            game_state = "swapping_back"
                        except Exception as e:
                            print(f"Error during swap back: {e}")
                            # Recover gracefully
                            game_state = "idle"
            
            elif game_state == "swapping_back":
                # Wait for swap-back animation to complete
                if not self.update_gems():
                    game_state = "idle"
            
            elif game_state == "matching":
                self.remove_matches()
                self.drop_gems()
                game_state = "dropping"
            
            elif game_state == "dropping":
                # Wait for all gems to finish falling
                if not self.update_gems():
                    # Check for new matches after dropping
                    if self.find_matches():
                        game_state = "matching"
                    else:
                        game_state = "idle"
            
            # Drawing
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_grid()
            self.draw_score()
            self.draw_toast()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Match3Game()
    game.run()
