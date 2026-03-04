import numpy as np
from tetromino_data import TETROMINO_SHAPES


class TetrisBoard:
    """Shared Tetris board logic used by both TetrisGameGenerator and TetrisSolver."""

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.board = np.zeros((height, width), dtype=int)

    def rotate_tetromino(self, tetromino, rotation: int):
        return tetromino[rotation % len(tetromino)]

    def is_valid_move(self, tetromino, row: int, col: int) -> bool:
        shape = np.array(tetromino)
        rows, cols = shape.shape
        if row + rows > self.height or col < 0 or col + cols > self.width:
            return False
        return not np.any(self.board[row:row + rows, col:col + cols] + shape > 1)

    def calculate_placement_height(self, tetromino, col: int) -> int:
        shape = np.array(tetromino)
        rows, cols = shape.shape
        height = 0
        while height + rows <= self.height and not np.any(
            self.board[height:height + rows, col:col + cols] + shape > 1
        ):
            height += 1
        return height

    def place_tetromino(self, tetromino, row: int, col: int):
        shape = np.array(tetromino)
        rows, cols = shape.shape
        while row + rows <= self.height and not np.any(
            self.board[row:row + rows, col:col + cols] + shape > 1
        ):
            row += 1
        self.board[row - 1:row - 1 + rows, col:col + cols] += shape
        self.clear_lines()

    def clear_lines(self) -> int:
        full_rows = np.all(self.board, axis=1)
        lines_cleared = int(np.sum(full_rows))
        if lines_cleared:
            self.board = np.vstack([
                np.zeros((lines_cleared, self.width), dtype=int),
                self.board[~full_rows],
            ])
        return lines_cleared
