from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import multiprocessing
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def solve_game(args):
    game, max_moves = args
    solver = TetrisSolver(game.board, game.sequence, game.goal, max_attempts=max_moves)
    result, moves, failed_attempts = solver.solve()
    return game if result else None

def generate_game(args):
    seed, goal, tetrominoes, initial_height_max = args
    return TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)

def run_game_generation_and_solving(start, end, goal, tetrominoes, initial_height_max, max_attempts):
    num_processes = multiprocessing.cpu_count()
    logging.info(f"Number of processes: {num_processes}")

    start_loop = time()

    start_game_generation = time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        games = pool.map(generate_game, [(i, goal, tetrominoes, initial_height_max) for i in range(start, end)])

    end_game_generation = time()
    logging.info(f"Time to generate games: {end_game_generation - start_game_generation:.2f} seconds")

    start_game_solving = time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        winnable_games = pool.map(solve_game, [(game, max_attempts) for game in games])
    winnable_games = [game for game in winnable_games if game is not None]
    end_game_solving = time()
    logging.info(f"Time to solve games: {end_game_solving - start_game_solving:.2f} seconds")

    end_loop = time()

    total_time = end_loop - start_loop
    logging.info(f"Total time: {total_time:.2f} seconds")
    logging.info(f"Number of winnable games: {len(winnable_games)}")

    with open('log.txt', 'a') as file:
        if winnable_games:
            avg_time_per_game = total_time / len(winnable_games)
            file.write(f"The average time per winnable game for {goal}/{tetrominoes} goal/tetrominoes was {avg_time_per_game:.2f} seconds. "
                       f"{len(winnable_games)} games were winnable. It took {total_time:.2f} seconds to pass through all {len(games)} seeds "
                       f"with a max_attempts of {max_attempts}.\n")
        else:
            file.write(f"No winnable games found for {goal}/{tetrominoes} goal/tetrominoes. "
                       f"It took {total_time:.2f} seconds to pass through all {len(games)} seeds "
                       f"with a max_attempts of {max_attempts}.\n")

    if winnable_games:
        with open('winnable_games.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
            for game in winnable_games:
                writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])

    return winnable_games

if __name__ == "__main__":
    # MODIFIABLE PARAMETERS
    goal = 8
    tetrominoes = 40
    initial_height_max = 4
    start = 0
    end = 10000
    max_attempts = 10000
    # =====================

    winnable_games = run_game_generation_and_solving(start, end, goal, tetrominoes, initial_height_max, max_attempts)
