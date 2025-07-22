import pygame
import sys
import random
import os
import math

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

choices = ["rock", "paper", "scissors"]
images = {"rock": rock, "paper": paper, "scissors": scissors}
positions = {"rock": (90, 650), "paper": (240, 650), "scissors": (390, 650)}

player_choice = None
computer_choice = None
result_text = ""
submitted = False
wins = 0
losses = 0
draws = 0

# Animation states
fade_alpha = 0
slide_x = 600
selected_scale = 1.0
highlight_alpha = 0
score_bump = 1.0
idle_phase = 0

clock = pygame.time.Clock()

def determine_winner(player, cpu):
    if player == cpu:
        return "Draw"
    if (player == "rock" and cpu == "scissors") or \
       (player == "paper" and cpu == "rock") or \
       (player == "scissors" and cpu == "paper"):
        return "You Win"
    return "You Lose"

def draw_button(rect, text, active, hover):
    color = BLUE if active else GRAY
    if hover and active:
        color = tuple(min(c + 40, 255) for c in color)
    pygame.draw.rect(WIN, color, rect, border_radius=8)
    label = SMALL.render(text, True, WHITE if active else DARK_GRAY)
    WIN.blit(label, (
        rect.x + (rect.width - label.get_width()) // 2,
        rect.y + (rect.height - label.get_height()) // 2
    ))

def draw_ui(mouse_pos):
    global fade_alpha, slide_x, selected_scale, highlight_alpha, score_bump, idle_phase

    WIN.fill(BLACK)

    # Score
    score_surf = pygame.transform.rotozoom(
        SMALL.render(f"Wins: {wins}   Losses: {losses}   Draws: {draws}", True, WHITE),
        0, score_bump
    )
    WIN.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 30))

    # Labels and VS
    WIN.blit(TINY.render("Player:", True, WHITE), (130, 300))
    WIN.blit(TINY.render("Computer:", True, WHITE), (360, 300))
    WIN.blit(FONT.render("VS", True, WHITE), (WIDTH // 2 - 30, 330))

    # Player image
    if player_choice:
        pimg = images[player_choice]
        if selected_scale < 1.2:
            selected_scale += 0.02
        zoomed = pygame.transform.rotozoom(pimg, 0, selected_scale)
        WIN.blit(zoomed, (100 + (120 - zoomed.get_width()) // 2, 340))

    # Computer image
    if submitted:
        slide_x = max(slide_x - 40, 360)
        WIN.blit(images[computer_choice], (slide_x, 340))
    elif player_choice:
        WIN.blit(question, (360, 340))

    # Result text
    if submitted:
        if fade_alpha < 255:
            fade_alpha += 15
        result_surf = FONT.render(result_text, True, GREEN if "Win" in result_text else RED if "Lose" in result_text else WHITE)
        result_surf.set_alpha(fade_alpha)
        WIN.blit(result_surf, (WIDTH // 2 - result_surf.get_width() // 2, 210))

    # Choice icons
    idle_phase += 0.1
    for choice in choices:
        cx, cy = positions[choice]
        bounce = math.sin(idle_phase + cx * 0.01) * 5
        WIN.blit(images[choice], (cx, cy + bounce))
        if choice == player_choice:
            highlight_alpha = min(highlight_alpha + 15, 255)
            surface = pygame.Surface((130, 130), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*BLUE, highlight_alpha), (0, 0, 130, 130), 4, border_radius=6)
            WIN.blit(surface, (cx - 5, cy - 5 + bounce))

    # Button
    submit_rect = pygame.Rect(200, 560, 200, 50)
    draw_button(submit_rect, "Submit" if not submitted else "Try Again", player_choice is not None, submit_rect.collidepoint(mouse_pos))
    return submit_rect

# Main loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    submit_rect = draw_ui(mouse_pos)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if not submitted:
                for choice in choices:
                    cx, cy = positions[choice]
                    if cx < x < cx + 120 and cy < y < cy + 120:
                        player_choice = choice
                        selected_scale = 0.8
                        highlight_alpha = 0
            if submit_rect.collidepoint((x, y)) and player_choice:
                if not submitted:
                    computer_choice = random.choice(choices)
                    result_text = determine_winner(player_choice, computer_choice)
                    fade_alpha = 0
                    slide_x = 600
                    submitted = True
                    score_bump = 1.2
                    if result_text == "You Win":
                        wins += 1
                    elif result_text == "You Lose":
                        losses += 1
                    else:
                        draws += 1
                else:
                    player_choice = None
                    computer_choice = None
                    result_text = ""
                    submitted = False
                    selected_scale = 1.0
                    highlight_alpha = 0
                    score_bump = 1.0

    if score_bump > 1.0:
        score_bump -= 0.01

    clock.tick(60)

pygame.quit()
sys.exit()
