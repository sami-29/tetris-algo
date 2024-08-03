from flask import Flask, render_template, request, jsonify
from flask_htmx import HTMX
from TetrisGameGenerator import TetrisGameGenerator
from TetrisSolver import TetrisSolver
from minimization import minimize_max_attempts
import multiprocessing
import json

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

    # Run the simulation (this is a placeholder, implement the actual simulation logic)
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
    # Implement the simulation logic here
    # This is a placeholder, replace with actual implementation
    return {
        'winnable_games': num_games // 2,
        'total_games': num_games,
        'average_time': 0.5
    }

if __name__ == '__main__':
    app.run(debug=True)
