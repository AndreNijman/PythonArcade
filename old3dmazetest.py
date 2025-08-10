import pygame
import math
import sys
import random
# testing out a commit maker
pygame.init()
WIDTH, HEIGHT = 640, 480
pygame.display.set_caption("3D Maze Test")
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Settings
TILE = 64
MAP_W, MAP_H = 16, 16
FOV = math.pi / 3
RAYS = 500
STEP_ANGLE = FOV / RAYS
SPEED = 3

# Maze generation (recursive backtracker)
def generate_maze(w, h):
    maze = [["1"] * w for _ in range(h)]
    visited = [[False] * w for _ in range(h)]

    def carve(x, y):
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        visited[y][x] = True
        maze[y][x] = "0"
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < w - 1 and 1 <= ny < h - 1 and not visited[ny][nx]:
                maze[y + dy // 2][x + dx // 2] = "0"
                carve(nx, ny)

    carve(1, 1)
    return maze

MAP = generate_maze(MAP_W, MAP_H)

# Player
px, py = TILE + 10, TILE + 10
angle = 0

def cast_rays():
    start_angle = angle - FOV / 2
    for r in range(RAYS):
        ray_angle = start_angle + r * STEP_ANGLE
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        for depth in range(1, 400):
            x = int((px + cos_a * depth) // TILE)
            y = int((py + sin_a * depth) // TILE)
            if 0 <= x < MAP_W and 0 <= y < MAP_H:
                if MAP[y][x] == "1":
                    wall_height = 20000 / (depth + 0.1)
                    color = 255 / (1 + depth * depth * 0.0001)
                    pygame.draw.rect(WIN, (color, color, color),
                                     (r * (WIDTH // RAYS), HEIGHT // 2 - wall_height // 2,
                                      WIDTH // RAYS, wall_height))
                    break

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle -= 0.05
    if keys[pygame.K_RIGHT]:
        angle += 0.05
    if keys[pygame.K_w]:
        nx = px + math.cos(angle) * SPEED
        ny = py + math.sin(angle) * SPEED
        if MAP[int(ny // TILE)][int(nx // TILE)] == "0":
            px, py = nx, ny
    if keys[pygame.K_s]:
        nx = px - math.cos(angle) * SPEED
        ny = py - math.sin(angle) * SPEED
        if MAP[int(ny // TILE)][int(nx // TILE)] == "0":
            px, py = nx, ny

    WIN.fill((30, 30, 30))
    cast_rays()
    pygame.display.flip()
    CLOCK.tick(60)
