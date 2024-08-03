import numpy as np
import logging
from typing import List, Tuple, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TetrisGameGenerator:
    tetromino_shapes: Dict[str, List[np.ndarray]] = {
        'I': [np.array([[1, 1, 1, 1]]), np.array([[1], [1], [1], [1]])],
        'J': [np.array([[1, 0, 0], [1, 1, 1]]), np.array([[1, 1], [1, 0], [1, 0]]), np.array([[1, 1, 1], [0, 0, 1]]), np.array([[0, 1], [0, 1], [1, 1]])],
        'L': [np.array([[0, 0, 1], [1, 1, 1]]), np.array([[1, 0], [1, 0], [1, 1]]), np.array([[1, 1, 1], [1, 0, 0]]), np.array([[1, 1], [0, 1], [0, 1]])],
        'O': [np.array([[1, 1], [1, 1]])],
        'S': [np.array([[0, 1, 1], [1, 1, 0]]), np.array([[1, 0], [1, 1], [0, 1]])],
        'T': [np.array([[0, 1, 0], [1, 1, 1]]), np.array([[1, 0], [1, 1], [1, 0]]), np.array([[1, 1, 1], [0, 1, 0]]), np.array([[0, 1], [1, 1], [0, 1]])],
        'Z': [np.array([[1, 1, 0], [0, 1, 1]]), np.array([[0, 1], [1, 1], [1, 0]])]
    }
    tetrominoes_names: List[str] = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

    def __init__(self, height: int = 20, width: int = 10, seed: int = None, goal: int = 15, tetrominoes: int = 40, initial_height_max: int = 7):
        self.height = height
        self.width = width
        self.seed = seed
        self.goal = goal
        self.tetrominoes = tetrominoes
        self.initial_height_max = initial_height_max
        self.board = np.zeros((self.height, self.width), dtype=int)

        np.random.seed(self.seed)
        self.fill_grid()
        self.sequence = self.generate_tetromino_sequence(self.tetrominoes)

    @staticmethod
    def rotate_tetromino(tetromino: np.ndarray, rotation: int) -> np.ndarray:
        return np.rot90(tetromino, k=-rotation)

    def is_valid_move(self, tetromino: np.ndarray, row: int, col: int) -> bool:
        shape = tetromino
        rows, cols = shape.shape

        if row + rows > self.height or col < 0 or col + cols > self.width:
            return False

        return not np.any(np.logical_and(shape == 1, self.board[row:row+rows, col:col+cols] == 1))

    def place_tetromino(self, tetromino: np.ndarray, row: int, col: int) -> None:
        shape = tetromino
        rows, cols = shape.shape

        while row + rows <= self.height and not np.any(np.logical_and(shape == 1, self.board[row:row+rows, col:col+cols] == 1)):
            row += 1

        self.board[row-1:row-1+rows, col:col+cols] = np.logical_or(self.board[row-1:row-1+rows, col:col+cols], shape)
        self.clear_lines()

    def clear_lines(self) -> None:
        full_rows = np.all(self.board, axis=1)
        self.board = np.vstack([np.zeros((np.sum(full_rows), self.width), dtype=int), self.board[~full_rows]])

    def calculate_placement_height(self, tetromino: np.ndarray, col: int) -> int:
        shape = tetromino
        rows, cols = shape.shape

        height = 0
        while height + rows <= self.height and not np.any(np.logical_and(shape == 1, self.board[height:height+rows, col:col+cols] == 1)):
            height += 1

        return height

    def fill_grid(self) -> None:
        while True:
            tetromino = np.random.choice(self.tetrominoes_names)
            rotation = np.random.randint(0, len(self.tetromino_shapes[tetromino]))
            shape = self.rotate_tetromino(self.tetromino_shapes[tetromino][0], rotation)
            col_to_try = np.random.randint(0, self.width - shape.shape[1] + 1)
            if self.is_valid_move(shape, 0, col_to_try):
                placement_height = self.calculate_placement_height(shape, col_to_try)
                if self.height + 1 - placement_height <= self.initial_height_max:
                    self.place_tetromino(shape, 0, col_to_try)
                else:
                    break

    def generate_tetromino_sequence(self, max_moves: int = None) -> List[str]:
        bag_size = 7
        sequence = []

        while len(sequence) < max_moves:
            bag = np.random.permutation(self.tetrominoes_names).tolist()
            while any(bag[i] == bag[i + 1] in ['S', 'Z'] for i in range(bag_size - 1)):
                np.random.shuffle(bag)
            sequence.extend(bag)

        return sequence[:max_moves]

    def print_grid(self) -> None:
        for row in self.board:
            print(' '.join(map(str, row)))

    def visualize_board(self) -> str:
        return '\n'.join([' '.join(map(str, row)) for row in self.board])

    def place_tetromino(self, tetromino: str, rotation: int, col: int) -> None:
        shape = self.rotate_tetromino(self.tetromino_shapes[tetromino][0], rotation)
        rows, cols = shape.shape
        row = 0
        while row + rows <= self.height and not np.any(np.logical_and(shape == 1, self.board[row:row+rows, col:col+cols] == 1)):
            row += 1
        row -= 1
        self.board[row:row+rows, col:col+cols] = np.logical_or(self.board[row:row+rows, col:col+cols], shape)
        self.clear_lines()

def generate_board_and_sequence(seed: int, tetrominoes: int, initial_height_max: int, goal: int = 0) -> Tuple[np.ndarray, List[str]]:
    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    return game.board, game.sequence

def main() -> None:
    game = TetrisGameGenerator(seed=15, goal=15, tetrominoes=40, initial_height_max=7)
    game.print_grid()
    logging.info(f"Sequence: {game.sequence}")

if __name__ == "__main__":
    import cProfile
    cProfile.run('main()', sort='cumulative')
