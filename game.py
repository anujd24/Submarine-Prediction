import pygame
import joblib
import random
import sys
import time

# Initialize PyGame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Submarine Mine Stopper - Final Fix")

# Colors
BLUE = (0, 0, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game variables
gravity = 0.5
game_active = True
score = 0
submarine_speed = 3

# Load model
try:
    model = joblib.load("rock_mine.pkl")
except:
    print("Error: Could not load model")
    sys.exit()

class Submarine:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.width = 50
        self.height = 30
        self.jump_power = 0
        self.is_jumping = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.frozen = False  # New state to completely freeze submarine
    
    def update(self):
        if self.frozen:
            return  # Skip all movement if frozen
            
        # Apply gravity if jumping
        if self.is_jumping:
            self.y -= self.jump_power
            self.jump_power -= gravity
            if self.y >= 300:  # Water surface
                self.y = 300
                self.is_jumping = False
        
        # Update rectangle position
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def jump(self):
        if not self.is_jumping and not self.frozen:
            self.is_jumping = True
            self.jump_power = 10
    
    def freeze(self):
        self.frozen = True  # Completely stop all movement
    
    def draw(self):
        pygame.draw.ellipse(screen, BLUE, self.rect)

class Obstacle:
    def __init__(self, x, obj_type):
        self.type = obj_type
        self.width = 40
        self.height = 40
        self.x = x
        self.y = 340
        self.detected = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.passed = False
    
    def update(self):
        self.x -= 3
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self):
        color = RED if self.type == "mine" else GREEN
        pygame.draw.rect(screen, color, self.rect)
        if self.detected:
            label = "MINE!" if self.type == "mine" else "ROCK"
            font = pygame.font.SysFont(None, 24)
            text = font.render(label, True, WHITE)
            screen.blit(text, (self.rect.x, self.rect.y - 20))

def show_game_over():
    font = pygame.font.SysFont(None, 72)
    text = font.render("GAME OVER", True, RED)
    screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - 50))
    
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, screen_height//2 + 20))
    
    restart_text = font.render("Press R to restart", True, WHITE)
    screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, screen_height//2 + 70))
    
    pygame.display.flip()

# Game objects
submarine = Submarine()
obstacles = []
obstacle_timer = 0

# Main game loop
clock = pygame.time.Clock()
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active and not submarine.frozen:
                submarine.jump()
            if event.key == pygame.K_r and not game_active:
                # Reset game
                game_active = True
                submarine = Submarine()
                obstacles = []
                score = 0
    
    if game_active and not submarine.frozen:
        # Handle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            submarine.x = max(0, submarine.x - submarine_speed)
        if keys[pygame.K_RIGHT]:
            submarine.x = min(screen_width - submarine.width, submarine.x + submarine_speed)
        
        submarine.update()
        
        # Generate obstacles
        obstacle_timer += 1
        if obstacle_timer > 60:
            obstacle_timer = 0
            obstacle_type = random.choice(["mine", "rock"])
            obstacles.append(Obstacle(screen_width, obstacle_type))
        
        # Update and check obstacles
        for obstacle in obstacles[:]:
            obstacle.update()
            
            # SONAR detection
            if abs(obstacle.x - submarine.x) < 150 and not obstacle.detected:
                sonar_data = [random.random() for _ in range(60)]
                prediction = model.predict([sonar_data])[0]
                obstacle.detected = True
            
            # Collision detection
                if submarine.rect.colliderect(obstacle.rect):
                    if obstacle.type == "mine":
                        # Immediately stop all game activity
                        game_active = False
                        # Freeze submarine in place
                        submarine.x = submarine.x  # Explicitly lock position
                        submarine.y = submarine.y
                        submarine.is_jumping = False
                        # Prevent any further movement processing
                        submarine.frozen = True
                        # Show explosion effect
                        pygame.draw.circle(screen, (255, 100, 0), submarine.rect.center, 30)
                        pygame.display.flip()
                        # Short delay to show explosion
                        pygame.time.delay(500)
                        
                    elif obstacle.type == "rock" and submarine.is_jumping:
                        if not obstacle.passed:
                            score += 10
                            obstacle.passed = True
            
            # Remove off-screen obstacles
            if obstacle.x < -50:
                obstacles.remove(obstacle)
    
    # Drawing
    screen.fill(BLACK)
    
    # Draw water
    pygame.draw.rect(screen, (0, 20, 100), (0, 350, screen_width, screen_height-350))
    
    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw()
    
    # Draw submarine
    submarine.draw()
    
    # Draw score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    # Draw instructions
    if not game_active:
        show_game_over()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()