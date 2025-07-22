import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

rock = pygame.image.load("C:\\Users\\andre\\Documents\\PythonArcade\\Sprites\\RockPaperScissors\\OIP-1952925797.jpg").convert()
scissors = pygame.image.load("C:\\Users\\andre\\Documents\\PythonArcade\\Sprites\\RockPaperScissors\\OIP-2118329776.jpg").convert()
paper = pygame.image.load("C:\\Users\\andre\\Documents\\PythonArcade\\Sprites\\RockPaperScissors\\old-paper-texture-for-the-design-natural-background-toned-abstract-old-brown-paper-as-vintage-wallpaper-backdrop-ai-generated-free-photo-2125980535.jpg").convert()

running = True
while running:
    WIN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Paddle movement
    keys = pygame.key.get_pressed()
    WIN.blit(rock, (100, 100))
    WIN.blit(scissors, (300, 100))
    WIN.blit(paper, (500, 100))
    if keys[pygame.K_LEFT]:
        rock = pygame.transform.rotate(rock, 5)
        
    pygame.display.flip()
    CLOCK.tick(60)
