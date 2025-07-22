import pygame
import sys
import random
import os

pygame.init()
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors")

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
DARK_GRAY = (40, 40, 40)

FONT = pygame.font.SysFont("segoeui", 48)
SMALL = pygame.font.SysFont("segoeui", 28)
TINY = pygame.font.SysFont("segoeui", 22)

base_path = os.path.join("Sprites", "RockPaperScissors")
rock = pygame.image.load(os.path.join(base_path, "OIP-1952925797.jpg"))
scissors = pygame.image.load(os.path.join(base_path, "OIP-2118329776.jpg"))
paper = pygame.image.load(os.path.join(base_path, "old-paper-texture-for-the-design-natural-background-toned-abstract-old-brown-paper-as-vintage-wallpaper-backdrop-ai-generated-free-photo-2125980535.jpg"))
question = pygame.image.load(os.path.join(base_path, "question-mark-1829459_1280-3611531784.png")).convert_alpha()

rock = pygame.transform.scale(rock, (120, 120))
paper = pygame.transform.scale(paper, (120, 120))
scissors = pygame.transform.scale(scissors, (120, 120))
question = pygame.transform.smoothscale(question, (120, 120))

clock = pygame.time.Clock()

choices = ["rock", "paper", "scissors"]
images = {"rock": rock, "paper": paper, "scissors": scissors}
positions = {"rock": (90, 650), "paper": (240, 650), "scissors": (390, 650)}

result_text = ""
player_choice = None
computer_choice = None
submitted = False

wins = 0
losses = 0
draws = 0

def draw_button(rect, text, active, hover):
    color = BLUE if active else GRAY
    if hover and active:
        color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
    pygame.draw.rect(WIN, color, rect, border_radius=8)
    label = SMALL.render(text, True, WHITE if active else DARK_GRAY)
    WIN.blit(label, (
        rect.x + (rect.width - label.get_width()) // 2,
        rect.y + (rect.height - label.get_height()) // 2
    ))

def draw_ui(mouse_pos):
    WIN.fill(BLACK)

    # Score display
    score_text = SMALL.render(f"Wins: {wins}   Losses: {losses}   Draws: {draws}", True, WHITE)
    WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 30))

    # Labels and VS
    WIN.blit(TINY.render("Player:", True, WHITE), (130, 300))
    WIN.blit(TINY.render("Computer:", True, WHITE), (360, 300))
    WIN.blit(FONT.render("VS", True, WHITE), (WIDTH // 2 - 30, 330))

    # Player & Computer
    if player_choice:
        WIN.blit(images[player_choice], (100, 340))
    if submitted:
        WIN.blit(images[computer_choice], (360, 340))
    elif player_choice:
        WIN.blit(question, (360, 340))

    # Result text
    if submitted:
        txt = FONT.render(result_text, True, GREEN if "Win" in result_text else RED if "Lose" in result_text else WHITE)
        WIN.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 210))

    # Choices
    for choice in choices:
        cx, cy = positions[choice]
        WIN.blit(images[choice], (cx, cy))
        if choice == player_choice:
            pygame.draw.rect(WIN, BLUE, (cx - 5, cy - 5, 130, 130), 4, border_radius=6)

    # Button
    submit_rect = pygame.Rect(200, 560, 200, 50)
    draw_button(submit_rect, "Submit" if not submitted else "Try Again", player_choice is not None, submit_rect.collidepoint(mouse_pos))

    return submit_rect

def determine_winner(player, cpu):
    if player == cpu:
        return "Draw"
    if (player == "rock" and cpu == "scissors") or \
       (player == "paper" and cpu == "rock") or \
       (player == "scissors" and cpu == "paper"):
        return "You Win"
    return "You Lose"

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    submit_rect = draw_ui(mouse_pos)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            for choice in choices:
                cx, cy = positions[choice]
                if cx < x < cx + 120 and cy < y < cy + 120 and not submitted:
                    player_choice = choice

            if submit_rect.collidepoint((x, y)) and player_choice:
                if not submitted:
                    computer_choice = random.choice(choices)
                    result_text = determine_winner(player_choice, computer_choice)
                    if result_text == "You Win":
                        wins += 1
                    elif result_text == "You Lose":
                        losses += 1
                    else:
                        draws += 1
                    submitted = True
                else:
                    player_choice = None
                    computer_choice = None
                    result_text = ""
                    submitted = False

    clock.tick(60)

pygame.quit()
sys.exit()
