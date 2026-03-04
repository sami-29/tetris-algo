"""
tetris_engine.py – Pure functions that implement Tetris board mechanics.

All functions operate on a numpy uint8 array of shape (height, width).
0 = empty, 1 = filled. No mutable class state; callers manage board copies.
"""

import numpy as np

BOARD_HEIGHT = 20
BOARD_WIDTH = 10

# Heuristic weights (tuned for line-clearing focus)
_W_LINES = 1000.0
_W_HEIGHT = -51.0
_W_HOLES = -35.0
_W_BUMPINESS = -18.0


def empty_board(height: int = BOARD_HEIGHT, width: int = BOARD_WIDTH) -> np.ndarray:
    return np.zeros((height, width), dtype=np.uint8)


def drop_row(board: np.ndarray, shape: np.ndarray, col: int) -> int:
    """Return the highest row index at which `shape` can legally rest in `col`.

    The piece starts at row 0 and slides down until it would collide or exit
    the board. Returns the last valid row (0-indexed from the top).
    """
    h, w = board.shape
    rows, cols = shape.shape
    row = 0
    while row + rows <= h:
        if np.any(board[row:row + rows, col:col + cols] + shape > 1):
            break
        row += 1
    return row - 1


def can_place(board: np.ndarray, shape: np.ndarray, row: int, col: int) -> bool:
    """Return True if `shape` fits at (row, col) without overlap or out-of-bounds."""
    h, w = board.shape
    rows, cols = shape.shape
    if row < 0 or row + rows > h or col < 0 or col + cols > w:
        return False
    return not np.any(board[row:row + rows, col:col + cols] + shape > 1)


def place_piece(board: np.ndarray, shape: np.ndarray, row: int, col: int) -> None:
    """Write `shape` onto `board` at (row, col) — mutates board in-place."""
    rows, cols = shape.shape
    board[row:row + rows, col:col + cols] += shape


def clear_lines(board: np.ndarray) -> tuple[np.ndarray, int]:
    """Remove all fully filled rows and prepend empty rows at the top.

    Returns (new_board, lines_cleared). Does NOT mutate the original array.
    """
    full = np.all(board, axis=1)
    n = int(full.sum())
    if n == 0:
        return board, 0
    new_board = np.vstack([
        np.zeros((n, board.shape[1]), dtype=np.uint8),
        board[~full],
    ])
    return new_board, n


def get_valid_columns(board: np.ndarray, shape: np.ndarray) -> list[int]:
    """Return all column indices where `shape` can be legally placed (at row 0)."""
    _, board_w = board.shape
    _, shape_w = shape.shape
    return [c for c in range(board_w - shape_w + 1) if can_place(board, shape, 0, c)]


def column_heights(board: np.ndarray) -> np.ndarray:
    """Return the filled height of each column (number of occupied cells from bottom)."""
    h, w = board.shape
    heights = np.zeros(w, dtype=np.int32)
    for c in range(w):
        col = board[:, c]
        filled = np.where(col == 1)[0]
        if filled.size:
            heights[c] = h - filled[0]
    return heights


def count_holes(board: np.ndarray) -> int:
    """Count empty cells that have at least one filled cell above them."""
    holes = 0
    _, w = board.shape
    for c in range(w):
        col = board[:, c]
        filled_above = False
        for cell in col:
            if cell == 1:
                filled_above = True
            elif filled_above:
                holes += 1
    return holes


def bumpiness(heights: np.ndarray) -> int:
    """Sum of absolute differences between adjacent column heights."""
    return int(np.sum(np.abs(np.diff(heights))))


def count_complete_lines(board: np.ndarray) -> int:
    """Return the number of rows that are completely filled."""
    return int(np.sum(np.all(board, axis=1)))


def evaluate(board: np.ndarray) -> float:
    """Score a board state. Higher is better.

    Weights encourage: clearing lines, low stack height, few holes, flat surface.
    """
    heights = column_heights(board)
    lines = count_complete_lines(board)
    holes = count_holes(board)
    bump = bumpiness(heights)
    agg_height = int(heights.sum())
    return (
        _W_LINES * lines
        + _W_HEIGHT * agg_height
        + _W_HOLES * holes
        + _W_BUMPINESS * bump
    )
