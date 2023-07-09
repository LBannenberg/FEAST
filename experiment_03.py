import common
from feast.hyperheuristics import RandomSearch

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_03'
ALGORITHM_NAME = 'random-search-1+1'

problem = common.get_fresh_problem()

random_search = RandomSearch(
    grammar=common.get_grammar(),
    starting_symbol='NUM',
    problem=problem,
    get_fresh_inner_heuristic=common.build_two_rate_ea,
    outer_budget=common.parameters['OUTER_BUDGET'],
    trials_per_evaluation=common.parameters['OUTER_TRIALS'],
    must_observe=['numeric_nullary_observable:rate'],
)

random_search.initialize_population()
random_search.run()

root = random_search.parent_population[0]
print(f"Best Formula: {root.formula}")

logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

common.benchmark(common.build_two_rate_ea, problem, root.evaluate)
