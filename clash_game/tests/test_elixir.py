import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from clash_game.elixir import ElixirBar


def test_elixir_gain_and_spend():
    bar = ElixirBar(amount=0, last_tick=time.time() - 3)
    bar.update()
    assert bar.amount >= 3
    assert bar.spend(2) is True
    assert bar.amount == 1
    assert bar.spend(10) is False
