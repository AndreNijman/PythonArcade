import pygame
import sys
import random

# Init
pygame.init()

# Constants
CELL_SIZE = 24
COLS = 10
ROWS = 20
WIDTH = COLS * CELL_SIZE
INFO_WIDTH = 150
HEIGHT = ROWS * CELL_SIZE
WINDOW_WIDTH = WIDTH + INFO_WIDTH
FPS = 60

# Colors
BG_COLOR = (15, 56, 15)
GRID_COLOR = (34, 139, 34)
TEXT_COLOR = (255, 255, 255)
DROP_SHADOW = (100, 100, 100)

# Tetromino colors
SHAPE_COLORS = {
    'I': (106, 190, 48),
    'O': (255, 216, 0),
    'T': (208, 70, 72),
    'S': (0, 168, 243),
    'Z': (255, 110, 64),
    'J': (168, 0, 32),
    'L': (191, 91, 0)
}

# Tetromino shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}


class Tetromino:
    def __init__(self, shape):
        self.shape = shape
        self.blocks = SHAPES[shape]
        self.color = SHAPE_COLORS[shape]
        self.x = COLS // 2 - len(self.blocks[0]) // 2
        self.y = 0

    def rotate(self):
        self.blocks = [list(row) for row in zip(*self.blocks[::-1])]

    def get_cells(self, offset_x=0, offset_y=0):
        return [(self.x + j + offset_x, self.y + i + offset_y)
                for i, row in enumerate(self.blocks)
                for j, val in enumerate(row) if val]


def create_grid(locked_positions):
    grid = [[BG_COLOR for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= x < COLS and 0 <= y < ROWS:
            grid[y][x] = color
    return grid


def valid_space(shape, grid):
    for x, y in shape.get_cells():
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] != BG_COLOR:
            return False
    return True


def hard_drop_y(shape, grid):
    while valid_space(shape, grid):
        shape.y += 1
    shape.y -= 1
    return shape.y


def clear_rows(grid, locked):
    rows_to_clear = [i for i in range(ROWS) if all(grid[i][x] != BG_COLOR for x in range(COLS))]
    for i in rows_to_clear:
        for x in range(COLS):
            locked.pop((x, i), None)
    for i in sorted(rows_to_clear):
        for y in range(i - 1, -1, -1):
            for x in range(COLS):
                if (x, y) in locked:
                    locked[(x, y + 1)] = locked.pop((x, y))
    return len(rows_to_clear)


def draw_grid(win, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(win, grid[y][x],
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for x in range(COLS):
        pygame.draw.line(win, GRID_COLOR, (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(win, GRID_COLOR, (0, y * CELL_SIZE), (WIDTH, y * CELL_SIZE))


def draw_info(win, font, score, lines, level, next_piece):
    pygame.draw.rect(win, BG_COLOR, (WIDTH, 0, INFO_WIDTH, HEIGHT))
    win.blit(font.render(f"Score: {score}", True, TEXT_COLOR), (WIDTH + 10, 20))
    win.blit(font.render(f"Lines: {lines}", True, TEXT_COLOR), (WIDTH + 10, 50))
    win.blit(font.render(f"Level: {level}", True, TEXT_COLOR), (WIDTH + 10, 80))
    win.blit(font.render("Next:", True, TEXT_COLOR), (WIDTH + 10, 120))
    for i, row in enumerate(next_piece.blocks):
        for j, val in enumerate(row):
            if val:
                pygame.draw.rect(
                    win, next_piece.color,
                    (WIDTH + 10 + j * CELL_SIZE, 150 + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                )


def draw_shadow(win, piece, grid):
    shadow = Tetromino(piece.shape)
    shadow.blocks = [row[:] for row in piece.blocks]
    shadow.x = piece.x
    shadow.y = piece.y

    # Temporarily remove current piece from grid to allow proper shadow drop
    temp_grid = [row[:] for row in grid]
    for x, y in piece.get_cells():
        if 0 <= x < COLS and 0 <= y < ROWS:
            temp_grid[y][x] = BG_COLOR

    while valid_space(shadow, temp_grid):
        shadow.y += 1
    shadow.y -= 1

    for x, y in shadow.get_cells():
        if y >= 0:
            pygame.draw.rect(win, DROP_SHADOW,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))




def main():
    win = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris (GBC Style)")
    font = pygame.font.SysFont("Arial", 18)
    clock = pygame.time.Clock()

    locked_positions = {}
    current_piece = Tetromino(random.choice(list(SHAPES.keys())))
    next_piece = Tetromino(random.choice(list(SHAPES.keys())))
    fall_speed = 500
    last_drop = pygame.time.get_ticks()
    score = 0
    lines_cleared = 0
    level = 1
    rotate_cooldown = 200
    move_cooldown = 50
    last_rotate = 0
    last_move = 0

    running = True
    while running:
        grid = create_grid(locked_positions)
        time_now = pygame.time.get_ticks()

        if time_now - last_drop > fall_speed:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                for x, y in current_piece.get_cells():
                    locked_positions[(x, y)] = current_piece.color
                current_piece = next_piece
                next_piece = Tetromino(random.choice(list(SHAPES.keys())))
                if not valid_space(current_piece, grid):
                    running = False
            last_drop = time_now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    for x, y in current_piece.get_cells():
                        locked_positions[(x, y)] = current_piece.color
                    current_piece = next_piece
                    next_piece = Tetromino(random.choice(list(SHAPES.keys())))
                    if not valid_space(current_piece, grid):
                        running = False
                    last_drop = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and time_now - last_move > move_cooldown:
            current_piece.x -= 1
            if not valid_space(current_piece, grid):
                current_piece.x += 1
            last_move = time_now
        if keys[pygame.K_RIGHT] and time_now - last_move > move_cooldown:
            current_piece.x += 1
            if not valid_space(current_piece, grid):
                current_piece.x -= 1
            last_move = time_now
        if keys[pygame.K_DOWN]:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
        if keys[pygame.K_UP] and time_now - last_rotate > rotate_cooldown:
            current_piece.rotate()
            if not valid_space(current_piece, grid):
                for _ in range(3):
                    current_piece.rotate()
            last_rotate = time_now

        for x, y in current_piece.get_cells():
            if y >= 0:
                grid[y][x] = current_piece.color

        cleared = clear_rows(grid, locked_positions)
        if cleared:
            lines_cleared += cleared
            score += cleared * 100
            if lines_cleared // 10 + 1 > level:
                level += 1
                fall_speed = max(100, 500 - (level - 1) * 40)

        win.fill(BG_COLOR)
        draw_grid(win, grid)
        draw_info(win, font, score, lines_cleared, level, next_piece)
        draw_shadow(win, current_piece, grid)
        pygame.display.update()
        clock.tick(FPS)


main()
