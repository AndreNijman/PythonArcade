import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Player
player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 40, 50, 20)
player_speed = 6
bullets = []

# Enemies
enemy_rows = 4
enemy_cols = 6
enemies = []
enemy_dir = 1
enemy_speed = 1

for row in range(enemy_rows):
    for col in range(enemy_cols):
        enemies.append(pygame.Rect(80 + col * 60, 60 + row * 40, 40, 30))

# Game loop
running = True
while running:
    CLOCK.tick(60)
    WIN.fill(BLACK)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bullets.append(pygame.Rect(player.centerx - 2, player.top, 4, 10))

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += player_speed

    # Bullet movement
    for b in bullets:
        b.y -= 8
    bullets = [b for b in bullets if b.bottom > 0]

    # Enemy movement
    move_down = False
    for e in enemies:
        e.x += enemy_dir * enemy_speed
        if e.right >= WIDTH or e.left <= 0:
            move_down = True
    if move_down:
        enemy_dir *= -1
        for e in enemies:
            e.y += 20

    # Bullet collision
    for b in bullets[:]:
        for e in enemies[:]:
            if b.colliderect(e):
                bullets.remove(b)
                enemies.remove(e)
                break

    # Game over check
    for e in enemies:
        if e.bottom >= HEIGHT - 50:
            running = False

    # Draw everything
    pygame.draw.rect(WIN, GREEN, player)
    for b in bullets:
        pygame.draw.rect(WIN, WHITE, b)
    for e in enemies:
        pygame.draw.rect(WIN, RED, e)

    pygame.display.flip()
