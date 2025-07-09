# Joshua Cooling

import pygame
import Box2D
from Box2D.b2 import world, dynamicBody, contactListener
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
SCALE = 30
MAX_ESCAPED = 2
DUCKS_PER_LEVEL = 5
UPWARD_FORCE_INTERVAL = 0.5
BASE_UPWARD_FORCE = 318
BASE_HORIZONTAL_FORCE = 50
WHITE = (255,255,255)
BLACK = (0,0,0)

# Game variables
level = 1
score = 0
shots = 3
escaped_ducks = 0
ducks_spawned = 0
ducks_shot = 0
elapsed_time = 0
spawn_delay = 3
dog = None
dog_max_y = 300
dog_min_y = 375
dog_alive = False
dog_pos = (150, dog_min_y)
dog_reach_max = False
nuke = None

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 64)
font_small = pygame.font.Font(None, 24)

# Box2D world
game_world = world(gravity=(0, -10), doSleep=True)

# If ducks collide they die
class MyContactListener(contactListener):
    def __init__(self, game_world):
        super().__init__()
        self.game_world = game_world

    def BeginContact(self, contact):
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB

        # Check if both fixtures belong to ducks
        if isinstance(fixtureA.body.userData, Duck) and isinstance(fixtureB.body.userData, Duck):
            duckA = fixtureA.body.userData
            duckB = fixtureB.body.userData
            
            # Set ducks to dead
            if duckA.alive and duckB.alive:
                duckA.alive = False
                duckB.alive = False

                # Add ducks to total
                global ducks_shot, score
                ducks_shot += 2
                score += 2

# Duck class
class Duck:
    def __init__(self, world, x, y, level):
        self.body = world.CreateDynamicBody(position=(x / SCALE, y / SCALE))
        self.body.CreateCircleFixture(radius=0.5, density=1, friction=0.3)
        self.body.userData = self
        self.alive = True
        self.image = pygame.image.load('duck.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.upward_force_timer = 0
        
        # Set movement direction of the duck
        self.direction = 1 if x < WIDTH // 2 else -1  
        if self.direction == 1:
            self.image = pygame.image.load('duck.png')
            self.image = pygame.transform.scale(self.image, (50, 50))
        elif self.direction == -1:
            self.image = pygame.image.load('duck1.png')
            self.image = pygame.transform.scale(self.image, (50, 50))

        # Increase speed based on level
        self.upward_force = BASE_UPWARD_FORCE + (level * 40)
        self.horizontal_force = BASE_HORIZONTAL_FORCE + (level * 60)

    # Applies force to duck
    def apply_upward_force(self):
        force = Box2D.b2Vec2(self.horizontal_force * self.direction, self.upward_force)
        self.body.ApplyForceToCenter(force, True)

    # Updates ducks position
    def update(self, dt):
        self.upward_force_timer += dt
        if self.upward_force_timer >= UPWARD_FORCE_INTERVAL:
            self.apply_upward_force()
            self.upward_force_timer = 0

    # Draws the duck
    def draw(self):
        if self.alive:
            pos = self.body.position * SCALE
            screen.blit(self.image, (pos[0] - self.image.get_width() // 2, HEIGHT - pos[1] - self.image.get_height() // 2))

    # Checks if duck is off the screen
    def is_off_screen(self):
        pos = self.body.position * SCALE
        return pos[1] < 0 or pos[1] > HEIGHT or pos[0] < 0 or pos[0] > WIDTH
    
# Display Game Over Screen, resets game
def game_over_screen():
    global running, score, ducks_spawned, ducks_shot, escaped_ducks, level, shots, duck, nuke, dog, dog_pos, game_over, dog_alive
    
    screen.fill(BLACK)
    game_over_text = font_large.render("Game Over!", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press 'R' to Restart", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 1.5))

    pygame.display.flip()

    waiting_for_restart = True
    while waiting_for_restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                waiting_for_restart = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                ducks_spawned = 0
                ducks_shot = 0
                escaped_ducks = 0
                level = 1
                shots = 3
                nuke = None
                dog = None
                dog_alive = False

                waiting_for_restart = False

# Create the contact listener and attach it to the world
contact_listener = MyContactListener(game_world)
game_world.contactListener = contact_listener

# Load images
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

dog_image = pygame.image.load('dog.png')
dog_image = pygame.transform.scale(dog_image, (90, 90))

nuke_image = pygame.image.load('nuke.png')
nuke_image = pygame.transform.scale(nuke_image, (40, 60))

ducks_spawned += 1
duck = Duck(game_world, random.randint(50, 750), 200, level)

duck2 = None

# Game loop
running = True

while running:
    dt = clock.tick(FPS) / 1000.0
    screen.blit(background, (0, 0))

    elapsed_time += dt

    # Check if duck escaped
    if duck.is_off_screen() and duck.alive:
        duck.alive = False
        escaped_ducks += 1
        shots = 3
        elapsed_time = 0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if shots > 0:
                shots -= 1
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check for clicks on duck1
                if duck.alive:
                    pos = duck.body.position * SCALE
                    duck_rect = pygame.Rect(pos[0] - 25, HEIGHT - pos[1] - 25, 50, 50)
                    if duck_rect.collidepoint(mouse_x, mouse_y):
                        duck.alive = False
                        score += 1
                        shots = 3
                        ducks_shot += 1
                        elapsed_time = 0
                        
                        dog_alive = True
                        dog_pos = pos

                # Check for clicks on duck2 if it exists
                if duck2 and duck2.alive:
                    pos2 = duck2.body.position * SCALE
                    duck2_rect = pygame.Rect(pos2[0] - 25, HEIGHT - pos2[1] - 25, 50, 50)
                    if duck2_rect.collidepoint(mouse_x, mouse_y):
                        duck2.alive = False
                        score += 1
                        shots = 3
                        ducks_shot += 1
                        elapsed_time = 0
                        
                        dog_alive = True
                        dog_pos = pos2

        # Check for spacebar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            nuke = game_world.CreateDynamicBody(position=((WIDTH - 50) / SCALE, HEIGHT / SCALE))
            nuke.CreateCircleFixture(radius=1, density=5, friction=0.5)

    # If enough time has passed, spawn a new duck
    if not duck.alive and elapsed_time >= spawn_delay:
        elapsed_time = 0
        ducks_spawned += 1
        duck = Duck(game_world, random.randint(50, 750), 200, level)

        # Spawn 2 ducks after 3 ducks have been spawned
        if ducks_spawned == 3:
            duck2 = Duck(game_world, random.randint(50, 750), 200, level)
            ducks_spawned += 1
    
    if duck2 != None:
        duck2.update(dt)
        duck2.draw()
    
    # Dropping of the nuke
    if nuke:
        pos = nuke.position * SCALE
        screen.blit(nuke_image, (pos[0] - nuke_image.get_width() // 2, HEIGHT - pos[1] - nuke_image.get_height() // 2))

        if pos[1] <= 150:
            nuke = None
            game_over_screen()

    # Update physics and duck state
    game_world.Step(1 / FPS, 6, 2)
    duck.update(dt)

    # Create the dog as a kinematic body
    if dog is None and dog_alive == True:
        dog = game_world.CreateKinematicBody(position=(dog_pos[0] / SCALE, dog_min_y / SCALE))
        dog_reach_max = False

    # Move the dog up and down
    if dog:
        if not dog_reach_max:
            dog.linearVelocity = (0, -2)
            if dog.position.y * SCALE <= dog_max_y:
                dog_reach_max = True
        else:
            dog.linearVelocity = (0, 2)
            if dog.position.y * SCALE >= dog_min_y:
                dog_reach_max = False
                game_world.DestroyBody(dog)
                dog = None
                dog_alive = False

        # Draw the dog
        if dog is not None:
            screen.blit(dog_image, (dog.position.x * SCALE, dog.position.y * SCALE))

    # Level progression
    if ducks_spawned == DUCKS_PER_LEVEL:
        if duck.alive == False:
            escaped_ducks = 0
            level += 1
            ducks_shot = 0
            ducks_spawned = 0

    # Game over condition
    if escaped_ducks >= MAX_ESCAPED:
        game_over_screen()

    # Draw the ducks
    duck.draw()
    if duck2:
        duck2.draw()

    # Display text
    score_text = font.render(f"Score: {score}", True, WHITE)
    shot_text = font_small.render(f"Shots: {shots}", True, WHITE)
    level_text = font_small.render(f"Level: {level}", True, WHITE)
    ducks_text = font.render(f"Ducks: {ducks_shot} Shot / {ducks_spawned} Spawned", True, WHITE)
    screen.blit(score_text, (625, 530))
    screen.blit(level_text, (78, 487))
    screen.blit(shot_text, (78, 532))
    screen.blit(ducks_text, (218, 532))

    pygame.display.update()
