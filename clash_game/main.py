"""Entry point for running the demo game.

The script supports two invocation styles:

* ``python -m clash_game.main`` (package execution)
* ``python clash_game/main.py`` (direct script execution)
"""

if __package__ in (None, ""):
    # When executed directly, ensure the package root is on ``sys.path``
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from clash_game.game import Game
else:  # pragma: no cover
    from .game import Game


def main():
    game = Game(seed=0)
    game.loop()


if __name__ == '__main__':
    main()
