import numpy as np

# Raw list-of-lists definitions for each piece and all its rotations.
# Pre-converted to numpy uint8 arrays at import time to avoid repeated
# np.array() calls in hot solver loops.
_RAW_SHAPES: dict[str, list[list[list[int]]]] = {
    'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    'J': [
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[0, 1], [0, 1], [1, 1]],
    ],
    'L': [
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]],
    ],
    'O': [[[1, 1], [1, 1]]],
    'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]],
    ],
    'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]],
}

# Public: each value is a tuple of numpy uint8 arrays — one per rotation.
TETROMINO_SHAPES: dict[str, tuple[np.ndarray, ...]] = {
    name: tuple(np.array(rot, dtype=np.uint8) for rot in rotations)
    for name, rotations in _RAW_SHAPES.items()
}

TETROMINO_NAMES: list[str] = list(TETROMINO_SHAPES.keys())
