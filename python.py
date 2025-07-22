import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
DARK_GRAY = (40, 40, 40)
OBSTACLE_COLOR = (100, 100, 100)
WHITE = (255, 255, 255)

# Snake setup
snake = [(10, 10)]
direction = (1, 0)
grow = False

# Food setup
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

# Obstacles
obstacles = []
obstacle_spawn_timer = 0
game_over = False
font = pygame.font.SysFont(None, 48)

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(WIN, DARK_GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(WIN, DARK_GRAY, (0, y), (WIDTH, y))

def draw():
    WIN.fill(BLACK)
    draw_grid()

    for ox, oy in obstacles:
        pygame.draw.rect(WIN, OBSTACLE_COLOR, (ox * CELL_SIZE, oy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for i, (x, y) in enumerate(snake):
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(WIN, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    fx, fy = food
    pygame.draw.rect(WIN, RED, (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    if game_over:
        text = font.render("Game Over - Press R", True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        WIN.blit(text, rect)

    pygame.display.flip()

def reset():
    global snake, direction, food, obstacles, obstacle_spawn_timer, game_over
    snake = [(10, 10)]
    direction = (1, 0)
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    obstacles = []
    obstacle_spawn_timer = 0
    game_over = False

while True:
    CLOCK.tick(10)
    if not game_over:
        obstacle_spawn_timer += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                direction = (1, 0)
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                reset()

    if not game_over:
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Check collision
        if (
            head in snake or
            head[0] < 0 or head[0] >= GRID_WIDTH or
            head[1] < 0 or head[1] >= GRID_HEIGHT or
            head in obstacles
        ):
            game_over = True
        else:
            snake.insert(0, head)
            if head == food:
                while True:
                    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                    if food not in snake and food not in obstacles:
                        break
            else:
                snake.pop()

        # Spawn new obstacle every ~3 seconds
        if obstacle_spawn_timer >= 30:
            obstacle_spawn_timer = 0
            while True:
                ox = random.randint(0, GRID_WIDTH - 1)
                oy = random.randint(0, GRID_HEIGHT - 1)
                if (ox, oy) not in snake and (ox, oy) != food and (ox, oy) not in obstacles:
                    obstacles.append((ox, oy))
                    break

    draw()
