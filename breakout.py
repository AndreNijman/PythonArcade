import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Paddle
paddle = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 15)
paddle_speed = 7

# Ball
ball = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2, 20, 20)
ball_speed = [5, -5]

# Bricks
bricks = []
rows, cols = 5, 8
brick_w = WIDTH // cols
brick_h = 30
for row in range(rows):
    for col in range(cols):
        bricks.append(pygame.Rect(col * brick_w, row * brick_h + 50, brick_w - 5, brick_h - 5))

# Game loop
running = True
while running:
    WIN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += paddle_speed

    # Ball movement
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Ball bounce
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed[0] *= -1
    if ball.top <= 0:
        ball_speed[1] *= -1
    if ball.colliderect(paddle):
        ball_speed[1] *= -1

    # Ball hits brick
    for brick in bricks[:]:
        if ball.colliderect(brick):
            bricks.remove(brick)
            ball_speed[1] *= -1
            break

    # Game over
    if ball.bottom >= HEIGHT:
        running = False

    # Draw
    pygame.draw.rect(WIN, BLUE, paddle)
    pygame.draw.ellipse(WIN, WHITE, ball)
    for brick in bricks:
        pygame.draw.rect(WIN, RED, brick)

    pygame.display.flip()
    CLOCK.tick(60)
