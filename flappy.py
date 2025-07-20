import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 400, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 36)

# Colors
SKY = (135, 206, 250)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)

# Bird setup
bird_x = 100
bird_y = HEIGHT // 2
bird_size = 30
velocity = 0
gravity = 0.5
jump = -10

# Wing flap animation
wing_timer = 0
wing_up = True

# Pipes
pipe_width = 60
gap = 180
pipes = []
pipe_timer = 0

# Game loop
running = True
while running:
    WIN.fill(SKY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            velocity = jump

    # Bird physics
    velocity += gravity
    bird_y += int(velocity)

    # Animate wings
    wing_timer += 1
    if wing_timer >= 10:
        wing_up = not wing_up
        wing_timer = 0

    # Pipe movement and generation
    pipe_timer += 1
    if pipe_timer >= 90:
        top = random.randint(50, HEIGHT - gap - 50)
        pipes.append(pygame.Rect(WIDTH, 0, pipe_width, top))
        pipes.append(pygame.Rect(WIDTH, top + gap, pipe_width, HEIGHT))
        pipe_timer = 0

    for pipe in pipes:
        pipe.x -= 4

    pipes = [p for p in pipes if p.right > 0]

    # Bird parts
    body = pygame.Rect(bird_x, bird_y, bird_size, bird_size)
    eye = pygame.Rect(bird_x + 20, bird_y + 5, 5, 5)
    beak = pygame.Rect(bird_x + bird_size, bird_y + 10, 10, 10)
    wing_y_offset = -5 if wing_up else 5
    wing = pygame.Rect(bird_x - 10, bird_y + 10 + wing_y_offset, 10, 10)

    # Collision
    for pipe in pipes:
        if body.colliderect(pipe):
            running = False
    if body.top <= 0 or body.bottom >= HEIGHT:
        running = False

    # Draw bird
    pygame.draw.rect(WIN, YELLOW, body)
    pygame.draw.rect(WIN, WHITE, eye)
    pygame.draw.rect(WIN, ORANGE, beak)
    pygame.draw.rect(WIN, RED, wing)

    # Draw pipes
    for pipe in pipes:
        pygame.draw.rect(WIN, GREEN, pipe)

    pygame.display.flip()
    CLOCK.tick(60)
