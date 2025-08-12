from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import json
import os

CARD_FILE = os.path.join(os.path.dirname(__file__), 'config', 'cards.json')

@dataclass
class Card:
    name: str
    elixir: int
    hp: int
    damage: int
    range: float
    speed: float
    attack_speed: float
    splash: bool = False
    targets: str = 'ground'
    type: str = 'troop'

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Card':
        return Card(
            name=data['name'],
            elixir=data['elixir'],
            hp=data['hp'],
            damage=data['damage'],
            range=data['range'],
            speed=data['speed'],
            attack_speed=data['attack_speed'],
            splash=data.get('splash', False),
            targets=data.get('targets', 'ground'),
            type=data.get('type', 'troop'),
        )


def load_cards() -> Dict[str, Card]:
    with open(CARD_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    return {name: Card.from_dict({**{'name': name}, **data}) for name, data in raw.items()}
