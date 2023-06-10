import feast.tree as tree
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_01'
ALGORITHM_NAME = 'fixed_two-rate'

sentence = 'numeric_observable:rate'
root = tree.create(sentence)


if __name__ == '__main__':
    f = common.get_fresh_problem()
    l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
    f.attach_logger(l)
    inner_heuristic = common.get_fresh_inner_heuristic(f)
    inner_heuristic.adaptation_function = root.evaluate
    f_best, best, f = inner_heuristic.run()
    print(f"result: {f_best} as {best} using {f.state.evaluations} evaluations")
