import common
from feast.hyperheuristics import GE

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_04'
ALGORITHM_NAME = 'classic-GE'

problem = common.get_fresh_problem()

ge = GE(
    common.get_grammar(),
    'NUM',
    problem=problem,
    build_inner_heuristic=common.build_two_rate_ea,
    outer_budget=common.parameters['OUTER_BUDGET'],
    trials_per_evaluation=common.parameters['OUTER_TRIALS'],
    parent_population_size=10,
    child_population_size=1,
    mutation_probability=0.5,
    crossover_probability=0.5,
    genome_length=50,
    enforce_unique_genotypes=True,
    enforce_unique_phenotypes=False,
    enforce_unique_coding_genotypes=False,
    survival='plus',
    cache_phenotype_evaluations=False,
    must_observe=['numeric_nullary_observable:rate'],
    # random_seed=1
)
ge.initialize_population()
ge.run()

print("Formulas in the final population:")
for i in range(ge.parent_population_size):
    fitness = ge.parent_population_fitness[i]
    root = ge.get_individual(i)
    print(f"[{fitness}]: {root.formula}")

root = ge.get_individual(0)
print(f"Best Formula: {root.formula}")

logger = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
problem.attach_logger(logger)

common.benchmark(common.build_two_rate_ea, problem, root.evaluate)