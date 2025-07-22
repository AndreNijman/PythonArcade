import pygame
import sys
import math
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
SHIP_RADIUS = 10
BULLET_LIFE = 60
ASTEROID_SIZES = {3: 40, 2: 25, 1: 15}

font = pygame.font.SysFont("Courier", 20)

def wrap_position(pos):
    x, y = pos
    return [x % WIDTH, y % HEIGHT]

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

class Bullet:
    def __init__(self, pos, angle):
        self.pos = list(pos)
        self.vel = [math.cos(angle) * 8, math.sin(angle) * 8]
        self.life = BULLET_LIFE

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos = wrap_position(self.pos)
        self.life -= 1

    def draw(self):
        pygame.draw.circle(WIN, WHITE, (int(self.pos[0]), int(self.pos[1])), 2)

class Asteroid:
    def __init__(self, pos, size):
        self.pos = list(pos)
        self.size = size
        speed = random.uniform(1, 3)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = [math.cos(angle) * speed, math.sin(angle) * speed]

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos = wrap_position(self.pos)

    def draw(self):
        radius = ASTEROID_SIZES[self.size]
        points = []
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            r = radius + random.randint(-5, 5)
            x = self.pos[0] + math.cos(angle) * r
            y = self.pos[1] + math.sin(angle) * r
            points.append((x, y))
        pygame.draw.polygon(WIN, WHITE, points, 1)

    def split(self):
        if self.size > 1:
            return [Asteroid(self.pos, self.size - 1), Asteroid(self.pos, self.size - 1)]
        return []

class Ship:
    def __init__(self):
        self.pos = [WIDTH / 2, HEIGHT / 2]
        self.vel = [0, 0]
        self.angle = 0
        self.lives = 3
        self.respawn_timer = 0

    def update(self, keys):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            return

        if keys[pygame.K_LEFT]: self.angle -= 0.07
        if keys[pygame.K_RIGHT]: self.angle += 0.07
        if keys[pygame.K_UP]:
            thrust = [math.cos(self.angle) * 0.2, math.sin(self.angle) * 0.2]
            self.vel[0] += thrust[0]
            self.vel[1] += thrust[1]

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos = wrap_position(self.pos)
        self.vel[0] *= 0.99
        self.vel[1] *= 0.99

    def draw(self):
        if self.respawn_timer > 0 and self.respawn_timer % 10 < 5:
            return
        tip = (self.pos[0] + math.cos(self.angle) * SHIP_RADIUS,
               self.pos[1] + math.sin(self.angle) * SHIP_RADIUS)
        left = (self.pos[0] + math.cos(self.angle + 2.5) * SHIP_RADIUS,
                self.pos[1] + math.sin(self.angle + 2.5) * SHIP_RADIUS)
        right = (self.pos[0] + math.cos(self.angle - 2.5) * SHIP_RADIUS,
                 self.pos[1] + math.sin(self.angle - 2.5) * SHIP_RADIUS)
        pygame.draw.polygon(WIN, WHITE, [tip, left, right], 1)

    def shoot(self):
        if self.respawn_timer == 0:
            return Bullet(self.pos, self.angle)

    def collide(self, asteroid):
        if self.respawn_timer > 0:
            return False
        return distance(self.pos, asteroid.pos) < ASTEROID_SIZES[asteroid.size]

# Game state
ship = Ship()
bullets = []
asteroids = []
score = 0
wave = 1

def draw_hud():
    lives_text = font.render(f"Lives: {ship.lives}", True, WHITE)
    score_text = font.render(f"Score: {score}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    WIN.blit(lives_text, (10, 10))
    WIN.blit(score_text, (WIDTH - 120, 10))
    WIN.blit(wave_text, (WIDTH // 2 - 40, 10))

def spawn_wave():
    global asteroids, wave
    asteroids = [Asteroid([random.randint(0, WIDTH), random.randint(0, HEIGHT)], 3) for _ in range(4 + wave)]

def main():
    global bullets, asteroids, score, wave
    shoot_cooldown = 0
    spawn_wave()

    while True:
        CLOCK.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        WIN.fill((0, 0, 0))

        ship.update(keys)
        ship.draw()

        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            bullet = ship.shoot()
            if bullet:
                bullets.append(bullet)
                shoot_cooldown = 10
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        for b in bullets[:]:
            b.update()
            b.draw()
            if b.life <= 0:
                bullets.remove(b)

        for a in asteroids[:]:
            a.update()
            a.draw()

        # Bullet-Asteroid collisions
        for b in bullets[:]:
            for a in asteroids[:]:
                if distance(b.pos, a.pos) < ASTEROID_SIZES[a.size]:
                    bullets.remove(b)
                    asteroids.remove(a)
                    asteroids.extend(a.split())
                    score += 100 * a.size
                    break

        # Ship-Asteroid collisions
        for a in asteroids:
            if ship.collide(a):
                ship.lives -= 1
                ship.pos = [WIDTH / 2, HEIGHT / 2]
                ship.vel = [0, 0]
                ship.angle = 0
                ship.respawn_timer = 120
                if ship.lives <= 0:
                    text = font.render("GAME OVER", True, WHITE)
                    WIN.blit(text, (WIDTH//2 - 70, HEIGHT//2))
                    pygame.display.update()
                    pygame.time.wait(2000)
                    pygame.quit()
                    sys.exit()
                break

        # New wave if all asteroids gone
        if not asteroids:
            wave += 1
            spawn_wave()

        draw_hud()
        pygame.display.update()

main()
