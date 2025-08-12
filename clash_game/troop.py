from __future__ import annotations
from dataclasses import dataclass
from typing import List
import math
import time

@dataclass
class Troop:
    x: float
    y: float
    hp: int
    damage: int
    speed: float
    range: float
    attack_speed: float
    last_attack: float = 0.0
    direction: int = 1  # 1 for right, -1 for left

    def update(self, enemies: List['Troop'], towers: List['Tower']) -> None:
        if self.hp <= 0:
            return
        target = self._target(enemies, towers)
        if target and self._in_range(target):
            self._attack(target)
        else:
            self.x += self.speed * self.direction

    def _attack(self, target) -> None:
        now = time.time()
        if now - self.last_attack < self.attack_speed:
            return
        target.hp -= self.damage
        self.last_attack = now

    def _target(self, enemies: List['Troop'], towers: List['Tower']):
        candidates = [t for t in enemies if t.hp > 0]
        candidates += [t for t in towers if t.hp > 0]
        if not candidates:
            return None
        return min(candidates, key=lambda t: self.distance_to(t))

    def _in_range(self, target) -> bool:
        return self.distance_to(target) <= self.range

    def distance_to(self, other) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)
