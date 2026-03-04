import numpy as np
from collections import deque
from tetris_board import TetrisBoard
from tetromino_data import TETROMINO_SHAPES


class TetrisSolver(TetrisBoard):
    def __init__(self, board, sequence, goal, max_attempts=100000):
        height, width = np.array(board).shape
        super().__init__(height, width)
        self.board = np.array(board)
        self.initial_board = np.array(board)
        self.sequence = deque(sequence)
        self.lines_cleared = 0
        self.failed_attempts = 0
        self.goal = goal
        self.max_attempts = max_attempts

    def reset(self):
        self.board = np.copy(self.initial_board)
        self.lines_cleared = 0
        self.failed_attempts = 0

    def clear_lines(self) -> int:
        full_rows = np.all(self.board, axis=1)
        lines_cleared = int(np.sum(full_rows))
        if lines_cleared:
            self.board = np.vstack([
                np.zeros((lines_cleared, self.width), dtype=int),
                self.board[~full_rows],
            ])
            self.lines_cleared += lines_cleared
        return lines_cleared

    def place_tetromino(self, tetromino, row: int, col: int):
        shape = np.array(tetromino)
        rows, cols = shape.shape
        while row + rows <= self.height and not np.any(
            self.board[row:row + rows, col:col + cols] + shape > 1
        ):
            row += 1
        np.add(
            self.board[row - 1:row - 1 + rows, col:col + cols],
            shape,
            out=self.board[row - 1:row - 1 + rows, col:col + cols],
        )
        self.clear_lines()

    def is_game_over(self) -> bool:
        return bool(np.any(self.board[0] == 1))

    def _evaluate_columns(self, tetromino):
        """Return at most one best column for the given tetromino rotation, sorted by placement height.
        Skip if the board's top row is already occupied (game effectively over)."""
        if np.any(self.board[0] == 1):
            return []
        columns = list(range(self.width - len(tetromino[0]) + 1))
        columns.sort(key=lambda col: -self.calculate_placement_height(tetromino, col))
        return columns[:1]

    def visualize(self, board=None) -> str:
        if board is None:
            board = self.board
        return '\n'.join([' '.join(map(str, row)) for row in board])

    def solve(self, current=None):
        current = current if current else self.sequence.popleft()
        shape = TETROMINO_SHAPES[current]

        for rotation in range(len(shape)):
            for col in self._evaluate_columns(shape[rotation]):
                if self.failed_attempts >= self.max_attempts:
                    return False, [], self.failed_attempts

                board_snapshot = np.copy(self.board)
                lines_snapshot = self.lines_cleared

                if not self.is_valid_move(shape[rotation], 0, col):
                    self.failed_attempts += 1
                    continue

                self.place_tetromino(shape[rotation], 0, col)

                if self.is_game_over():
                    self.board = board_snapshot
                    self.lines_cleared = lines_snapshot
                    self.failed_attempts += 1
                    continue

                if self.lines_cleared >= self.goal:
                    return True, [(current, rotation, col)], self.failed_attempts

                if self.sequence:
                    next_piece = self.sequence.popleft()
                    result, moves, attempts = self.solve(next_piece)
                    if result:
                        return True, [(current, rotation, col)] + moves, attempts
                    self.sequence.appendleft(next_piece)

                self.board = board_snapshot
                self.lines_cleared = lines_snapshot
                self.failed_attempts += 1

        return False, [], self.failed_attempts

    def visualize_moves(self, stack):
        self.reset()
        for tetromino, rotation, col in stack:
            initial_lines = self.lines_cleared
            self.place_tetromino(TETROMINO_SHAPES[tetromino][rotation], 0, col)
            print(f"Tetromino: {tetromino}  Rotation: {rotation}  Column: {col}")
            print(f"Lines cleared: {self.lines_cleared - initial_lines}")
            print(self.visualize())
            print()


if __name__ == '__main__':
    from time import time
    from TetrisGameGenerator import TetrisGameGenerator
    import cProfile

    seed, goal, tetrominoes, initial_height_max = 1, 10, 40, 14

    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    solver = TetrisSolver(game.board, game.sequence, goal)

    print(solver.visualize())

    profiler = cProfile.Profile()
    profiler.enable()
    start = time()
    result, stack, failed_attempts = solver.solve()
    end = time()
    profiler.disable()
    profiler.print_stats(sort='cumulative')

    print(f'Time taken: {end - start:.3f}s')
    print(f'Result: {result}')
    print(f'Stack: {stack}')
    print(f'Failed attempts: {failed_attempts}')
    print(f'Lines cleared: {solver.lines_cleared}')

    solver.visualize_moves(stack)
