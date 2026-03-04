import random
import numpy as np
from tetris_board import TetrisBoard
from tetromino_data import TETROMINO_SHAPES, TETROMINO_NAMES


class TetrisGameGenerator(TetrisBoard):
    def __init__(self, height=20, width=10, seed=None, goal=15, tetrominoes=40, initial_height_max=7):
        super().__init__(height, width)
        self.seed = seed
        self.goal = goal
        self.tetrominoes = tetrominoes
        self.initial_height_max = initial_height_max

        random.seed(self.seed)
        self._fill_grid()
        self.sequence = self._generate_tetromino_sequence(self.tetrominoes)

    def _fill_grid(self):
        while True:
            name = random.choice(TETROMINO_NAMES)
            rotation = random.randint(0, len(TETROMINO_SHAPES[name]) - 1)
            shape = self.rotate_tetromino(TETROMINO_SHAPES[name], rotation)
            col = random.randint(0, self.width - len(shape[0]))
            if self.is_valid_move(shape, 0, col):
                placement_height = self.calculate_placement_height(shape, col)
                if self.height + 1 - placement_height <= self.initial_height_max:
                    self.place_tetromino(shape, 0, col)
                else:
                    break

    def _generate_tetromino_sequence(self, max_moves=None):
        bag_size = len(TETROMINO_NAMES)
        bags = []
        while True:
            bag = TETROMINO_NAMES.copy()
            random.shuffle(bag)
            while any(bag[i] in ('S', 'Z') and bag[i] == bag[i + 1] for i in range(bag_size - 1)):
                random.shuffle(bag)
            bags.append(bag)
            if len(bags) * bag_size >= max_moves:
                sequence = [piece for b in bags for piece in b]
                return sequence[:max_moves] if max_moves else sequence

    def print_grid(self):
        for row in self.board:
            print(' '.join(map(str, row)))


def generate_board_and_sequence(seed, tetrominoes, initial_height_max, goal=0):
    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    return game.board, game.sequence


def main():
    game = TetrisGameGenerator(seed=15, goal=15, tetrominoes=40, initial_height_max=7)
    game.print_grid()
    print(game.sequence)


if __name__ == "__main__":
    import cProfile
    cProfile.run('main()', sort='cumulative')
