from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import multiprocessing
import csv
from minimization import minimize_max_attempts

def solve_game(args):
    game, max_moves, test = args
    solver = TetrisSolver(game.board, game.sequence, game.goal, max_attempts=max_moves)

    result, moves, failed_attempts = solver.solve()

    # write to attempts.csv if test is True

    with open('attempts.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # write header
        if test:
            writer.writerow(["seed", "tetrominoes", "goal", "initial_height_max", "max_moves", "failed_attempts", "solvable"])
        writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max, max_moves, failed_attempts, result])

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

def get_max_attempts_from_csv(goal, tetrominoes, initial_height_max):
    try:
        with open('best_max_attempts.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if int(row[1]) == goal and int(row[2]) == tetrominoes and int(row[3]) == initial_height_max:
                    return int(row[4])
    except FileNotFoundError:
        pass
    return None


if __name__ == "__main__":
    winnable_games = []
    attempts = []
    games = []
    goal = 10
    tetrominoes = 50
    initial_height_max = 7
    num_processes = multiprocessing.cpu_count()
    print(f"Number of processes: {num_processes}")
    test_games_to_generate = 0
    games_to_generate = 1000000


    start_loop = time()

    start_minimization = time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        games = pool.map(generate_game, [(i, goal, tetrominoes, initial_height_max) for i in range(0, test_games_to_generate)])

    max_attempts = get_max_attempts_from_csv(goal, tetrominoes, initial_height_max)

    if max_attempts is None:
        max_attempts = 100
        start_minimization = time()

        with multiprocessing.Pool(processes=num_processes) as pool:
            attempts = pool.map(solve_game, [(game, max_attempts, True) for game in games])

        max_attempts = minimize_max_attempts(attempts)
        print(f"Best max_attempts: {max_attempts}")
        print(f"Time to minimize max_attempts: {time() - start_minimization}")

        # Save the max_attempts in best_max_attempts.csv
        with open('best_max_attempts.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([goal, tetrominoes, initial_height_max, max_attempts])

    start_game_generation = time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        games += pool.map(generate_game, [(i, goal, tetrominoes, initial_height_max) for i in range(test_games_to_generate, games_to_generate)])

    end_game_generation = time()
    print(f"Time to generate games: {end_game_generation - start_game_generation}")


    start_game_solving = time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        winnable_games = pool.map(solve_game, [(game, 1, False) for game in games])
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
        with open('winnable_games.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
            for game in winnable_games:
                writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])
