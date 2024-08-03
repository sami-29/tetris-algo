from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import multiprocessing
import csv

def minimize_max_attempts(attempts):
    size = len(attempts)
    best_max_attempts = 0
    best_efficiency_ratio = 0
    memo = {}

    for i in range(size):
        current_attempt_key = tuple(attempts[i].items())
        if current_attempt_key in memo or not attempts[i]["solvable"]:
            continue

        memo[current_attempt_key] = True

        max_attempts = attempts[i]["failed_attempts"] + 1
        solved = 0
        loop = max_attempts * size

        for j in range(max_attempts * size):
            current_attempt = j // size + 1
            isSolvable = True if attempts[j % size]["solvable"] and attempts[j % size]["failed_attempts"] + 1 == current_attempt else False
            solved += 1 if isSolvable else 0
            loop -= max_attempts - current_attempt if isSolvable else 0

        efficiency_ratio = solved / loop
        if efficiency_ratio > best_efficiency_ratio:
            best_efficiency_ratio = efficiency_ratio
            best_max_attempts = max_attempts

    return best_max_attempts

def solve_game(args):
    game, max_moves, test = args
    solver = TetrisSolver(game.board, game.sequence, game.goal, max_attempts=max_moves)

    result, moves, failed_attempts = solver.solve()
    if(test):
        return {
                "solvable": result,
                "failed_attempts": failed_attempts
                }


    return game if result else None

def generate_game(args):
    seed, goal, tetrominoes, initial_height_max = args
    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes,initial_height_max= initial_height_max)
    return game

if __name__ == "__main__":
    winnable_games = []
    attempts = []
    games = []

    num_processes = multiprocessing.cpu_count()
    print(f"Number of processes: {num_processes}")

    # MODIFIABLE PARAMETERS
    goal = 8
    tetrominoes = 40
    initial_height_max = 4
    start = 0
    end = 100
    # =====================

    start_loop = time()

    # Preliminary phase to find optimal max_attempts
    test_games_to_generate = 20
    test_max_attempts = 20000

    print("Starting preliminary phase to find optimal max_attempts...")
    start_minimization = time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        test_games = pool.map(generate_game, [(i, goal, tetrominoes, initial_height_max) for i in range(test_games_to_generate)])

    with multiprocessing.Pool(processes=num_processes) as pool:
        test_attempts = pool.map(solve_game, [(game, test_max_attempts, True) for game in test_games])

    max_attempts = minimize_max_attempts(test_attempts)
    print(f"Optimal max_attempts found: {max_attempts}")
    print(f"Time to find optimal max_attempts: {time() - start_minimization}")

    # Main phase
    start_game_generation = time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        games = pool.map(generate_game, [(i, goal, tetrominoes, initial_height_max) for i in range(start, end)])

    end_game_generation = time()
    print(f"Time to generate games: {end_game_generation - start_game_generation}")

    start_game_solving = time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        winnable_games = pool.map(solve_game, [(game, max_attempts, False) for game in games])
    winnable_games = [game for game in winnable_games if game is not None]
    end_game_solving = time()
    print(f"Time to solve games: {end_game_solving - start_game_solving}")

    end_loop = time()

    print("Total time: ", end_loop - start_loop)
    print("Number of winnable games: ", len(winnable_games))

    with open('log.txt', 'a') as file:
        file.write(f"The average time per winnable game for {goal}/{tetrominoes} goal/tetrominoes was {(end_loop - start_loop) / len(winnable_games)} seconds. {len(winnable_games)} games were winnable. It took {end_loop - start_loop} seconds to pass through all {len(games)} seeds. with a max_attempts of {max_attempts}.\n")

    # Create a CSV file with the winnable games and their seed | max_moves | goal | initial_height_max
    if(len(winnable_games) > 0):
        with open('winnable_games.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
            for game in winnable_games:
                writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])
