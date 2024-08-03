from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import multiprocessing
import csv
import logging
from flask import Flask, render_template, request, jsonify, send_file
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

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

    with multiprocessing.Pool(processes=num_processes) as pool:
        start_game_generation = time()
        games = pool.map(generate_game, [(i, goal, tetrominoes, initial_height_max) for i in range(start, end)])
        end_game_generation = time()
        logging.info(f"Time to generate games: {end_game_generation - start_game_generation:.2f} seconds")

        start_game_solving = time()
        winnable_games = pool.map(solve_game, [(game, max_attempts) for game in games])
        winnable_games = [game for game in winnable_games if game is not None]
        end_game_solving = time()
        logging.info(f"Time to solve games: {end_game_solving - start_game_solving:.2f} seconds")

    total_time = time() - start_loop
    log_results(goal, tetrominoes, max_attempts, total_time, winnable_games, len(games))
    return winnable_games

def log_results(goal, tetrominoes, max_attempts, total_time, winnable_games, total_games):
    logging.info(f"Total time: {total_time:.2f} seconds")
    logging.info(f"Number of winnable games: {len(winnable_games)}")

    with open('log.txt', 'a') as file:
        if winnable_games:
            avg_time_per_game = total_time / len(winnable_games)
            file.write(f"The average time per winnable game for {goal}/{tetrominoes} goal/tetrominoes was {avg_time_per_game:.2f} seconds. "
                       f"{len(winnable_games)} games were winnable. It took {total_time:.2f} seconds to pass through all {total_games} seeds "
                       f"with a max_attempts of {max_attempts}.\n")
        else:
            file.write(f"No winnable games found for {goal}/{tetrominoes} goal/tetrominoes. "
                       f"It took {total_time:.2f} seconds to pass through all {total_games} seeds "
                       f"with a max_attempts of {max_attempts}.\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_games():
    data = request.json
    start = int(data['start'])
    end = int(data['end'])
    goal = int(data['goal'])
    tetrominoes = int(data['tetrominoes'])
    initial_height_max = int(data['initial_height_max'])
    max_attempts = int(data['max_attempts'])

    winnable_games = run_game_generation_and_solving(start, end, goal, tetrominoes, initial_height_max, max_attempts)

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
    for game in winnable_games:
        writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])

    # Create a response with the CSV file
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='winnable_games.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)
