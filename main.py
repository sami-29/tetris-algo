from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import cProfile

games = []
winnable_games = []
for i in range(50):
    games.append(TetrisGameGenerator(seed=i, goal=8, tetrominoes=50))

# profiler = cProfile.Profile()
# profiler.enable()

start_loop = time()
for game in games:
    print(game.sequence)
    now = time()
    solver = TetrisSolver(game.board, game.sequence, game.goal, 10000000)
    result, moves, failed_attempts = solver.solve()
    print("Moves: ", moves)
    print("Time: ", time() - now)

    if result:
        winnable_games.append(game)
        print("Winnable game found")

end_loop = time()
print("Total time: ", end_loop - start_loop)

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
