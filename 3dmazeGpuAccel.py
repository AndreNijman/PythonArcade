import pygame
import math
import sys
import random
import numpy as np
from numba import cuda

pygame.init()
WIDTH, HEIGHT = 1920, 1080
pygame.display.set_caption("3D Maze Test")
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Settings
TILE = 64
MAP_W, MAP_H = 16, 16
FOV = math.pi / 3
RAYS = 10000
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
MAP_np = np.array([[int(cell) for cell in row] for row in MAP], dtype=np.int32)
MAP_d = cuda.to_device(MAP_np)

# Player
px, py = TILE + 10, TILE + 10
angle = 0.0

# Output buffers
wall_heights = np.zeros(RAYS, dtype=np.float32)
wall_colors = np.zeros(RAYS, dtype=np.float32)

@cuda.jit
def cast_rays_cuda(px, py, angle, wall_heights, wall_colors, MAP):
    r = cuda.grid(1)
    if r >= wall_heights.size:
        return

    FOV = 1.0472  # pi/3
    TILE = 64.0
    RAYS = wall_heights.size
    STEP_ANGLE = FOV / RAYS

    ray_angle = angle - FOV / 2 + r * STEP_ANGLE
    sin_a = math.sin(ray_angle)
    cos_a = math.cos(ray_angle)

    for depth in range(1, 400):
        rx = px + cos_a * depth
        ry = py + sin_a * depth
        x = int(rx // TILE)
        y = int(ry // TILE)
        if 0 <= x < MAP.shape[1] and 0 <= y < MAP.shape[0]:
            if MAP[y][x] == 1:
                wall_heights[r] = 20000.0 / (depth + 0.1)
                wall_colors[r] = 255.0 / (1.0 + depth * depth * 0.0001)
                return

# Main loop
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

    threads_per_block = 128
    blocks_per_grid = (RAYS + threads_per_block - 1) // threads_per_block
    cast_rays_cuda[blocks_per_grid, threads_per_block](px, py, angle, wall_heights, wall_colors, MAP_d)
    cuda.synchronize()

    for r in range(RAYS):
        color = max(0, min(255, float(wall_colors[r])))
        height = max(0, min(HEIGHT, float(wall_heights[r])))
        x = int(r * WIDTH / RAYS)
        w = int(WIDTH / RAYS) + 1  # +1 avoids gaps
        pygame.draw.rect(WIN, (color, color, color),
                         (x, HEIGHT // 2 - int(height) // 2, w, int(height)))

    pygame.display.flip()
    CLOCK.tick(60)
