from typing import Callable

import numpy as np
from ioh import ProblemClass, get_problem, logger, ProblemType

from metaheuristics.base import Heuristic
from metaheuristics.tworate import TwoRateEa
import os
from feast.grammar import Grammar

parameters = {
    'OUTPUT_DIR': 'experiment_output/',

    # 'PROBLEM_TYPE': 1,  # OneMax,
    'PROBLEM_TYPE': 19,  # Ising,
    'INSTANCE_ID': 1,
    'DIMENSION': 16,
    'PROBLEM_CLASS': ProblemClass.PBO,

    'INNER_BUDGET': 5000,
    'OUTER_BUDGET': 500,
    'OUTER_TRIALS': 5,
    'BENCHMARK_RUNS': 10
}

parameters['CHILD_POP_SIZE'] = parameters['DIMENSION']


def get_fresh_problem():
    return get_problem(
        parameters['PROBLEM_TYPE'],
        parameters['INSTANCE_ID'],
        parameters['DIMENSION'],
        parameters['PROBLEM_CLASS']
    )


def get_fresh_inner_heuristic(problem: ProblemType, injection):
    heuristic = TwoRateEa(parameters['CHILD_POP_SIZE'])
    heuristic.configure(
        problem,
        parameters['INNER_BUDGET'],
        injection
    )


def build_two_rate_ea(problem: ProblemType, individual_evaluate) -> Heuristic:
    heuristic = TwoRateEa(parameters['CHILD_POP_SIZE'])
    heuristic.configure(
        problem,
        parameters['INNER_BUDGET'],
        {'adaptation': individual_evaluate}
    )
    heuristic.initialize_population()
    return heuristic


def get_logger(experiment_name, algorithm_name):
    l = logger.Analyzer(
        root=os.getcwd(),  # Store data in the current working directory
        folder_name=experiment_name,  # in a folder named: 'my-experiment'
        algorithm_name=algorithm_name,  # meta-data for the algorithm used to generate these results
        store_positions=True  # store x-variables in the logged files
    )
    return l


def get_grammar():
    return Grammar()


def benchmark(metaheuristic_builder: Callable, problem: ProblemType, solution: Callable):
    performance = []
    for i in range(parameters['BENCHMARK_RUNS']):
        inner_heuristic = metaheuristic_builder(problem, solution)
        y_best, x_best, problem = inner_heuristic.run()

        leftover_budget = inner_heuristic.budget - problem.state.evaluations
        leftover_ratio = leftover_budget / inner_heuristic.budget
        score = y_best + leftover_ratio  # leftover budget ratio is a tiebreaker

        performance.append(score)

        print(f"result: {y_best} as {x_best} using {problem.state.evaluations} evaluations")
        problem.reset()

    print(f"Aggregate score: {np.mean(performance)}")

