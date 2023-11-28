from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator



games = []
winnable_games = []
for i in range(100):
    games.append(TetrisGameGenerator(seed=i, goal=i+1, tetrominoes= i*2+10))

for game in games:
    print(game.sequence)
    solver = TetrisSolver(game.height, game.width, game.grid, game.sequence)
    result, moves, failed_attempts = solver.solve(game.goal)
    if result:
        winnable_games.append(game)


print(len(winnable_games))
# create a csv file with the winnable games and their seed | max_moves | goal | initial_height_max
import csv

with open('winnable_games.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
    for game in winnable_games:
        writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])




