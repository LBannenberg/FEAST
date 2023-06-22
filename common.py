from ioh import ProblemClass, get_problem, logger
from metaheuristics.tworate import TwoRateEa
import os
from feast.grammar import Grammar

parameters = {
    'OUTPUT_DIR': 'experiment_output/',

    'PROBLEM_TYPE': 1,  # OneMax,
    'INSTANCE_ID': 1,
    'DIMENSION': 16,
    'PROBLEM_CLASS': ProblemClass.PBO,

    'INNER_BUDGET': 1000,
    'OUTER_BUDGET': 100,
    'OUTER_TRIALS': 3
}

parameters['CHILD_POP_SIZE'] = parameters['DIMENSION']


def get_fresh_problem():
    return get_problem(
        parameters['PROBLEM_TYPE'],
        parameters['INSTANCE_ID'],
        parameters['DIMENSION'],
        parameters['PROBLEM_CLASS']
    )


def get_fresh_inner_heuristic(f):
    return TwoRateEa(
        problem=f,
        dimension=parameters['DIMENSION'],
        budget=1000,
        child_pop_size=16
    )


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
