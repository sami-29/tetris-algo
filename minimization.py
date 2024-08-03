import numpy as np
from db_operations import get_cached_max_attempts, cache_max_attempts

def minimize_max_attempts(attempts, goal, tetrominoes, initial_height_max):
    params = {
        'goal': goal,
        'tetrominoes': tetrominoes,
        'initial_height_max': initial_height_max
    }
    
    cached_result = get_cached_max_attempts(params)
    if cached_result is not None:
        return cached_result

    size = len(attempts)
    max_attempts_range = range(1, max(attempt["failed_attempts"] for attempt in attempts) + 2)
    
    best_max_attempts = 0
    best_efficiency_score = 0

    for max_attempts in max_attempts_range:
        solved = sum(1 for attempt in attempts if attempt["solvable"] and attempt["failed_attempts"] < max_attempts)
        total_attempts = sum(min(max_attempts, attempt["failed_attempts"] + 1) for attempt in attempts)
        
        efficiency_score = (solved ** 2) / total_attempts
        
        if efficiency_score > best_efficiency_score:
            best_efficiency_score = efficiency_score
            best_max_attempts = max_attempts

    cache_max_attempts(params, best_max_attempts)
    return best_max_attempts




if __name__ == "__main__":
    example_attempts = [
        {"solvable": True, "failed_attempts": 0},
        {"solvable": True, "failed_attempts": 0},
        {"solvable": True, "failed_attempts": 1},
        {"solvable": True, "failed_attempts": 1},
        {"solvable": True, "failed_attempts": 1},
        {"solvable": True, "failed_attempts": 2},
        {"solvable": True, "failed_attempts": 999},
        {"solvable": False, "failed_attempts": 1000},
    ]

    result = minimize_max_attempts(example_attempts)
    print(f"Best max_attempts: {result}")
