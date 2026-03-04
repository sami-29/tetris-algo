"""
TetrisSolver.py – Adaptive beam search Tetris solver.

Uses a progressive widening strategy: attempt a narrow beam first (fast),
then retry with progressively wider beams if needed. This gives near-instant
results on easy games while still solving hard ones that a narrow beam misses.

Public API:
    solver = TetrisSolver(board, sequence, goal)
    result, moves, evaluations = solver.solve()
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field

from tetromino_data import TETROMINO_SHAPES
import tetris_engine as engine

# Beam widths to try in order. The solver runs a full search at each width
# and returns immediately on success. Only moves to the next width on failure.
_BEAM_SCHEDULE = (1, 5, 20, 100)


@dataclass
class _State:
    score: float
    lines_cleared: int
    board: np.ndarray
    moves: list[tuple[str, int, int]]


class TetrisSolver:
    """Progressive beam-search solver for the Tetris line-clearing problem.

    Parameters
    ----------
    board : array-like
        20×10 initial board (0 = empty, 1 = filled).
    sequence : list[str]
        Ordered list of tetromino names to place.
    goal : int
        Number of lines to clear to win.
    beam_schedule : tuple[int, ...]
        Sequence of beam widths to attempt in order.
        Narrower widths are tried first for speed; wider widths are used
        as fallback when the narrow search fails.
    max_attempts : int
        Kept for API compatibility; unused.
    """

    def __init__(
        self,
        board: list | np.ndarray,
        sequence: list[str],
        goal: int,
        beam_schedule: tuple[int, ...] = _BEAM_SCHEDULE,
        max_attempts: int = 100_000,
    ) -> None:
        self.initial_board = np.array(board, dtype=np.uint8)
        self.sequence = list(sequence)
        self.goal = goal
        self.beam_schedule = beam_schedule

    def solve(self) -> tuple[bool, list[tuple[str, int, int]], int]:
        """Run progressive beam search.

        Returns
        -------
        success : bool
        moves : list of (piece_name, rotation_index, column) tuples
        evaluations : int
            Total board positions evaluated across all attempts.
        """
        total_evals = 0
        for width in self.beam_schedule:
            success, moves, evals = self._beam_search(width)
            total_evals += evals
            if success:
                return True, moves, total_evals
        return False, [], total_evals

    def _beam_search(self, beam_width: int) -> tuple[bool, list[tuple[str, int, int]], int]:
        """Single beam search pass at the given width."""
        evaluations = 0
        beam: list[_State] = [_State(
            score=engine.evaluate(self.initial_board),
            lines_cleared=0,
            board=self.initial_board.copy(),
            moves=[],
        )]

        for piece_name in self.sequence:
            rotations = TETROMINO_SHAPES[piece_name]
            candidates: list[_State] = []

            for state in beam:
                for rot_idx, shape in enumerate(rotations):
                    for col in engine.get_valid_columns(state.board, shape):
                        evaluations += 1

                        landing_row = engine.drop_row(state.board, shape, col)
                        if landing_row < 0:
                            continue

                        new_board = state.board.copy()
                        engine.place_piece(new_board, shape, landing_row, col)
                        new_board, lines_this_move = engine.clear_lines(new_board)

                        new_lines = state.lines_cleared + lines_this_move
                        new_moves = state.moves + [(piece_name, rot_idx, col)]

                        if new_lines >= self.goal:
                            return True, new_moves, evaluations

                        candidates.append(_State(
                            score=engine.evaluate(new_board),
                            lines_cleared=new_lines,
                            board=new_board,
                            moves=new_moves,
                        ))

            if not candidates:
                return False, [], evaluations

            if len(candidates) > beam_width:
                candidates.sort(key=lambda s: s.score, reverse=True)
                candidates = candidates[:beam_width]

            beam = candidates

        return False, [], evaluations
