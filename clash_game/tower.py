from __future__ import annotations
from dataclasses import dataclass
from typing import List
import math
import time

@dataclass
class Tower:
    x: float
    y: float
    hp: int
    damage: int
    range: float
    attack_speed: float
    last_attack: float = 0.0

    def update(self, enemies: List['Troop']) -> None:
        now = time.time()
        if now - self.last_attack < self.attack_speed:
            return
        target = self._get_target(enemies)
        if target:
            target.hp -= self.damage
            self.last_attack = now

    def _get_target(self, enemies: List['Troop']):
        in_range = [t for t in enemies if self.distance_to(t) <= self.range]
        if not in_range:
            return None
        return min(in_range, key=lambda t: self.distance_to(t))

    def distance_to(self, troop: 'Troop') -> float:
        return math.hypot(self.x - troop.x, self.y - troop.y)
