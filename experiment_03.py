from feast.grammar import Grammar
import feast.tree as tree
import math
import common

# Logger settings
EXPERIMENT_NAME = common.parameters['OUTPUT_DIR'] + 'experiment_02'
ALGORITHM_NAME = 'random-search-1+1'



def train(grammar):
    lowest_evaluations = math.inf
    best_recipe = None
    for i in range(common.parameters['OUTER_BUDGET']):
        recipe = grammar.produce_random_sentence(soft_limit=5, initial_symbol='NUMERIC_EXPRESSION')
        root = tree.create(recipe)

        print(f"Generation {i}")
        print(f"  Formula: {root.formula}")
        print(f"  Static?: {'yes' if root.is_static else 'no'}")
        def adaptation(observables):
            return root.evaluate(observables)

        f = common.get_fresh_problem()
        inner_heuristic = common.get_fresh_inner_heuristic(f)
        inner_heuristic.adaptation_function = adaptation
        f_best, best, f = inner_heuristic.run()
        if f.state.evaluations < lowest_evaluations:
            lowest_evaluations = f.state.evaluations
            best_recipe = recipe
        print(f"  lowest: {lowest_evaluations}, current: {f.state.evaluations}")

    return best_recipe


if __name__ == '__main__':
    observables_declaration = {'boolean': ['best_child_is_low'], 'numeric': ['rate', 'dimension']}
    grammar = Grammar(observable_declaration=observables_declaration)
    best_recipe = train(grammar)
    root = tree.create(best_recipe)

    def adaptation(observables):
        return root.evaluate(observables)

    f = common.get_fresh_problem()
    l = common.get_logger(EXPERIMENT_NAME, ALGORITHM_NAME)
    f.attach_logger(l)

    inner_heuristic = common.get_fresh_inner_heuristic(f)
    inner_heuristic.adaptation_function = adaptation
    f_best, best, f = inner_heuristic.run()
    print(f"result: {f_best} as {best} using {f.state.evaluations} evaluations")
