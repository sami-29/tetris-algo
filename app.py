from flask import Flask, render_template, request, jsonify
from TetrisGameGenerator import TetrisGameGenerator
from TetrisSolver import TetrisSolver
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_game():
    data = request.json
    seed = int(data['seed'])
    goal = int(data['goal'])
    tetrominoes = int(data['tetrominoes'])
    initial_height_max = int(data['initial_height_max'])

    game = TetrisGameGenerator(seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max)
    
    return jsonify({
        'board': game.board.tolist(),
        'sequence': game.sequence
    })

@app.route('/solve', methods=['POST'])
def solve_game():
    data = request.json
    board = np.array(data['board'])
    sequence = data['sequence']
    goal = int(data['goal'])
    max_attempts = int(data['max_attempts'])

    solver = TetrisSolver(board, sequence, goal, max_attempts=max_attempts)
    result, moves, failed_attempts = solver.solve()

    return jsonify({
        'result': result,
        'moves': moves,
        'failed_attempts': failed_attempts
    })

if __name__ == '__main__':
    app.run(debug=True)
