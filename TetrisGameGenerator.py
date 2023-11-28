import random


class TetrisGameGenerator:
    def __init__(self, height=20, width=10, seed=None, goal=40, tetrominoes=100, initial_height_max=7):
        self.height = height
        self.width = width
        self.seed = seed
        self.goal = goal
        self.tetrominoes = tetrominoes
        self.initial_height_max = initial_height_max
        self.grid = [[0] * width for _ in range(height)]
        self.winnable = False
        self.tetrominoes_names = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

        random.seed(self.seed)
        self.fill_grid()
        self.sequence = self.generate_sequence(self.tetrominoes)

    def fill_grid(self):
        ...


    def generate_tetromino_sequence(self, max_moves=None):
        tetromino_names = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
        bag_size = 7
        bags = []

        while True:
            # Generate a bag with all seven tetrominoes permuted randomly
            bag = tetromino_names.copy()
            random.shuffle(bag)

            # Check for snake sequences and reshuffle if needed
            while any(bag[i] == bag[i + 1] in ['S', 'Z'] for i in range(bag_size - 1)):
                random.shuffle(bag)

            bags.append(bag)

            # Check if we have enough tetrominoes in the sequence
            if len(bags) * bag_size >= max_moves:
                sequence = [tetromino for bag in bags for tetromino in bag]
                return sequence[:max_moves] if max_moves else sequence

    def print_grid(self):
        for row in range(self.height):
            for col in range(self.width):
                print(self.grid[row][col], end=' ')
            print()


if __name__ == '__main__':
    game = TetrisGameGenerator()
    game.print_grid()
    print(game.sequence)
