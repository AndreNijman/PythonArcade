import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 560, 620
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Map
TILE_SIZE = 20
maze = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #      # ##.######",
    "      .   #      #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#...##................##...#",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

# Entities
pacman_pos = [14, 23]
direction = [0, 0]
score = 0

ghost_pos = [14, 11]

# Timers
move_delay = 6
move_counter = 0

ghost_delay = 12
ghost_counter = 0

font = pygame.font.SysFont("Arial", 24)

def draw_maze():
    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if char == '#':
                pygame.draw.rect(WIN, BLUE, rect)
            elif char == '.':
                pygame.draw.circle(WIN, WHITE, rect.center, 3)
            elif char == 'o':
                pygame.draw.circle(WIN, WHITE, rect.center, 6)

def move_pacman():
    global pacman_pos, score
    new_x = pacman_pos[0] + direction[0]
    new_y = pacman_pos[1] + direction[1]
    if maze[new_y][new_x] not in '#':
        pacman_pos = [new_x, new_y]
        tile = maze[new_y][new_x]
        if tile == '.' or tile == 'o':
            row = list(maze[new_y])
            row[new_x] = ' '
            maze[new_y] = ''.join(row)
            score += 10 if tile == '.' else 50

def draw_pacman():
    x, y = pacman_pos
    center = (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2)
    pygame.draw.circle(WIN, YELLOW, center, TILE_SIZE//2)

def draw_ghost():
    x, y = ghost_pos
    center = (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2)
    pygame.draw.circle(WIN, RED, center, TILE_SIZE//2)

def move_ghost():
    global ghost_pos
    options = []
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = ghost_pos[0]+dx, ghost_pos[1]+dy
        if maze[ny][nx] != '#':
            dist = abs(nx - pacman_pos[0]) + abs(ny - pacman_pos[1])
            options.append((dist, (nx, ny)))
    if options:
        options.sort()
        ghost_pos = options[0][1]

def draw_score():
    text = font.render(f"Score: {score}", True, WHITE)
    WIN.blit(text, (10, HEIGHT - 30))

def check_game_over():
    return pacman_pos == ghost_pos

def main():
    global direction, move_counter, ghost_counter
    while True:
        CLOCK.tick(FPS)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: direction = [-1, 0]
                if event.key == pygame.K_RIGHT: direction = [1, 0]
                if event.key == pygame.K_UP: direction = [0, -1]
                if event.key == pygame.K_DOWN: direction = [0, 1]

        move_counter += 1
        if move_counter >= move_delay:
            move_counter = 0
            move_pacman()

        ghost_counter += 1
        if ghost_counter >= ghost_delay:
            ghost_counter = 0
            move_ghost()

        if check_game_over():
            text = font.render("Game Over", True, RED)
            WIN.blit(text, (WIDTH//2 - 60, HEIGHT//2))
            pygame.display.update()
            pygame.time.wait(2000)
            pygame.quit()
            sys.exit()

        draw_maze()
        draw_pacman()
        draw_ghost()
        draw_score()

        pygame.display.update()

main()
