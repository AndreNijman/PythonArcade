import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 600, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Colors
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# Frog setup
frog = pygame.Rect(WIDTH // 2 - 15, HEIGHT - 50, 30, 30)
frog_start_y = HEIGHT - 50
frog_speed = 40

# Cars
lanes = [120, 180, 240, 300, 360]
cars = []
car_speed = [3, -4, 2, -3, 5]

for i, y in enumerate(lanes):
    for j in range(3):
        x = j * 220 + random.randint(0, 60)
        cars.append({"rect": pygame.Rect(x, y, 70, 30), "speed": car_speed[i], "lane": y})

# Draw frog sprite
def draw_frog(x, y):
    pygame.draw.rect(WIN, GREEN, (x, y, 30, 30))              # body
    pygame.draw.circle(WIN, DARK_GREEN, (x + 7, y), 6)        # left eye
    pygame.draw.circle(WIN, DARK_GREEN, (x + 23, y), 6)       # right eye
    pygame.draw.rect(WIN, DARK_GREEN, (x - 5, y + 10, 10, 10))  # left leg
    pygame.draw.rect(WIN, DARK_GREEN, (x + 25, y + 10, 10, 10))  # right leg

# Draw car sprite
def draw_car(rect, color):
    pygame.draw.rect(WIN, color, rect)                          # body
    pygame.draw.rect(WIN, BLACK, (rect.x + 10, rect.y + 5, 15, 10))  # left window
    pygame.draw.rect(WIN, BLACK, (rect.x + 35, rect.y + 5, 15, 10))  # right window
    pygame.draw.circle(WIN, BLACK, (rect.x + 10, rect.y + 28), 5)  # wheels
    pygame.draw.circle(WIN, BLACK, (rect.x + 60, rect.y + 28), 5)

# Game loop
running = True
while running:
    CLOCK.tick(30)
    WIN.fill(GRAY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        frog.y -= frog_speed
        pygame.time.wait(100)
    elif keys[pygame.K_DOWN] and frog.y + frog_speed < HEIGHT:
        frog.y += frog_speed
        pygame.time.wait(100)
    elif keys[pygame.K_LEFT] and frog.x - frog_speed >= 0:
        frog.x -= frog_speed
        pygame.time.wait(100)
    elif keys[pygame.K_RIGHT] and frog.x + frog_speed < WIDTH:
        frog.x += frog_speed
        pygame.time.wait(100)

    # Move cars
    for car in cars:
        car["rect"].x += car["speed"]
        if car["speed"] > 0 and car["rect"].left > WIDTH:
            car["rect"].right = 0
        elif car["speed"] < 0 and car["rect"].right < 0:
            car["rect"].left = WIDTH

    # Collision
    for car in cars:
        if frog.colliderect(car["rect"]):
            frog.x = WIDTH // 2 - 15
            frog.y = frog_start_y

    # Win check
    if frog.top < 100:
        frog.x = WIDTH // 2 - 15
        frog.y = frog_start_y

    # Draw road lanes
    pygame.draw.rect(WIN, BLACK, (0, 100, WIDTH, 300))
    for y in lanes:
        pygame.draw.line(WIN, WHITE, (0, y - 2), (WIDTH, y - 2), 2)

    # Draw everything
    for car in cars:
        color = RED if car["speed"] > 0 else BLUE
        draw_car(car["rect"], color)

    draw_frog(frog.x, frog.y)

    pygame.display.flip()
