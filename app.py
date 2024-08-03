from flask import Flask, render_template, request, jsonify
from flask_htmx import HTMX
from TetrisGameGenerator import TetrisGameGenerator
from TetrisSolver import TetrisSolver
from minimization import minimize_max_attempts
import multiprocessing
import json
import time

app = Flask(__name__)
htmx = HTMX(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.form
    goal = int(data.get('goal', 15))
    tetrominoes = int(data.get('tetrominoes', 40))
    initial_height_max = int(data.get('initialHeightMax', 7))
    num_games = int(data.get('numGames', 100))

    results = simulate_games(goal, tetrominoes, initial_height_max, num_games)

    return jsonify(results)

@app.route('/run_single_game', methods=['POST'])
def run_single_game():
    data = request.form
    seed = int(data.get('seed', 42))
    goal = int(data.get('goal', 15))
    tetrominoes = int(data.get('tetrominoes', 40))
    initial_height_max = int(data.get('initialHeightMax', 7))

    # Generate and solve a single game
    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    solver = TetrisSolver(game.board, game.sequence, goal)
    result, moves, failed_attempts = solver.solve()

    return jsonify({
        'result': result,
        'moves': moves,
        'failedAttempts': failed_attempts,
        'initialBoard': game.board.tolist(),
        'sequence': game.sequence
    })

def simulate_games(goal, tetrominoes, initial_height_max, num_games):
    start_time = time.time()
    winnable_games = 0
    total_attempts = 0

    with multiprocessing.Pool() as pool:
        results = pool.starmap(
            run_single_simulation,
            [(i, goal, tetrominoes, initial_height_max) for i in range(num_games)]
        )

    for result, attempts in results:
        if result:
            winnable_games += 1
        total_attempts += attempts

    end_time = time.time()
    total_time = end_time - start_time
    average_time = total_time / num_games

    return {
        'winnable_games': winnable_games,
        'total_games': num_games,
        'average_time': average_time,
        'average_attempts': total_attempts / num_games
    }

def run_single_simulation(seed, goal, tetrominoes, initial_height_max):
    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    solver = TetrisSolver(game.board, game.sequence, goal)
    result, _, failed_attempts = solver.solve()
    return result, failed_attempts

if __name__ == '__main__':
    app.run(debug=True)
