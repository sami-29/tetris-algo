def minimize_max_attempts(attempts):
    size = len(attempts)
    best_max_attempts = 0
    best_efficiency_ratio = 0
    memo = {}

    for i in range(size):
        # Convert the dictionary to a hashable type (tuple) before using it as a key in memo
        current_attempt_key = tuple(attempts[i].items())
        if current_attempt_key in memo or not attempts[i]["solvable"]:
            continue

        memo[current_attempt_key] = True

        max_attempts = attempts[i]["failed_attempts"] + 1
        solved = 0
        loop = max_attempts * size

        for j in range(max_attempts * size):
            # the current attempt is basically if j is from 0-size we are at attempt 1 from size- 2*size we are at attempt 2 etc
            current_attempt = j // size + 1
            isSolvable = True if attempts[j % size]["solvable"] and attempts[j % size]["failed_attempts"] + 1 == current_attempt else False
            solved += 1 if isSolvable else 0
            loop -= max_attempts - current_attempt if isSolvable else 0


        efficiency_ratio = solved / loop

        # if the efficiency ratio is better than the best one we update the best one and the best max attempts
        if efficiency_ratio > best_efficiency_ratio:
            best_efficiency_ratio = efficiency_ratio
            best_max_attempts = max_attempts

    return best_max_attempts




if __name__ == "__main__":
    # Example usage:
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
