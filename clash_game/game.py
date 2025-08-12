from __future__ import annotations
import pygame
import random
import os
import time
from typing import Dict, List
from .card import load_cards, Card, CARD_FILE
from .troop import Troop
from .tower import Tower
from .elixir import ElixirBar

WIDTH, HEIGHT = 800, 480
LANE_Y = [HEIGHT * 0.3, HEIGHT * 0.7]

class Game:
    def __init__(self, seed: int = 0):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Mini Royale')
        self.clock = pygame.time.Clock()
        self.running = True
        self.random = random.Random(seed)
        self.cards = load_cards()
        self.card_mtime = os.path.getmtime(CARD_FILE)
        self.player_elixir = ElixirBar()
        self.bot_elixir = ElixirBar()
        self.player_towers = [Tower(100, HEIGHT/2, 1500, 50, 120, 1.0)]
        self.bot_towers = [Tower(WIDTH-100, HEIGHT/2, 1500, 50, 120, 1.0)]
        self.player_troops: List[Troop] = []
        self.bot_troops: List[Troop] = []

    def hot_reload(self):
        mtime = os.path.getmtime(CARD_FILE)
        if mtime != self.card_mtime:
            self.cards = load_cards()
            self.card_mtime = mtime

    def spawn_troop(self, name: str, lane_idx: int, is_player=True):
        card = self.cards[name]
        troop = Troop(
            x=150 if is_player else WIDTH-150,
            y=LANE_Y[lane_idx],
            hp=card.hp,
            damage=card.damage,
            speed=card.speed * (1 if is_player else -1),
            range=card.range,
            attack_speed=card.attack_speed,
            direction=1 if is_player else -1,
        )
        if is_player:
            self.player_troops.append(troop)
        else:
            self.bot_troops.append(troop)

    def bot_logic(self):
        self.bot_elixir.update()
        if self.bot_elixir.spend(3):
            lane = self.random.randint(0, len(LANE_Y)-1)
            self.spawn_troop('knight', lane, is_player=False)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                lane = 0 if event.pos[1] < HEIGHT/2 else 1
                if self.player_elixir.spend(3):
                    self.spawn_troop('knight', lane, is_player=True)

    def update(self):
        self.hot_reload()
        self.player_elixir.update()
        self.bot_logic()
        for troop in self.player_troops:
            troop.update(self.bot_troops, self.bot_towers)
        for troop in self.bot_troops:
            troop.update(self.player_troops, self.player_towers)
        for tower in self.player_towers:
            tower.update(self.bot_troops)
        for tower in self.bot_towers:
            tower.update(self.player_troops)
        self.player_troops = [t for t in self.player_troops if t.hp > 0]
        self.bot_troops = [t for t in self.bot_troops if t.hp > 0]

    def draw(self):
        self.screen.fill((50, 180, 50))
        # Draw lanes
        pygame.draw.line(self.screen, (150, 150, 150), (0, HEIGHT/2), (WIDTH, HEIGHT/2), 2)
        # Draw towers
        for t in self.player_towers + self.bot_towers:
            pygame.draw.rect(self.screen, (100, 100, 255), pygame.Rect(t.x-20, t.y-40, 40, 80))
        # Draw troops
        for troop in self.player_troops:
            pygame.draw.circle(self.screen, (0, 0, 255), (int(troop.x), int(troop.y)), 10)
        for troop in self.bot_troops:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(troop.x), int(troop.y)), 10)
        # Elixir bar
        pygame.draw.rect(self.screen, (30, 30, 30), pygame.Rect(10, HEIGHT-30, 200, 20))
        pygame.draw.rect(self.screen, (120, 0, 255), pygame.Rect(10, HEIGHT-30, 20*self.player_elixir.amount, 20))
        pygame.display.flip()

    def loop(self):
        while self.running:
            self.clock.tick(60)
            self.handle_input()
            self.update()
            self.draw()
        pygame.quit()
