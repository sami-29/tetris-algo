from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import cProfile

games = []
winnable_games = []
for i in range(500):
    games.append(TetrisGameGenerator(seed=i, goal=5, tetrominoes=30))

# profiler = cProfile.Profile()
# profiler.enable()

for game in games:
    print(game.sequence)
    now = time()
    solver = TetrisSolver(game.board, game.sequence, game.goal)
    result, moves, failed_attempts = solver.solve()
    print("Moves: ", moves)
    print("Time: ", time() - now)
    if result:
        winnable_games.append(game)
        print("Winnable game found")

# profiler.disable()
# profiler.print_stats(sort='cumulative')

print(len(winnable_games))
# create a csv file with the winnable games and their seed | max_moves | goal | initial_height_max
import csv

with open('winnable_games.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
    for game in winnable_games:
        writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])




