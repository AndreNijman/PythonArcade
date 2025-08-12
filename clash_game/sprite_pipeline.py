"""Generate simple procedural sprites for the game."""
import os
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
pygame.init()

def generate():
    os.makedirs(ASSET_DIR, exist_ok=True)
    knight = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(knight, (0, 0, 255), (16, 16), 15)
    pygame.image.save(knight, os.path.join(ASSET_DIR, 'knight.png'))

    tower = pygame.Surface((40, 80), pygame.SRCALPHA)
    pygame.draw.rect(tower, (100, 100, 255), (0, 0, 40, 80))
    pygame.image.save(tower, os.path.join(ASSET_DIR, 'tower.png'))

    sheet = pygame.Surface((72, 80), pygame.SRCALPHA)
    sheet.blit(knight, (0, 24))
    sheet.blit(tower, (32, 0))
    pygame.image.save(sheet, os.path.join(ASSET_DIR, 'spritesheet.png'))
    pygame.quit()


if __name__ == '__main__':
    generate()
