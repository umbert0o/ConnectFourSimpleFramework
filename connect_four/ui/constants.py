"""UI constants for the Connect Four visual layer."""

from connect_four.game.player import Player

HEADER_HEIGHT = 80

# Info panel (right side)
PANEL_WIDTH = 280
PANEL_PADDING = 15
PANEL_BG_COLOR = (25, 25, 40)
PANEL_BORDER_COLOR = (60, 60, 80)

BG_COLOR = (30, 30, 30)
BOARD_COLOR = (0, 70, 170)
EMPTY_COLOR = (20, 20, 20)
PLAYER1_COLOR = (220, 50, 50)
PLAYER2_COLOR = (240, 220, 50)
HOVER_COLOR = (200, 200, 200)

HIGHLIGHT_BORDER = (255, 255, 255)

_PLAYER_COLOR: dict[int, tuple[int, int, int]] = {
    Player.PLAYER_1: PLAYER1_COLOR,
    Player.PLAYER_2: PLAYER2_COLOR,
}
