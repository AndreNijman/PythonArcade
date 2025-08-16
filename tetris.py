import pygame, sys, random, math, time

# ---------- Init ----------
pygame.init()
pygame.display.set_caption("Tetris — Neon FX (7-Bag, Timer, Left Controls)")
FPS = 60
clock = pygame.time.Clock()

# ---------- Sizes ----------
CELL = 28
COLS, ROWS = 10, 20
W, H = COLS * CELL, ROWS * CELL

LEFT_INFO_W  = 210
RIGHT_INFO_W = 190
WIN_W, WIN_H = LEFT_INFO_W + W + RIGHT_INFO_W, H
screen = pygame.display.set_mode((WIN_W, WIN_H))

# ---------- Tunables ----------
BASE_FALL_MS = 520
LEVEL_STEP = 40
MIN_FALL_MS = 90

MOVE_COOLDOWN = 110
ROT_COOLDOWN  = 230

SHOW_CRT = False
CRT_SCANLINE_ALPHA = 8
CRT_VIGNETTE_STRENGTH = 60

BLOCK_GLOW = 160
BLOCK_OUTLINE_A = 230
SHADOW_ALPHA = 90
SHADOW_BORDER_A = 180
GRID_ALPHA_X = 40
GRID_ALPHA_Y = 30

# ---------- Colors ----------
WHITE = (245, 250, 255)
UI_MUTED = (170, 190, 210)
GLOW = (60, 150, 255)
BG_TOP = (8, 12, 26)
BG_BOT = (12, 8, 30)

SHAPE_COLORS = {
    'I': (0, 220, 255),
    'O': (255, 220, 0),
    'T': (200, 90, 255),
    'S': (0, 235, 150),
    'Z': (255, 80, 120),
    'J': (80, 140, 255),
    'L': (255, 160, 60),
}
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

# ---------- Helpers ----------
def make_gradient(w, h, top, bot):
    s = pygame.Surface((w, h)).convert()
    for y in range(h):
        t = y / max(1, h-1)
        col = (int(top[0]*(1-t)+bot[0]*t), int(top[1]*(1-t)+bot[1]*t), int(top[2]*(1-t)+bot[2]*t))
        pygame.draw.line(s, col, (0, y), (w, y))
    return s

def rounded_rect(surf, color, rect, r=6, width=0):
    pygame.draw.rect(surf, color, rect, width=width, border_radius=r)

def add_glow(surf, px, py, w, h, col, radius=9, alpha=95):
    glow = pygame.Surface((w + radius*2, h + radius*2), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*col, alpha), (radius-2, radius-2, w+4, h+4), border_radius=10)
    surf.blit(glow, (px - radius, py - radius), special_flags=pygame.BLEND_ADD)

def outline_rect(surf, color, rect, r=6, a=120, width=2):
    pygame.draw.rect(surf, (*color, a), rect, width=width, border_radius=r)

# ---------- Hi-quality block sprites ----------
BLOCK_CACHE = {}
GHOST_CACHE = {}
def lighten(c, amt): return (min(255, c[0]+amt), min(255, c[1]+amt), min(255, c[2]+amt))

def make_block_sprite(color):
    if color in BLOCK_CACHE: return BLOCK_CACHE[color]
    hr = CELL * 3
    s = pygame.Surface((hr, hr), pygame.SRCALPHA)
    r = int(hr*0.22)
    core = (color[0], color[1], color[2])
    pygame.draw.rect(s, core, (int(hr*.07), int(hr*.07), int(hr*.86), int(hr*.86)), border_radius=r)
    for i in range(1, 6):
        pad = int(hr*(0.07 + i*0.01)); a = 50 - i*7
        col = (*lighten(color, 40), max(0, a))
        pygame.draw.rect(s, col, (pad, pad, hr-2*pad, hr-2*pad), border_radius=r)
    pygame.draw.rect(s, (*lighten(color, 20), 220),
                     (int(hr*.06), int(hr*.06), int(hr*.88), int(hr*.88)),
                     width=int(hr*.05), border_radius=r)
    scaled = pygame.transform.smoothscale(s, (CELL-4, CELL-4))
    BLOCK_CACHE[color] = scaled
    return scaled

def make_ghost_sprite(color):
    if color in GHOST_CACHE: return GHOST_CACHE[color]
    spr = make_block_sprite(color).copy()
    body = pygame.Surface(spr.get_size(), pygame.SRCALPHA)
    body.fill((*color, SHADOW_ALPHA))
    spr.blit(body, (0, 0))
    pygame.draw.rect(spr, (*color, SHADOW_BORDER_A), (0, 0, spr.get_width(), spr.get_height()), width=2, border_radius=8)
    GHOST_CACHE[color] = spr
    return spr

# ---------- Tetromino ----------
class Tetromino:
    def __init__(self, k):
        self.k = k
        self.blocks = [row[:] for row in SHAPES[k]]
        self.color = SHAPE_COLORS[k]
        self.x = COLS // 2 - len(self.blocks[0]) // 2
        self.y = -2
    def rotated(self): return [list(r) for r in zip(*self.blocks[::-1])]
    def cells(self, ox=0, oy=0, blocks=None):
        b = blocks if blocks is not None else self.blocks
        for i, row in enumerate(b):
            for j, v in enumerate(row):
                if v: yield (self.x + j + ox, self.y + i + oy)

# ---------- Board ----------
def create_grid(locked):
    g = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), col in locked.items():
        if 0 <= x < COLS and 0 <= y < ROWS: g[y][x] = col
    return g

def valid(piece, grid, ox=0, oy=0, blocks=None):
    for x, y in piece.cells(ox, oy, blocks):
        if x < 0 or x >= COLS or y >= ROWS: return False
        if y >= 0 and grid[y][x] is not None: return False
    return True

def lock_piece(piece, locked):
    for x, y in piece.cells(): locked[(x, y)] = piece.color

def find_full_rows(grid): return [i for i in range(ROWS) if all(grid[i][x] is not None for x in range(COLS))]

def clear_rows(locked, rows):
    if not rows: return
    rows = sorted(rows)
    for r in rows:
        for x in range(COLS): locked.pop((x, r), None)
    for r in rows:
        for y in range(r-1, -1, -1):
            for x in range(COLS):
                if (x, y) in locked: locked[(x, y+1)] = locked.pop((x, y))

# ---------- FX ----------
class Particle:
    def __init__(self, x, y, color):
        ang = random.uniform(-math.pi, math.pi); spd = random.uniform(80, 260)
        self.vx = math.cos(ang)*spd; self.vy = math.sin(ang)*spd - 80
        self.x = x; self.y = y; self.life = random.uniform(0.35, 0.7)
        self.color = color; self.size = random.randint(2, 4); self.age = 0.0
    def update(self, dt): self.age += dt; self.x += self.vx*dt; self.y += self.vy*dt; self.vy += 420*dt
    def dead(self): return self.age >= self.life
    def draw(self, s):
        t = max(0.0, 1.0 - self.age/self.life); a = int(180*t); sz = int(self.size*(0.7+0.6*t))
        pygame.draw.rect(s, (*self.color, a), (int(self.x)-sz//2, int(self.y)-sz//2, sz, sz), border_radius=3)

class FX:
    def __init__(self): self.p = []; self.wave = None; self.shake_t = 0.0
    def burst(self, cx, cy, color, n=28): self.p += [Particle(cx, cy, color) for _ in range(n)]
    def start_wave(self, rows): 
        if rows: self.wave = {"rows": rows[:], "t": 0.0, "dur": 0.35}
    def add_shake(self, amt=0.3): self.shake_t = min(0.5, self.shake_t + amt)
    def update(self, dt):
        self.p = [x for x in self.p if not x.dead()]
        for x in self.p: x.update(dt)
        if self.wave:
            self.wave["t"] += dt
            if self.wave["t"] >= self.wave["dur"]: self.wave = None
        if self.shake_t > 0: self.shake_t = max(0, self.shake_t - dt*1.7)
    def shake_off(self):
        if self.shake_t <= 0: return 0, 0
        mag = 6 * (self.shake_t ** 0.7)
        return random.randint(-int(mag), int(mag)), random.randint(-int(mag), int(mag))
    def draw_wave(self, surf):
        if not self.wave: return
        t = self.wave["t"]/self.wave["dur"]; w = int(W*(0.2+1.4*t)); a = int(160*(1-t)); x0 = (W-w)//2
        for r in self.wave["rows"]:
            y = r * CELL; overlay = pygame.Surface((w, CELL), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255,255,255,a), (0,0,w,CELL), border_radius=8)
            surf.blit(overlay, (x0,y), special_flags=pygame.BLEND_ADD)

fx = FX()

# ---------- UI ----------
bg_grad = make_gradient(WIN_W, WIN_H, BG_TOP, BG_BOT)
def scanlines(w, h, gap=3, alpha=CRT_SCANLINE_ALPHA):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, gap): pygame.draw.line(s, (255,255,255,alpha), (0,y), (w,y))
    return s
scan = scanlines(WIN_W, WIN_H)
def vignette(w, h, strength=CRT_VIGNETTE_STRENGTH):
    v = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w/2, h/2; maxd = math.hypot(cx, cy); step = 3
    for y in range(0,h,step):
        for x in range(0,w,step):
            d = math.hypot(x-cx, y-cy)/maxd; a = int(strength*max(0, d-0.38))
            if a: pygame.draw.rect(v, (0,0,0,a), (x,y,step,step))
    return v
vign = vignette(WIN_W, WIN_H)

# ---------- Fonts ----------
ui_font = pygame.font.SysFont("arial", 18)
big_font = pygame.font.SysFont("arial", 28)

# ---------- Draw helpers ----------
def draw_grid_bg(surf, ms):
    t = ms * 0.0015
    g = pygame.Surface((W, H), pygame.SRCALPHA)
    for x in range(COLS+1):
        a = int(GRID_ALPHA_X*(0.5+0.5*math.sin(t + x*0.6)))
        pygame.draw.line(g, (GLOW[0],GLOW[1],GLOW[2], a), (x*CELL,0), (x*CELL,H), 1)
    for y in range(ROWS+1):
        a = int(GRID_ALPHA_Y*(0.5+0.5*math.sin(t*1.2 + y*0.55)))
        pygame.draw.line(g, (GLOW[0],GLOW[1],GLOW[2], a), (0,y*CELL), (W,y*CELL), 1)
    surf.blit(g, (0,0), special_flags=pygame.BLEND_ADD)

def draw_block(surf, x, y, color, pulse=1.0):
    px, py = x*CELL, y*CELL
    core_col = (min(255, color[0]+10), min(255, color[1]+10), min(255, color[2]+10))
    rounded_rect(surf, core_col, (px+2, py+2, CELL-4, CELL-4), r=8)
    add_glow(surf, px, py, CELL, CELL, color, radius=10, alpha=int(BLOCK_GLOW*pulse))
    surf.blit(make_block_sprite(color), (px+2, py+2))
    outline_rect(surf, color, (px+1, py+1, CELL-2, CELL-2), r=8, a=BLOCK_OUTLINE_A, width=3)

def draw_shadow_piece(s, piece, grid):
    ghost = Tetromino(piece.k); ghost.blocks = [r[:] for r in piece.blocks]
    ghost.x, ghost.y = piece.x, piece.y
    while valid(ghost, grid, oy=1): ghost.y += 1
    gs = make_ghost_sprite(piece.color)
    for x, y in ghost.cells():
        if y < 0: continue
        s.blit(gs, (x*CELL+2, y*CELL+2))

def draw_next(panel, piece, ms):
    panel.fill((0,0,0,0))
    panel.blit(ui_font.render("NEXT", True, WHITE), (14,8))
    ox, oy = 22, 38
    wave = 0.7 + 0.3 * math.sin(ms * 0.004)
    for i, row in enumerate(piece.blocks):
        for j, v in enumerate(row):
            if not v: continue
            px, py = ox + j*(CELL-6), oy + i*(CELL-6)
            add_glow(panel, px, py, CELL-8, CELL-8, piece.color, alpha=int(130*wave))
            spr = pygame.transform.smoothscale(make_block_sprite(piece.color), (CELL-8, CELL-8))
            panel.blit(spr, (px, py))

def draw_right_panel(surf, score, lines, level, nxt, ms, elapsed_s):
    x0 = LEFT_INFO_W + W
    panel = pygame.Surface((RIGHT_INFO_W, H), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10,20,35,200), (10,10,RIGHT_INFO_W-20,H-20), border_radius=14)
    pygame.draw.rect(panel, (80,160,255,60), (10,10,RIGHT_INFO_W-20,H-20), width=2, border_radius=14)

    # Time
    mm = int(elapsed_s // 60)
    ss = int(elapsed_s % 60)
    tstr = f"{mm:02d}:{ss:02d}"
    panel.blit(ui_font.render("TIME", True, UI_MUTED), (22, 16))
    panel.blit(big_font.render(tstr, True, WHITE), (22, 36))

    # Score / Lines / Level
    panel.blit(ui_font.render("SCORE", True, UI_MUTED), (22, 86))
    panel.blit(ui_font.render(str(score), True, WHITE), (22, 108))
    panel.blit(ui_font.render("LINES", True, UI_MUTED), (22, 140))
    panel.blit(ui_font.render(str(lines), True, WHITE), (22, 162))
    panel.blit(ui_font.render("LEVEL", True, UI_MUTED), (22, 194))
    panel.blit(ui_font.render(str(level), True, WHITE), (22, 216))

    # Next
    next_card = pygame.Surface((RIGHT_INFO_W-40, 120), pygame.SRCALPHA)
    pygame.draw.rect(next_card, (18,30,55,180), (0,0,RIGHT_INFO_W-40,120), border_radius=12)
    pygame.draw.rect(next_card, (80,160,255,70), (0,0,RIGHT_INFO_W-40,120), width=2, border_radius=12)
    draw_next(next_card, nxt, ms)
    panel.blit(next_card, (20, 260))

    # Pulse
    t = 0.5 + 0.5 * math.sin(ms * 0.004)
    pulse_w = int((RIGHT_INFO_W - 40) * (0.2 + 0.8 * t))
    glow = pygame.Surface((pulse_w, 4), pygame.SRCALPHA)
    pygame.draw.rect(glow, (120,200,255,140), (0,0,pulse_w,4), border_radius=2)
    panel.blit(glow, (20, 240), special_flags=pygame.BLEND_ADD)

    surf.blit(panel, (x0, 0))

def draw_left_controls(surf):
    panel = pygame.Surface((LEFT_INFO_W, H), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10,20,35,200), (10,10,LEFT_INFO_W-20,H-20), border_radius=14)
    pygame.draw.rect(panel, (80,160,255,60), (10,10,LEFT_INFO_W-20,H-20), width=2, border_radius=14)

    title = big_font.render("CONTROLS", True, WHITE)
    panel.blit(title, (16, 16))

    lines = [
        ("← / →", "Move"),
        ("↓", "Soft drop"),
        ("↑", "Rotate"),
        ("SPACE", "Hard drop"),
        ("R", "Restart"),
        ("ESC", "Quit"),
    ]
    y = 60
    for k, desc in lines:
        panel.blit(ui_font.render(k, True, WHITE), (16, y))
        panel.blit(ui_font.render(desc, True, UI_MUTED), (110, y))
        y += 26

    surf.blit(panel, (0, 0))

# ---------- 7-Bag Generator ----------
def new_bag():
    bag = list(SHAPES.keys())
    random.shuffle(bag)
    return bag

class PieceQueue:
    def __init__(self):
        self.bag = new_bag()
    def next_piece_key(self):
        if not self.bag:
            self.bag = new_bag()
        return self.bag.pop()
    def peek_next_key(self):
        if not self.bag:
            self.bag = new_bag()
        return self.bag[-1]

# ---------- Game ----------
def main():
    locked = {}
    queue = PieceQueue()

    current = Tetromino(queue.next_piece_key())
    nxt = Tetromino(queue.next_piece_key())

    score = 0
    lines = 0
    level = 1
    fall_ms = BASE_FALL_MS

    last_drop = pygame.time.get_ticks()
    last_move = 0
    last_rot = 0

    clearing_rows = []
    clear_t = 0.0
    clear_dur = 0.28

    start_time = time.time()

    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        now = pygame.time.get_ticks()
        elapsed_s = time.time() - start_time

        grid = create_grid(locked)

        # dynamic difficulty: lines and time both push level up
        level_target = 1 + (lines // 10) + int(elapsed_s // 60)
        if level_target > level:
            level = level_target
            fall_ms = max(MIN_FALL_MS, BASE_FALL_MS - (level - 1) * LEVEL_STEP)

        # gravity
        if now - last_drop >= fall_ms:
            if valid(current, grid, oy=1): current.y += 1
            else:
                lock_piece(current, locked)
                for x, y in current.cells():
                    fx.burst(x*CELL+CELL//2, y*CELL+CELL//2, current.color, n=6)
                current = nxt
                nxt = Tetromino(queue.next_piece_key())
                grid = create_grid(locked)
                if not valid(current, grid): running = False
                rows = find_full_rows(grid)
                if rows: clearing_rows = rows[:]; clear_t = 0.0; fx.start_wave(rows)
            last_drop = now

        # events
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                while valid(current, grid, oy=1): current.y += 1
                lock_piece(current, locked)
                for x, y in current.cells():
                    fx.burst(x*CELL+CELL//2, y*CELL+CELL//2, current.color, n=8)
                current = nxt
                nxt = Tetromino(queue.next_piece_key())
                grid = create_grid(locked)
                if not valid(current, grid): running = False
                last_drop = pygame.time.get_ticks()
                rows = find_full_rows(grid)
                if rows: clearing_rows = rows[:]; clear_t = 0.0; fx.start_wave(rows)

        # held keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and now - last_move > MOVE_COOLDOWN:
            if valid(current, grid, ox=-1): current.x -= 1; last_move = now
        if keys[pygame.K_RIGHT] and now - last_move > MOVE_COOLDOWN:
            if valid(current, grid, ox=1): current.x += 1; last_move = now
        if keys[pygame.K_DOWN]:
            if valid(current, grid, oy=1): current.y += 1
        if keys[pygame.K_UP] and now - last_rot > ROT_COOLDOWN:
            rb = current.rotated()
            for dx in (0, -1, 1, -2, 2):
                if valid(current, grid, ox=dx, blocks=rb):
                    current.blocks = rb; current.x += dx; break
            last_rot = now

        # line clear timing
        if clearing_rows:
            clear_t += dt
            if clear_t >= clear_dur:
                clear_rows(locked, clearing_rows)
                n = len(clearing_rows)
                score += n*120 + (n-1)*80
                lines += n
                if n >= 4: fx.add_shake(0.5)
                clearing_rows = []

        # FX
        fx.update(dt)

        # dgrid with current
        dgrid = [row[:] for row in grid]
        for x, y in current.cells():
            if 0 <= y < ROWS: dgrid[y][x] = current.color

        # ---------- Draw ----------
        screen.blit(bg_grad, (0,0))

        # left controls
        draw_left_controls(screen)

        # playfield
        play = pygame.Surface((W, H), pygame.SRCALPHA)
        add_glow(play, 0, 0, W, H, (80,150,255), radius=28, alpha=38)
        draw_grid_bg(play, now)
        draw_shadow_piece(play, current, grid)

        pulse = 0.9 + 0.1 * math.sin(now * 0.006)
        for y in range(ROWS):
            for x in range(COLS):
                col = dgrid[y][x]
                if col is None: continue
                draw_block(play, x, y, col, pulse=pulse)

        fx.draw_wave(play)
        for p in fx.p: p.draw(play)

        pygame.draw.rect(play, (120,200,255,70), (0,0,W,H), width=3, border_radius=12)

        ox, oy = fx.shake_off()
        screen.blit(play, (LEFT_INFO_W + ox, 0 + oy))

        # right stats + timer + next
        draw_right_panel(screen, score, lines, level, Tetromino(nxt.k), now, elapsed_s)

        if SHOW_CRT:
            screen.blit(vign, (0,0))
            screen.blit(scan, (0,0))

        pygame.display.flip()

    # game over
    over = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    pygame.draw.rect(over, (0,0,0,150), (0,0,WIN_W,WIN_H))
    msg = big_font.render("GAME OVER", True, WHITE)
    sub = ui_font.render("ESC quit, R restart", True, UI_MUTED)
    over.blit(msg, (WIN_W//2 - msg.get_width()//2, WIN_H//2 - 30))
    over.blit(sub, (WIN_W//2 - sub.get_width()//2, WIN_H//2 + 4))
    screen.blit(over, (0,0)); pygame.display.flip()
    wait_restart()

def wait_restart():
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if e.key == pygame.K_r: main()
        clock.tick(60)

if __name__ == "__main__":
    main()
