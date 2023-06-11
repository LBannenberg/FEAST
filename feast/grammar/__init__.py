import json
import random


class Grammar:
    def __init__(self, observable_declaration):
        if 'num' in observable_declaration and len(observable_declaration['num']):
            self.productions['NUMERIC_OBSERVABLE'] = [
                ['numeric_observable:' + name for name in observable_declaration['num']]
            ]
            self.productions['NUMERIC_EXPRESSION'].append(['NUMERIC_OBSERVABLE'])

        if 'boolean' in observable_declaration and len(observable_declaration['boolean']):
            self.productions['BOOLEAN_OBSERVABLE'] = [
                ['boolean_observable:' + name for name in observable_declaration['boolean']]
            ]
            self.productions['BOOLEAN_EXPRESSION'].append(['BOOLEAN_OBSERVABLE'])

    def __repr__(self):
        return json.dumps(self.productions, sort_keys=False, indent=2)

    def produce_random_sentence(self, soft_limit=10, starting_symbol='START'):
        terminals = []
        non_terminals = [starting_symbol]  # use BOOLEAN_EXPRESSION or NUMERIC_EXPRESSION to force the type

        while len(non_terminals):
            symbol = non_terminals[0]

            # Detect when we're making an overly large tree
            # We're allowed to duck over and under the limit for non-terminals, to reduce bias to left-large trees
            # When we have too many terminals, we have to make the limit permanent
            limit_triggered = len(non_terminals) > soft_limit
            if len(terminals) > soft_limit * 10:
                limit_triggered = True

            # If limited, bound the size of the tree by only making leaves
            if limit_triggered and symbol == 'NUMERIC_EXPRESSION':
                symbol = 'NUMERIC'
            if limit_triggered and symbol == 'BOOLEAN_EXPRESSION':
                symbol = 'BOOLEAN'

            options = self.productions[symbol]
            choice = options[random.randint(0, len(options) - 1)]
            non_terminals, terminals = self._produce(choice, non_terminals, terminals)
        return '|'.join(terminals)

    def produce_from_genome(self, genome, wraparound=0, starting_symbol='START', return_coding_length=False):
        terminals = []
        non_terminals = [starting_symbol]  # use BOOLEAN_EXPRESSION or NUMERIC_EXPRESSION to force the type
        gene = 0
        wraps = 0

        while len(non_terminals):
            if gene >= len(genome):
                if (
                        wraparound == 0  # no wrap
                        or (0 < wraparound <= wraps)  # exhausted wraps
                ):
                    break
                gene = 0
                wraps += 1
            symbol = non_terminals[0]
            options = self.productions[symbol]
            index = genome[gene] % len(options)
            choice = options[index]  # map gene to production
            non_terminals, terminals = self._produce(choice, non_terminals, terminals)
            gene += 1

        sentence = 'invalid' if len(non_terminals) else '|'.join(terminals)

        if return_coding_length:
            coding_length = len(genome) if wraps else gene
            return sentence, coding_length

        # complete valid derivation
        return sentence

    def _produce(self, choice, non_terminals, terminals):
        new_terminals = []
        new_non_terminals = []
        for s in choice:
            if s in self.productions.keys():
                new_non_terminals.append(s)
            else:
                new_terminals.append(s)
        terminals = terminals + new_terminals
        non_terminals = new_non_terminals + non_terminals[1:]
        return non_terminals, terminals

    productions = {
        'START': [
            ['NUMERIC_EXPRESSION'],
            ['BOOLEAN_EXPRESSION'],
        ],
        'NUMERIC_EXPRESSION': [
            ['NUMERIC'],
            # ['NUMERIC_OBSERVABLE'],  # added during __init__ if any names are passed
            ['NUMERIC_BINARY_EXPRESSION'],
            ['if:numeric', 'BOOLEAN_EXPRESSION', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['numeric_expression:negative', 'NUMERIC_EXPRESSION']
        ],
        'NUMERIC': [['numeric:' + str(num)]
                    for num in [-1, -0.5, 0, 0.1, 0.5, 1, 2, 3, 4, 5, 10, 20, 50, 100, 'uniform']
                    ],
        # 'NUMERIC_OBSERVABLE': [],  # added during __init__ if any names are passed
        'NUMERIC_BINARY_EXPRESSION': [
            ['numeric_expression:+', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['numeric_expression:-', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['numeric_expression:*', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['numeric_expression:/', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            # ['numeric_expression:%', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            # ['numeric_expression:^', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['numeric_expression:min', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['numeric_expression:max', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION']
        ],
        'BOOLEAN_EXPRESSION': [
            ['BOOLEAN'],
            # ['BOOLEAN_OBSERVABLE'],  # added during __init__ if any names are passed
            ['BOOLEAN_BINARY_EXPRESSION'],
            ['if:boolean', 'BOOLEAN_EXPRESSION', 'BOOLEAN_EXPRESSION', 'BOOLEAN_EXPRESSION'],
            ['boolean_expression:not', 'BOOLEAN_EXPRESSION'],
            ['boolean_expression:truthy', 'NUMERIC_EXPRESSION']
        ],
        'BOOLEAN': [['boolean:true'], ['boolean:false']],
        # 'BOOLEAN_OBSERVABLE': [],  # added during __init__ if any names are passed
        'BOOLEAN_BINARY_EXPRESSION': [
            ['boolean_expression:and', 'BOOLEAN_EXPRESSION', 'BOOLEAN_EXPRESSION'],
            ['boolean_expression:or', 'BOOLEAN_EXPRESSION', 'BOOLEAN_EXPRESSION'],
            ['boolean_expression:>', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['boolean_expression:>=', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['boolean_expression:==', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['boolean_expression:<=', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['boolean_expression:<', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION'],
            ['boolean_expression:!=', 'NUMERIC_EXPRESSION', 'NUMERIC_EXPRESSION']
        ]
    }
