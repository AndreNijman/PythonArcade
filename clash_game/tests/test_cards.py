import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from clash_game.card import load_cards

def test_load_cards():
    cards = load_cards()
    assert 'knight' in cards
    k = cards['knight']
    assert k.elixir == 3
    assert k.damage == 75
