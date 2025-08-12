from .game import Game


def main():
    game = Game(seed=0)
    game.loop()


if __name__ == '__main__':
    main()
