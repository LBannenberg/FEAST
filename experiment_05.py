import feast.tree as tree
import common
import json

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_05'
ALGORITHM_NAME = 'fixed_two-rate'

sentence = 'numeric_expression:negative|numeric_expression:+|numeric_observable:rate|numeric_expression:*|numeric:1|numeric:2'
root = tree.create(sentence)

# f = common.get_fresh_problem()
# l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
# f.attach_logger(l)
# inner_heuristic = common.get_fresh_inner_heuristic(f)
# inner_heuristic.inject_function(root.evaluate)
# y_best, x_best, f = inner_heuristic.run()
# print(f"result: {y_best} as {x_best} using {f.state.evaluations} evaluations")


# print(json.dumps(root.collect_index(), sort_keys=True, indent=4))
print(root.serialize())
root.alter_node_value('0.0', '-')
print(root.serialize())
root.graft_new_subtree('0.0.0', 'numeric_expression:*|numeric:3|numeric:5')
print(root.serialize())