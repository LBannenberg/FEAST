from ioh import get_problem, ProblemClass
from metaheuristics.tworate import TwoRateEa
import random

# Inner problem settings
PROBLEM_TYPE = 1  # OneMax
INSTANCE_ID = 1
DIMENSION = 16
PROBLEM_CLASS = ProblemClass.PBO
INNER_BUDGET = 10000

# Heuristic parameters
CHILD_POP_SIZE = DIMENSION

# Outer problem settings
OUTER_BUDGET = 1000  # each outer run consumes a full inner budget


def original_adaptation(is_low_mutant: bool, rate: float, dimension: int):
    s = 0.75 if is_low_mutant else 0.25
    return max(rate / 2, 2) if random.random() <= s else min(2 * rate, dimension / 4)


if __name__ == '__main__':
    f = get_problem(PROBLEM_TYPE, INSTANCE_ID, DIMENSION, PROBLEM_CLASS)
    original_heuristic = TwoRateEa(
        problem=f,
        dimension=DIMENSION,
        budget=INNER_BUDGET,
        child_pop_size=CHILD_POP_SIZE,
        adaptation_function=original_adaptation,
    )
    result = original_heuristic.run()
    print(f"result: {result}")
