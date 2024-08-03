from flask import Flask, render_template, request, send_file, jsonify
from TetrisSolver import TetrisSolver
from TetrisGameGenerator import TetrisGameGenerator
from time import time
import multiprocessing
import csv
import io
import logging
import concurrent.futures
import threading
import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def solve_game(args):
    game, max_moves = args
    try:
        solver = TetrisSolver(game.board, game.sequence, game.goal, max_attempts=max_moves)
        result, moves, failed_attempts = solver.solve()
        return game if result else None
    except Exception as e:
        logging.error(f"Error in solve_game: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def generate_game(args):
    seed, goal, tetrominoes, initial_height_max = args
    try:
        return TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    except Exception as e:
        logging.error(f"Error in generate_game: {str(e)}")
        logging.error(traceback.format_exc())
        return None

def run_game_generation_and_solving(start, end, goal, tetrominoes, initial_height_max, max_attempts):
    num_processes = multiprocessing.cpu_count()
    logging.info(f"Number of processes: {num_processes}")

    start_loop = time()
    games = []
    winnable_games = []

    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
            start_game_generation = time()
            future_to_game = {executor.submit(generate_game, (i, goal, tetrominoes, initial_height_max)): i for i in range(start, end)}
            for future in concurrent.futures.as_completed(future_to_game):
                try:
                    game = future.result()
                    if game is not None:
                        games.append(game)
                    if len(games) % 100 == 0:
                        logging.info(f"Generated {len(games)} games")
                except Exception as e:
                    logging.error(f"Error generating game: {str(e)}")
                    logging.error(traceback.format_exc())
            end_game_generation = time()
            logging.info(f"Time to generate games: {end_game_generation - start_game_generation:.2f} seconds")

            start_game_solving = time()
            future_to_solve = {executor.submit(solve_game, (game, max_attempts)): game for game in games}
            for future in concurrent.futures.as_completed(future_to_solve):
                try:
                    result = future.result()
                    if result:
                        winnable_games.append(result)
                    if len(winnable_games) % 10 == 0:
                        logging.info(f"Found {len(winnable_games)} winnable games")
                except Exception as e:
                    logging.error(f"Error solving game: {str(e)}")
                    logging.error(traceback.format_exc())
            end_game_solving = time()
            logging.info(f"Time to solve games: {end_game_solving - start_game_solving:.2f} seconds")

    except Exception as e:
        logging.error(f"Error in game generation and solving process: {str(e)}")
        logging.error(traceback.format_exc())

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
    start = int(request.form['start'])
    end = int(request.form['end'])
    goal = int(request.form['goal'])
    tetrominoes = int(request.form['tetrominoes'])
    initial_height_max = int(request.form['initial_height_max'])
    max_attempts = int(request.form['max_attempts'])

    def run_processing():
        try:
            logging.info(f"Starting processing with parameters: start={start}, end={end}, goal={goal}, tetrominoes={tetrominoes}, initial_height_max={initial_height_max}, max_attempts={max_attempts}")
            winnable_games = run_game_generation_and_solving(start, end, goal, tetrominoes, initial_height_max, max_attempts)

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["seed", "max_moves", "goal", "initial_height_max"])
            for game in winnable_games:
                writer.writerow([game.seed, game.tetrominoes, game.goal, game.initial_height_max])

            # Save CSV to file
            output.seek(0)
            with open('winnable_games.csv', 'w', newline='') as f:
                f.write(output.getvalue())

            logging.info(f'Processing complete. {len(winnable_games)} winnable games found.')
        except Exception as e:
            logging.error(f"Error in run_processing: {str(e)}")
            logging.error(traceback.format_exc())

    # Start processing in a separate thread
    thread = threading.Thread(target=run_processing)
    thread.start()

    return jsonify({
        'message': 'Processing started. Check the console for progress updates.',
        'download_url': '/download_csv'
    })

@app.route('/download_csv')
def download_csv():
    return send_file(
        'winnable_games.csv',
        mimetype='text/csv',
        as_attachment=True,
        download_name='winnable_games.csv'
    )

@app.route('/simulate', methods=['POST'])
def simulate():
    seed = int(request.form['seed'])
    goal = int(request.form['goal'])
    tetrominoes = int(request.form['tetrominoes'])
    initial_height_max = int(request.form['initial_height_max'])
    max_attempts = int(request.form['max_attempts'])

    game = generate_game((seed, goal, tetrominoes, initial_height_max))
    solver = TetrisSolver(game.board, game.sequence, game.goal, max_attempts=max_attempts)
    result, moves, failed_attempts = solver.solve()

    return jsonify({
        'result': result,
        'moves': moves,
        'failed_attempts': failed_attempts,
        'board': game.visualize_board(),
        'sequence': game.sequence
    })

if __name__ == "__main__":
    app.run(debug=True)
