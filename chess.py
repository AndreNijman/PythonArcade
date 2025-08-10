"""Simplified chess game with AI, menu, and full mechanics.

This module implements a playable chess game using pygame.  It supports
all standard chess rules including castling, en passant and promotion.
A simple minimax based AI is included with three difficulty levels.
The game can be played in two player mode or against the AI.

The goal of this file is to provide an example of a complete game
implementation suitable for small projects or teaching purposes.  The
implementation purposely avoids using external chess libraries so that
the rules are encoded directly in Python and therefore easy to read.
"""
from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import io
import sys
import sysconfig
import importlib.util

import pygame
import cairosvg

# Load python-chess module dynamically to access piece SVGs without
# clashing with this file's name.
spec = importlib.util.spec_from_file_location(
    "chess", sysconfig.get_path("purelib") + "/chess/__init__.py"
)
chess = importlib.util.module_from_spec(spec)
sys.modules["chess"] = chess
spec.loader.exec_module(chess)
import chess.svg

# ---------------------------------------------------------------------------
# Basic data structures
# ---------------------------------------------------------------------------

WHITE, BLACK = "w", "b"
PIECES = ["K", "Q", "R", "B", "N", "P"]

# Piece values for evaluation
PIECE_VALUES = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100}

BOARD_SIZE = 8

Move = Tuple[int, int, int, int, Optional[str]]  # (r0,c0,r1,c1,promotion)


def initial_board() -> List[List[str]]:
    """Return the starting board configuration."""
    board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for c in range(BOARD_SIZE):
        board[1][c] = BLACK + "P"
        board[6][c] = WHITE + "P"
    pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for c, p in enumerate(pieces):
        board[0][c] = BLACK + p
        board[7][c] = WHITE + p
    return board


def clone_board(board: List[List[str]]) -> List[List[str]]:
    return [row[:] for row in board]


@dataclass
class GameState:
    board: List[List[str]]
    white_to_move: bool = True
    castling: str = "KQkq"  # king/queen side rights
    en_passant: Optional[Tuple[int, int]] = None
    halfmove_clock: int = 0
    fullmove_number: int = 1

    def copy(self) -> "GameState":
        return GameState(
            clone_board(self.board),
            self.white_to_move,
            self.castling,
            self.en_passant,
            self.halfmove_clock,
            self.fullmove_number,
        )


# ---------------------------------------------------------------------------
# Move generation and rules
# ---------------------------------------------------------------------------

DIRECTIONS = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "W": (0, -1),
    "NE": (-1, 1),
    "NW": (-1, -1),
    "SE": (1, 1),
    "SW": (1, -1),
}


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def square_attacked(state: GameState, r: int, c: int, by_white: bool) -> bool:
    """Return True if square (r,c) is attacked by the given color."""
    board = state.board
    enemy = WHITE if by_white else BLACK
    pawn_dir = -1 if by_white else 1
    # Pawns
    for dc in (-1, 1):
        rr, cc = r + pawn_dir, c + dc
        if in_bounds(rr, cc) and board[rr][cc] == enemy + "P":
            return True
    # Knights
    for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        rr, cc = r + dr, c + dc
        if in_bounds(rr, cc) and board[rr][cc] == enemy + "N":
            return True
    # Sliding pieces
    sliders = [
        ("BQ", ["NE", "NW", "SE", "SW"]),
        ("RQ", ["N", "S", "E", "W"]),
    ]
    for pieces, dirs in sliders:
        for d in dirs:
            dr, dc = DIRECTIONS[d]
            rr, cc = r + dr, c + dc
            while in_bounds(rr, cc):
                piece = board[rr][cc]
                if piece:
                    if piece[0] == enemy and piece[1] in pieces:
                        return True
                    break
                rr += dr
                cc += dc
    # King
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if not dr and not dc:
                continue
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc) and board[rr][cc] == enemy + "K":
                return True
    return False


def is_in_check(state: GameState, white: bool) -> bool:
    # Locate king
    k = WHITE + "K" if white else BLACK + "K"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state.board[r][c] == k:
                return square_attacked(state, r, c, not white)
    return False


def generate_moves(state: GameState) -> List[Move]:
    board = state.board
    moves: List[Move] = []
    color = WHITE if state.white_to_move else BLACK
    enemy = BLACK if state.white_to_move else WHITE
    pawn_dir = -1 if state.white_to_move else 1

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if not piece or piece[0] != color:
                continue
            ptype = piece[1]
            if ptype == "P":
                # Forward move
                rr = r + pawn_dir
                if in_bounds(rr, c) and not board[rr][c]:
                    if rr in (0, 7):
                        for promo in ["Q", "R", "B", "N"]:
                            moves.append((r, c, rr, c, promo))
                    else:
                        moves.append((r, c, rr, c, None))
                    if (r == 6 and color == WHITE) or (r == 1 and color == BLACK):
                        rr2 = r + 2 * pawn_dir
                        if not board[rr2][c]:
                            moves.append((r, c, rr2, c, None))
                # Captures
                for dc in (-1, 1):
                    cc = c + dc
                    rr = r + pawn_dir
                    if in_bounds(rr, cc):
                        target = board[rr][cc]
                        if target and target[0] == enemy:
                            if rr in (0, 7):
                                for promo in ["Q", "R", "B", "N"]:
                                    moves.append((r, c, rr, cc, promo))
                            else:
                                moves.append((r, c, rr, cc, None))
                    if state.en_passant == (rr, cc):
                        moves.append((r, c, rr, cc, None))
            elif ptype == "N":
                for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                    rr, cc = r + dr, c + dc
                    if in_bounds(rr, cc) and (not board[rr][cc] or board[rr][cc][0] == enemy):
                        moves.append((r, c, rr, cc, None))
            elif ptype in ("B", "R", "Q"):
                dirs = []
                if ptype in ("B", "Q"):
                    dirs += ["NE", "NW", "SE", "SW"]
                if ptype in ("R", "Q"):
                    dirs += ["N", "S", "E", "W"]
                for d in dirs:
                    dr, dc = DIRECTIONS[d]
                    rr, cc = r + dr, c + dc
                    while in_bounds(rr, cc):
                        if not board[rr][cc]:
                            moves.append((r, c, rr, cc, None))
                        else:
                            if board[rr][cc][0] == enemy:
                                moves.append((r, c, rr, cc, None))
                            break
                        rr += dr
                        cc += dc
            elif ptype == "K":
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if not dr and not dc:
                            continue
                        rr, cc = r + dr, c + dc
                        if in_bounds(rr, cc) and (not board[rr][cc] or board[rr][cc][0] == enemy):
                            moves.append((r, c, rr, cc, None))
                # Castling
                if color == WHITE:
                    rights = [("K", (7, 4, 7, 6, 7, 5)), ("Q", (7, 4, 7, 2, 7, 3))]
                else:
                    rights = [("k", (0, 4, 0, 6, 0, 5)), ("q", (0, 4, 0, 2, 0, 3))]
                for sym, (r0, c0, r1, c1, r2, c2) in rights:
                    if sym in state.castling and not board[r1][c1] and not board[r2][c2]:
                        if not square_attacked(state, r0, c0, not state.white_to_move) and not square_attacked(state, r2, c2, not state.white_to_move) and not square_attacked(state, r1, c1, not state.white_to_move):
                            moves.append((r0, c0, r2, c2, None))
    # Filter illegal moves
    legal: List[Move] = []
    for m in moves:
        st = apply_move(state, m, make_copy=True)
        if not is_in_check(st, state.white_to_move):
            legal.append(m)
    return legal


def apply_move(state: GameState, move: Move, make_copy: bool = False) -> GameState:
    """Apply move and return new state."""
    if make_copy:
        state = state.copy()
    r0, c0, r1, c1, promo = move
    piece = state.board[r0][c0]
    state.board[r0][c0] = ""
    # En passant capture
    if piece[1] == "P" and (r1, c1) == state.en_passant:
        state.board[r0][c1] = ""
    # Castling
    if piece[1] == "K" and abs(c1 - c0) == 2:
        if c1 > c0:  # king side
            rook_from = (r0, 7)
            rook_to = (r0, 5)
        else:
            rook_from = (r0, 0)
            rook_to = (r0, 3)
        rook = state.board[rook_from[0]][rook_from[1]]
        state.board[rook_from[0]][rook_from[1]] = ""
        state.board[rook_to[0]][rook_to[1]] = rook
    # Move piece
    state.board[r1][c1] = piece if not promo else piece[0] + promo
    # Update en passant square
    state.en_passant = None
    if piece[1] == "P" and abs(r1 - r0) == 2:
        state.en_passant = ((r0 + r1) // 2, c0)
    # Update castling rights
    if piece[1] == "K":
        if piece[0] == WHITE:
            state.castling = state.castling.replace("K", "").replace("Q", "")
        else:
            state.castling = state.castling.replace("k", "").replace("q", "")
    if piece[1] == "R":
        if r0 == 7 and c0 == 0:
            state.castling = state.castling.replace("Q", "")
        if r0 == 7 and c0 == 7:
            state.castling = state.castling.replace("K", "")
        if r0 == 0 and c0 == 0:
            state.castling = state.castling.replace("q", "")
        if r0 == 0 and c0 == 7:
            state.castling = state.castling.replace("k", "")
    # Halfmove clock and fullmove number
    if piece[1] == "P" or state.board[r1][c1]:
        state.halfmove_clock = 0
    else:
        state.halfmove_clock += 1
    if not state.white_to_move:
        state.fullmove_number += 1
    state.white_to_move = not state.white_to_move
    return state


def result(state: GameState) -> Optional[str]:
    moves = generate_moves(state)
    if moves:
        if state.halfmove_clock >= 100:
            return "draw"
        return None
    if is_in_check(state, state.white_to_move):
        return "black" if state.white_to_move else "white"
    return "draw"


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------


def evaluate(state: GameState) -> int:
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = state.board[r][c]
            if piece:
                value = PIECE_VALUES[piece[1]]
                score += value if piece[0] == WHITE else -value
    return score


def minimax(state: GameState, depth: int, alpha: int, beta: int, maximizing: bool) -> Tuple[int, Optional[Move]]:
    res = result(state)
    if res == "white":
        return (math.inf, None)
    if res == "black":
        return (-math.inf, None)
    if res == "draw" or depth == 0:
        return evaluate(state), None
    best_move: Optional[Move] = None
    if maximizing:
        max_eval = -math.inf
        for move in generate_moves(state):
            eval, _ = minimax(apply_move(state, move, make_copy=True), depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in generate_moves(state):
            eval, _ = minimax(apply_move(state, move, make_copy=True), depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move


class AIPlayer:
    def __init__(self, difficulty: str):
        self.depth = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty, 1)

    def choose_move(self, state: GameState) -> Move:
        moves = generate_moves(state)
        if self.depth == 1:
            return random.choice(moves)
        _, move = minimax(state, self.depth, -math.inf, math.inf, state.white_to_move)
        if move is None:
            move = random.choice(moves)
        return move


# ---------------------------------------------------------------------------
# Pygame UI
# ---------------------------------------------------------------------------

WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = WIDTH // BOARD_SIZE

pygame.init()
FONT = pygame.font.SysFont("arial", 24)
SMALL_FONT = pygame.font.SysFont("arial", 18)

COLORS = [(238, 238, 210), (118, 150, 86)]
HIGHLIGHT = (246, 246, 105)


def load_piece_images() -> dict[str, pygame.Surface]:
    images: dict[str, pygame.Surface] = {}
    for color in (WHITE, BLACK):
        for piece in PIECES:
            symbol = piece if color == WHITE else piece.lower()
            svg_data = chess.svg.piece(chess.Piece.from_symbol(symbol), size=SQUARE_SIZE)
            png_data = cairosvg.svg2png(bytestring=str(svg_data).encode("utf-8"))
            images[color + piece] = pygame.image.load(io.BytesIO(png_data))
    return images


PIECE_IMAGES = load_piece_images()


def draw_board(screen: pygame.Surface, state: GameState, selected: Optional[Tuple[int, int]], moves: List[Move]):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = COLORS[(r + c) % 2]
            pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    if selected:
        r, c = selected
        pygame.draw.rect(screen, HIGHLIGHT, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        for m in moves:
            if m[0] == r and m[1] == c:
                rr, cc = m[2], m[3]
                pygame.draw.circle(screen, HIGHLIGHT, (cc * SQUARE_SIZE + SQUARE_SIZE // 2, rr * SQUARE_SIZE + SQUARE_SIZE // 2), 10)
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = state.board[r][c]
            if piece:
                screen.blit(PIECE_IMAGES[piece], (c * SQUARE_SIZE, r * SQUARE_SIZE))


def save_game(state: GameState, path: str):
    with open(path, "w") as f:
        json.dump(state.__dict__, f)


def load_game(path: str) -> GameState:
    with open(path) as f:
        data = json.load(f)
    board = data["board"]
    return GameState(board, data["white_to_move"], data["castling"], tuple(data["en_passant"]) if data["en_passant"] else None, data["halfmove_clock"], data["fullmove_number"])


# ---------------------------------------------------------------------------
# Menu and main loop
# ---------------------------------------------------------------------------


def menu(screen: pygame.Surface) -> Tuple[str, str]:
    difficulty = "easy"
    mode = "ai"
    while True:
        screen.fill((0, 0, 0))
        title = FONT.render("Chess", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        opts = [
            f"1. Start Game ({'AI' if mode == 'ai' else '2P'})",
            f"2. Difficulty ({difficulty})",
            "3. Load Game",
            "ESC. Quit",
        ]
        for i, text in enumerate(opts):
            img = SMALL_FONT.render(text, True, (255, 255, 255))
            screen.blit(img, (50, 150 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise SystemExit
                if event.key == pygame.K_1:
                    return mode, difficulty
                if event.key == pygame.K_2:
                    difficulty = {"easy": "medium", "medium": "hard", "hard": "easy"}[difficulty]
                if event.key == pygame.K_3:
                    if os.path.exists("saved_game.json"):
                        return "load", difficulty
    return mode, difficulty


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    mode, difficulty = menu(screen)
    if mode == "load":
        state = load_game("saved_game.json")
    else:
        state = GameState(initial_board())
        ai = AIPlayer(difficulty)
    running = True
    selected: Optional[Tuple[int, int]] = None
    history: List[GameState] = [state.copy()]
    while running:
        if mode == "ai" and not state.white_to_move:
            move = ai.choose_move(state)
            state = apply_move(state, move)
            history.append(state.copy())
            selected = None
            res = result(state)
            if res:
                print("Result:", res)
        draw_board(screen, state, selected, generate_moves(state))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and len(history) > 1:
                    history.pop()
                    state = history[-1].copy()
                if event.key == pygame.K_s:
                    save_game(state, "saved_game.json")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                c = event.pos[0] // SQUARE_SIZE
                r = event.pos[1] // SQUARE_SIZE
                if selected:
                    moves = generate_moves(state)
                    move = next((m for m in moves if m[0] == selected[0] and m[1] == selected[1] and m[2] == r and m[3] == c), None)
                    if move:
                        if move[4] and state.white_to_move:
                            # simple promotion to queen only in UI
                            move = (move[0], move[1], move[2], move[3], "Q")
                        state = apply_move(state, move)
                        history.append(state.copy())
                        res = result(state)
                        if res:
                            print("Result:", res)
                        selected = None
                    else:
                        selected = (r, c)
                else:
                    piece = state.board[r][c]
                    if piece and ((piece[0] == WHITE) == state.white_to_move):
                        selected = (r, c)
        pygame.time.wait(20)
    pygame.quit()


if __name__ == "__main__":
    main()
