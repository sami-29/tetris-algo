import os
import multiprocessing
import time
import logging

from flask import Flask, render_template, request, jsonify
from flask_htmx import HTMX

from TetrisGameGenerator import TetrisGameGenerator
from TetrisSolver import TetrisSolver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
htmx = HTMX(app)

MAX_GAMES = 1000
MAX_TETROMINOES = 200
MAX_GOAL = 40
MAX_HEIGHT = 15
MIN_VALUE = 1


def parse_game_params(data: dict) -> dict:
    return {
        'seed': max(0, int(data.get('seed', 42))),
        'goal': min(MAX_GOAL, max(MIN_VALUE, int(data.get('goal', 8)))),
        'tetrominoes': min(MAX_TETROMINOES, max(MIN_VALUE, int(data.get('tetrominoes', 40)))),
        'initial_height_max': min(MAX_HEIGHT, max(MIN_VALUE, int(data.get('initialHeightMax', 7)))),
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')


@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        params = parse_game_params(request.form)
        num_games = min(MAX_GAMES, max(1, int(request.form.get('numGames', 100))))
        results = _simulate_games(
            params['goal'], params['tetrominoes'], params['initial_height_max'], num_games
        )
        return jsonify(results)
    except (ValueError, TypeError) as exc:
        logging.warning('Invalid simulation input: %s', exc)
        return jsonify({'error': 'Invalid input parameters.'}), 400
    except Exception as exc:
        logging.error('Simulation error: %s', exc)
        return jsonify({'error': 'Simulation failed. Please try again.'}), 500


@app.route('/run_single_game', methods=['POST'])
def run_single_game():
    try:
        params = parse_game_params(request.form)
        game = TetrisGameGenerator(
            seed=params['seed'],
            goal=params['goal'],
            tetrominoes=params['tetrominoes'],
            initial_height_max=params['initial_height_max'],
        )
        solver = TetrisSolver(game.board, game.sequence, params['goal'])
        result, moves, evaluations = solver.solve()
        return jsonify({
            'result': result,
            'moves': moves,
            'failedAttempts': evaluations,
            'initialBoard': game.board.tolist(),
            'sequence': game.sequence,
            'goal': params['goal'],
        })
    except (ValueError, TypeError) as exc:
        logging.warning('Invalid single-game input: %s', exc)
        return jsonify({'error': 'Invalid input parameters.'}), 400
    except Exception as exc:
        logging.error('Single-game error: %s', exc)
        return jsonify({'error': 'Game failed. Please try again.'}), 500


@app.route('/generate_initial_board', methods=['POST'])
def generate_initial_board():
    try:
        params = parse_game_params(request.json or {})
        game = TetrisGameGenerator(
            seed=params['seed'],
            goal=params['goal'],
            tetrominoes=params['tetrominoes'],
            initial_height_max=params['initial_height_max'],
        )
        return jsonify({'board': game.board.tolist()})
    except (ValueError, TypeError) as exc:
        logging.warning('Invalid board generation input: %s', exc)
        return jsonify({'error': 'Invalid input parameters.'}), 400


def _simulate_games(goal: int, tetrominoes: int, initial_height_max: int, num_games: int) -> dict:
    logging.info('Starting simulation: %d games', num_games)
    start = time.time()
    winnable = 0
    total_evaluations = 0

    args = [(i, goal, tetrominoes, initial_height_max) for i in range(num_games)]
    with multiprocessing.Pool() as pool:
        for result, evals in pool.imap_unordered(_run_single_simulation, args):
            if result:
                winnable += 1
            total_evaluations += evals

    elapsed = time.time() - start
    logging.info('Simulation done in %.2fs', elapsed)
    return {
        'winnable_games': winnable,
        'total_games': num_games,
        'average_time': elapsed / num_games,
        'average_attempts': total_evaluations / num_games,
        'total_time': round(elapsed, 2),
    }


def _run_single_simulation(args: tuple) -> tuple[bool, int]:
    seed, goal, tetrominoes, initial_height_max = args
    game = TetrisGameGenerator(
        seed=seed, goal=goal, tetrominoes=tetrominoes, initial_height_max=initial_height_max
    )
    solver = TetrisSolver(game.board, game.sequence, goal)
    result, _, evaluations = solver.solve()
    return result, evaluations


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)
