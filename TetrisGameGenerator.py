import random
import logging
from typing import List, Tuple, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TetrisGameGenerator:
    tetromino_shapes = {
        'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
        'J': [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
        'L': [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],
        'O': [[[1, 1], [1, 1]]],
        'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
        'T': [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
        'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]
    }
    tetrominoes_names: List[str] = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

    def __init__(self, height: int = 20, width: int = 10, seed: int = None, goal: int = 15, tetrominoes: int = 40, initial_height_max: int = 7):
        self.height = height
        self.width = width
        self.seed = seed
        self.goal = goal
        self.tetrominoes = tetrominoes
        self.initial_height_max = initial_height_max
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]

        random.seed(self.seed)
        self.fill_grid()
        self.sequence = self.generate_tetromino_sequence(self.tetrominoes)

    @staticmethod
    def rotate_tetromino(tetromino: List[List[int]], rotation: int) -> List[List[int]]:
        for _ in range(rotation % 4):
            tetromino = list(zip(*tetromino[::-1]))
        return [list(row) for row in tetromino]

    def is_valid_move(self, tetromino: List[List[int]], row: int, col: int) -> bool:
        shape = tetromino
        rows, cols = len(shape), len(shape[0])

        if row + rows > self.height or col < 0 or col + cols > self.width:
            return False

        return not any(shape[r][c] == 1 and self.board[row+r][col+c] == 1
                       for r in range(rows) for c in range(cols))

    def place_tetromino(self, tetromino: List[List[int]], row: int, col: int) -> None:
        shape = tetromino
        rows, cols = len(shape), len(shape[0])

        while row + rows <= self.height and not any(shape[r][c] == 1 and self.board[row+r][col+c] == 1
                                                    for r in range(rows) for c in range(cols)):
            row += 1

        for r in range(rows):
            for c in range(cols):
                if shape[r][c] == 1:
                    self.board[row-1+r][col+c] = 1

        self.clear_lines()

    def clear_lines(self) -> None:
        self.board = [[0 for _ in range(self.width)] for _ in range(sum(1 for row in self.board if 0 in row))] + \
                     [row for row in self.board if 0 not in row]

    def calculate_placement_height(self, tetromino: List[List[int]], col: int) -> int:
        shape = tetromino
        rows, cols = len(shape), len(shape[0])

        height = 0
        while height + rows <= self.height and not any(shape[r][c] == 1 and self.board[height+r][col+c] == 1
                                                       for r in range(rows) for c in range(cols)):
            height += 1

        return height

    def fill_grid(self) -> None:
        while True:
            tetromino = random.choice(self.tetrominoes_names)
            rotation = random.randint(0, len(self.tetromino_shapes[tetromino]) - 1)
            shape = self.rotate_tetromino(self.tetromino_shapes[tetromino][0], rotation)
            col_to_try = random.randint(0, self.width - len(shape[0]) + 1)
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
            bag = random.sample(self.tetrominoes_names, bag_size)
            while any(bag[i] == bag[i + 1] in ['S', 'Z'] for i in range(bag_size - 1)):
                random.shuffle(bag)
            sequence.extend(bag)

        return sequence[:max_moves]

    def print_grid(self) -> None:
        for row in self.board:
            print(' '.join(map(str, row)))

    def visualize_board(self) -> str:
        return '\n'.join([' '.join(map(str, row)) for row in self.board])

    def place_tetromino(self, tetromino: List[List[int]], row: int, col: int) -> None:
        rows, cols = len(tetromino), len(tetromino[0])
        for r in range(rows):
            for c in range(cols):
                if tetromino[r][c] == 1:
                    self.board[row+r][col+c] = 1
        self.clear_lines()

def generate_board_and_sequence(seed: int, tetrominoes: int, initial_height_max: int, goal: int = 0) -> Tuple[List[List[int]], List[str]]:
    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    return game.board, game.sequence

def main() -> None:
    game = TetrisGameGenerator(seed=15, goal=15, tetrominoes=40, initial_height_max=7)
    game.print_grid()
    logging.info(f"Sequence: {game.sequence}")

if __name__ == "__main__":
    import cProfile
    cProfile.run('main()', sort='cumulative')
