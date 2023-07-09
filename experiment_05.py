import common
from feast.hyperheuristics import Topiary

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_05'
ALGORITHM_NAME = 'topiary'

problem = common.get_fresh_problem()

topiary = Topiary(
    grammar=common.get_grammar(),
    starting_symbol='NUM',
    problem=problem,
    get_fresh_inner_heuristic=common.build_two_rate_ea,
    outer_budget=common.parameters['OUTER_BUDGET'],
    trials_per_evaluation=common.parameters['OUTER_TRIALS'],
    parent_population_size=10,
    child_population_size=15,
    enforce_unique_phenotypes=True,
    survival='plus',
    must_observe=['numeric_nullary_observable:rate'],
    # random_seed=0
)
topiary.initialize_population()
topiary.run()

print("Formulas in the final population:")
for i in range(topiary.parent_population_size):
    fitness = topiary.parent_population_fitness[i]
    root = topiary.parent_population[i]
    print(f"[{fitness}]: {root.formula}")

root = topiary.parent_population[0]
print(f"Best Formula: {root.formula}")

logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

common.benchmark(common.build_two_rate_ea, problem, root.evaluate)