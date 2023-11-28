
import logging
from random import shuffle
from collections import deque

tetromino_shapes = {
        'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
        'J': [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
        'L': [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],
        'O': [[[1, 1], [1, 1]]],
        'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
        'T': [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],
        'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]
}


class TetrisSolver:
    def __init__(self, height, width, board, sequence, goal):
        self.height = height
        self.width = width
        self.board = board
        self.sequence = sequence
        self.lines_cleared = 0
        self.stack = []
        self.failed_attempts = 0
        self.goal = goal


    def rotate_tetromino(self, tetromino, rotation):
        return tetromino[rotation % len(tetromino)]

    def is_valid_move(self, tetromino, row, col):
        for i, r in enumerate(tetromino):
            for j, element in enumerate(r):
                if element and (
                        row + i >= self.height or
                        not (0 <= col + j < self.width) or
                        self.board[row + i][col + j]
                ):
                    return False

        return True

    def place_tetromino(self, tetromino, row, col):

        while self.is_valid_move(tetromino, row + 1, col):
            row += 1

        for i in range(len(tetromino)):
            for j in range(len(tetromino[0])):
                if tetromino[i][j]:
                    self.board[row + i][col + j] = 1


        self.clear_lines()

    def clear_lines(self):
        lines_cleared = 0
        for row in range(self.height):
            if all(self.board[row]):
                lines_cleared += 1
                self.board = [[0]*self.width] + self.board[:row] + self.board[row+1:]
        self.lines_cleared += lines_cleared

        self.board += [[0] * self.width] * lines_cleared


    def visualize(self, board=None):
        if board is None:
            board = self.board

        board_str = ''
        for row in range(self.height):
            for col in range(self.width):
                board_str += str(board[row][col]) + ' '
            board_str += '\n'
        return board_str

    def is_game_over(self):
        return any(self.board[0][col] == 1 for col in range(self.width))

    def solve(self, current = None):
        current = current if current else self.sequence.pop(0)
        shape = tetromino_shapes[current]

        for rotation in range(len(current)):
            for col in range(self.width):
                boardcopy = [row[:] for row in self.board]
                print("Current:", current, "Rotation:", rotation, "Col:", col)
                current_iteration_lines_cleared = self.lines_cleared
                if self.is_valid_move(shape[rotation], 0, col):
                    self.place_tetromino(shape[rotation], 0, col)

                    print("Board after placing tetromino:")
                    print("Lines cleared:", self.lines_cleared)
                    print(self.visualize())
                else:
                    continue

                if self.is_game_over():
                    self.board = boardcopy
                    self.failed_attempts += 1
                    continue
                elif self.lines_cleared >= self.goal:
                    self.stack.append((current, rotation, col))
                    return True, self.stack, self.failed_attempts
                elif self.sequence:
                    self.stack.append((current, rotation, col))
                    next_tetromino = self.sequence.pop(0)
                    result, stack, attempts = self.solve(next_tetromino)
                    if result:
                        return True, stack, attempts  # Propagate the success
                    # If the current sequence didn't lead to success, backtrack
                    self.sequence.insert(0, next_tetromino)
                    self.stack.pop()
                    self.board = boardcopy
                else:
                    self.board = boardcopy
                    self.lines_cleared = current_iteration_lines_cleared
                    self.failed_attempts += 1
                if(rotation == len(current) - 1 and col == self.width - 1):
                    self.stack.pop()
                    self.sequence.insert(0, current)


        return False, self.stack, self.failed_attempts

    def test(self, tetrominoes, positions):
        positions = deque(positions)
        for tetromino in tetrominoes:
            col = positions.popleft()

            self.place_tetromino(tetromino, 0, col)
            if(self.is_game_over()):
                return False
            board = self.board.copy()
            self.visualize(board)

        lines_cleared = self.lines_cleared
        self.lines_cleared = 0
        self.board = [[0] * self.width for _ in range(self.height)]
        return lines_cleared


# Example usage:
height, width = 20, 10
goal_lines = 1
max_moves = 20

board = [[0] * width for _ in range(height)]


sequence = ['I','I','I','I']

print("Sequence:", sequence)

logging.basicConfig(level=logging.INFO)
solver = TetrisSolver(height, width, board, sequence, goal_lines)

result, moves, failed_attempts = solver.solve()

print("Result:", result)
print("Moves:", moves)
print("Failed attempts:", failed_attempts)
print("Lines cleared:", solver.lines_cleared)



