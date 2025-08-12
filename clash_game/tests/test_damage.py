import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from clash_game.tower import Tower
from clash_game.troop import Troop


def test_tower_damage():
    tower = Tower(x=0, y=0, hp=1000, damage=50, range=100, attack_speed=0.5)
    troop = Troop(x=50, y=0, hp=200, damage=0, speed=0, range=0, attack_speed=1.0)
    tower.last_attack = 0.0
    tower.update([troop])
    assert troop.hp == 150
