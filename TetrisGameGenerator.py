"""
TetrisGameGenerator.py – Generates a random Tetris board and piece sequence.

Uses tetris_engine pure functions directly; no inheritance from a base class.
"""

from __future__ import annotations

import random
import numpy as np

from tetromino_data import TETROMINO_SHAPES, TETROMINO_NAMES
import tetris_engine as engine


class TetrisGameGenerator:
    """Generate a deterministic Tetris board + sequence from a seed.

    Parameters
    ----------
    height, width : int
        Board dimensions (default 20×10).
    seed : int | None
        Random seed for deterministic generation.
    goal : int
        Target line-clear count (stored for downstream use; not used here).
    tetrominoes : int
        How many pieces to include in the sequence.
    initial_height_max : int
        Stop pre-filling the board when the highest column reaches this many
        rows from the bottom.
    """

    def __init__(
        self,
        height: int = 20,
        width: int = 10,
        seed: int | None = None,
        goal: int = 15,
        tetrominoes: int = 40,
        initial_height_max: int = 7,
    ) -> None:
        self.height = height
        self.width = width
        self.seed = seed
        self.goal = goal
        self.tetrominoes = tetrominoes
        self.initial_height_max = initial_height_max

        rng = random.Random(seed)
        self.board = engine.empty_board(height, width)
        self._fill_board(rng)
        self.sequence = self._generate_sequence(rng, tetrominoes)

    # ── Board generation ──────────────────────────────────────────────────────

    def _fill_board(self, rng: random.Random) -> None:
        """Drop random pieces until the stack reaches `initial_height_max`."""
        while True:
            name = rng.choice(TETROMINO_NAMES)
            shape = rng.choice(TETROMINO_SHAPES[name])
            _, shape_w = shape.shape
            col = rng.randint(0, self.width - shape_w)

            if not engine.can_place(self.board, shape, 0, col):
                continue

            landing_row = engine.drop_row(self.board, shape, col)
            if landing_row < 0:
                continue

            # How many rows from the bottom does the piece land?
            _, shape_h = shape.shape  # shape_h is actually rows
            rows, _ = shape.shape
            stack_height = self.height - landing_row
            if stack_height > self.initial_height_max:
                break

            engine.place_piece(self.board, shape, landing_row, col)
            self.board, _ = engine.clear_lines(self.board)

    # ── Sequence generation ────────────────────────────────────────────────────

    def _generate_sequence(self, rng: random.Random, count: int) -> list[str]:
        """Generate a piece sequence using the 7-bag system.

        Each bag contains exactly one of every piece type, shuffled.
        Consecutive identical S/Z pieces within a bag trigger a re-shuffle.
        """
        bag_size = len(TETROMINO_NAMES)
        sequence: list[str] = []

        while len(sequence) < count:
            bag = TETROMINO_NAMES.copy()
            rng.shuffle(bag)
            while any(
                bag[i] in ('S', 'Z') and bag[i] == bag[i + 1]
                for i in range(bag_size - 1)
            ):
                rng.shuffle(bag)
            sequence.extend(bag)

        return sequence[:count]

    def print_grid(self) -> None:
        for row in self.board:
            print(' '.join(map(str, row)))


def generate_board_and_sequence(
    seed: int,
    tetrominoes: int,
    initial_height_max: int,
    goal: int = 0,
) -> tuple[np.ndarray, list[str]]:
    game = TetrisGameGenerator(
        seed=seed,
        goal=goal,
        tetrominoes=tetrominoes,
        initial_height_max=initial_height_max,
    )
    return game.board, game.sequence


def main() -> None:
    game = TetrisGameGenerator(seed=15, goal=15, tetrominoes=40, initial_height_max=7)
    game.print_grid()
    print(game.sequence)


if __name__ == '__main__':
    import cProfile
    cProfile.run('main()', sort='cumulative')
