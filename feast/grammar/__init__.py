import json
import random


class Grammar:
    def __init__(self, observable_declaration, wraparound=0, grammar_definition='feast/grammar/mixed.json'):
        with open(grammar_definition) as f:
            rules = json.load(f)
        self.wraparound = wraparound
        if 'numeric' in observable_declaration and len(observable_declaration['numeric']):
            rules['NUMERIC_OBSERVABLE'] = [
                ['numeric_observable:' + name for name in observable_declaration['numeric']]
            ]
            rules['NUMERIC_EXPRESSION'].append(['NUMERIC_OBSERVABLE'])

        if 'boolean' in observable_declaration and len(observable_declaration['boolean']):
            rules['BOOLEAN_OBSERVABLE'] = [
                ['boolean_observable:' + name for name in observable_declaration['boolean']]
            ]
            rules['BOOLEAN_EXPRESSION'].append(['BOOLEAN_OBSERVABLE'])
        self.productions = rules

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

    def get_genome_coding_length(self, genome, starting_symbol):
        _, coding_length = self._produce_from_genome(genome, starting_symbol=starting_symbol)
        return coding_length

    def get_sentence_from_genome(self, genome, starting_symbol):
        sentence, _ = self._produce_from_genome(genome, starting_symbol=starting_symbol)
        return sentence

    def _produce_from_genome(self, genome, starting_symbol):
        terminals = []
        non_terminals = [starting_symbol]  # use BOOLEAN_EXPRESSION or NUMERIC_EXPRESSION to force the type
        gene = 0
        wraps = 0

        while len(non_terminals):
            if gene >= len(genome):
                if (
                        self.wraparound == 0  # no wrap
                        or (0 < self.wraparound <= wraps)  # exhausted wraps
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

        sentence = '|'.join(terminals)
        if len(non_terminals):
            raise ValueError(f"Cannot finish derivation. So far: {sentence}")

        coding_length = len(genome) if wraps else gene
        return sentence, coding_length

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

