from dataclasses import dataclass
import time

ELIXIR_MAX = 10
ELIXIR_TICK = 1.0  # seconds per elixir

@dataclass
class ElixirBar:
    amount: float = 5.0
    last_tick: float = time.time()

    def update(self) -> None:
        now = time.time()
        delta = now - self.last_tick
        gained = int(delta / ELIXIR_TICK)
        if gained > 0:
            self.amount = min(ELIXIR_MAX, self.amount + gained)
            self.last_tick += gained * ELIXIR_TICK

    def spend(self, cost: int) -> bool:
        if self.amount >= cost:
            self.amount -= cost
            return True
        return False
