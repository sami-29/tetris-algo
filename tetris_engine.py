"""
tetris_engine.py – Pure functions that implement Tetris board mechanics.

All functions operate on a numpy uint8 array of shape (height, width).
0 = empty, 1 = filled. No mutable class state; callers manage board copies.

All hot-path functions (column_heights, count_holes, evaluate) are fully
vectorised — no Python-level loops — so they run at C speed on any hardware.
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
    """Return the row index at which `shape` comes to rest in `col`.

    Slides the piece down from row 0 until it would collide or exit.
    Returns the last valid row (0-indexed from top), or -1 if it cannot
    even be placed at row 0.
    """
    h, _ = board.shape
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
    """Return the filled height of each column — fully vectorised.

    Uses argmax to find the first filled row per column in O(1) NumPy ops
    instead of a Python loop over each column.
    """
    any_filled = board.any(axis=0)                      # (width,) bool
    first_filled = (board != 0).argmax(axis=0)          # row index of first block
    h = board.shape[0]
    return np.where(any_filled, h - first_filled, 0).astype(np.int32)


def count_holes(board: np.ndarray) -> int:
    """Count empty cells that have at least one filled cell above them — vectorised.

    A cumulative sum along axis=0 turns any cell below the first filled cell
    in its column positive. Holes are those cells that are positive in that
    mask but empty in the board.
    """
    filled_from_top = np.cumsum(board, axis=0) > 0     # True for cells at/below first block
    return int(np.sum(filled_from_top & (board == 0)))


def bumpiness(heights: np.ndarray) -> int:
    """Sum of absolute differences between adjacent column heights."""
    return int(np.sum(np.abs(np.diff(heights))))


def count_complete_lines(board: np.ndarray) -> int:
    """Return the number of rows that are completely filled."""
    return int(np.sum(np.all(board, axis=1)))


def evaluate(board: np.ndarray) -> float:
    """Score a board state. Higher is better.

    All four sub-computations are vectorised NumPy operations — no Python loops.
    Weights encourage: clearing lines, low stack height, few holes, flat surface.
    """
    heights = column_heights(board)
    lines = int(np.sum(np.all(board, axis=1)))
    holes = count_holes(board)
    bump = int(np.sum(np.abs(np.diff(heights))))
    return (
        _W_LINES * lines
        + _W_HEIGHT * int(heights.sum())
        + _W_HOLES * holes
        + _W_BUMPINESS * bump
    )
