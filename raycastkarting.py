import pygame
import sys
import numpy as np
import math

# Constants
WIDTH, HEIGHT = 640, 480
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH
MAX_DEPTH = 500
MAP_SIZE = 64

# Colors
ROAD_COLOR = (50, 50, 50)
GRASS_COLOR = (20, 120, 20)

# Pygame init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Generate real curvy track
track_map = np.zeros((MAP_SIZE, MAP_SIZE), dtype=np.uint8)

control_points = [
    (10, 10), (20, 12), (30, 8), (40, 14), (50, 30),
    (45, 45), (30, 50), (15, 42), (5, 30), (6, 15), (10, 10)
]

def draw_thick_line(x0, y0, x1, y1, thickness):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2)
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + (x1 - x0) * t)
        y = int(y0 + (y1 - y0) * t)
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                tx = x + dx
                ty = y + dy
                if 0 <= tx < MAP_SIZE and 0 <= ty < MAP_SIZE:
                    track_map[ty, tx] = 1

for i in range(len(control_points) - 1):
    x0, y0 = control_points[i]
    x1, y1 = control_points[i + 1]
    draw_thick_line(x0, y0, x1, y1, thickness=3)

# Player
player_x = 32.0
player_y = 48.0
player_angle = 0.0
speed = 0.0

def cast_floor():
    screen.fill((0, 0, 0))
    half_h = HEIGHT // 2  # normal camera angle

    for y in range(half_h + 1, HEIGHT):
        ray_dir_x0 = math.cos(player_angle - HALF_FOV)
        ray_dir_y0 = math.sin(player_angle - HALF_FOV)
        ray_dir_x1 = math.cos(player_angle + HALF_FOV)
        ray_dir_y1 = math.sin(player_angle + HALF_FOV)

        p = y - half_h
        pos_z = 0.5 * HEIGHT
        row_distance = pos_z / p

        floor_step_x = row_distance * (ray_dir_x1 - ray_dir_x0) / WIDTH
        floor_step_y = row_distance * (ray_dir_y1 - ray_dir_y0) / WIDTH

        floor_x = player_x + row_distance * ray_dir_x0
        floor_y = player_y + row_distance * ray_dir_y0

        for x in range(WIDTH):
            cell_x = int(floor_x) % MAP_SIZE
            cell_y = int(floor_y) % MAP_SIZE
            tile = track_map[cell_y, cell_x]

            color = ROAD_COLOR if tile == 1 else GRASS_COLOR
            screen.set_at((x, y), color)

            floor_x += floor_step_x
            floor_y += floor_step_y

    # Draw player kart in fixed screen position
    kart_w = 10
    kart_h = 16
    kart_rect = pygame.Rect(WIDTH//2 - kart_w, HEIGHT//2 + 100 - kart_h, kart_w*2, kart_h*2)
    pygame.draw.rect(screen, (255, 0, 0), kart_rect)

def handle_input():
    global player_x, player_y, player_angle, speed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        speed += 0.1
    elif keys[pygame.K_DOWN]:
        speed -= 0.1
    else:
        speed *= 0.95

    if keys[pygame.K_LEFT]:
        player_angle -= 0.05
    if keys[pygame.K_RIGHT]:
        player_angle += 0.05

    dx = math.cos(player_angle) * speed
    dy = math.sin(player_angle) * speed
    player_x += dx
    player_y += dy

    # Clamp inside map
    player_x = max(1, min(MAP_SIZE - 2, player_x))
    player_y = max(1, min(MAP_SIZE - 2, player_y))

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        handle_input()
        cast_floor()
        pygame.display.flip()
        clock.tick(60)

main()
