import pygame
import sys

# Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 36)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ball
ball = pygame.Rect(WIDTH//2 - 15, HEIGHT//2 - 15, 30, 30)
ball_speed = [5, 5]

# Paddles
paddle_speed = 7
p1 = pygame.Rect(20, HEIGHT//2 - 60, 10, 120)
p2 = pygame.Rect(WIDTH - 30, HEIGHT//2 - 60, 10, 120)

# Scores
score1 = 0
score2 = 0

# Game loop
while True:
    WIN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and p1.top > 0:
        p1.y -= paddle_speed
    if keys[pygame.K_s] and p1.bottom < HEIGHT:
        p1.y += paddle_speed
    if keys[pygame.K_UP] and p2.top > 0:
        p2.y -= paddle_speed
    if keys[pygame.K_DOWN] and p2.bottom < HEIGHT:
        p2.y += paddle_speed

    # Ball movement
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Bounce
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed[1] *= -1
    if ball.colliderect(p1) or ball.colliderect(p2):
        ball_speed[0] *= -1

    # Score
    if ball.left <= 0:
        score2 += 1
        ball.center = (WIDTH//2, HEIGHT//2)
        ball_speed[0] *= -1
    if ball.right >= WIDTH:
        score1 += 1
        ball.center = (WIDTH//2, HEIGHT//2)
        ball_speed[0] *= -1

    # Draw
    pygame.draw.rect(WIN, WHITE, p1)
    pygame.draw.rect(WIN, WHITE, p2)
    pygame.draw.ellipse(WIN, WHITE, ball)
    pygame.draw.aaline(WIN, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
    WIN.blit(FONT.render(str(score1), True, WHITE), (WIDTH//4, 20))
    WIN.blit(FONT.render(str(score2), True, WHITE), (WIDTH*3//4, 20))

    pygame.display.flip()
    CLOCK.tick(60)
