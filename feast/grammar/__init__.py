import json
import random
from typing import Union, List, Tuple


class Grammar:
    def __init__(self, wraparound: int = 0, grammar_definition: str = 'feast/grammar/mixed.json'):
        self.wraparound = wraparound
        with open(grammar_definition) as f:
            self.productions = json.load(f)
        self.reductions = self._prepare_reductions()

    def __repr__(self) -> str:
        return json.dumps(self.productions, sort_keys=False, indent=2)

    def produce_random_sentence(self, starting_symbol: str, soft_limit: int = 10) -> str:
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
            if limit_triggered and symbol in ['NUM', 'NUM_BINARY_OPERATOR', 'NUM_COND']:
                symbol = 'NUM_CONSTANT'
            if limit_triggered and symbol == ['BOOL', 'BOOL_BINARY_OPERATOR', 'BOOL_COND']:
                symbol = 'BOOL_CONSTANT'

            options = self.productions[symbol]
            choice = options[random.randint(0, len(options) - 1)]
            non_terminals, terminals = self._produce(choice, non_terminals, terminals)
        return '|'.join(terminals)

    def get_genome_coding_length(self, genome: List[int], starting_symbol: str) -> int:
        _, coding_length = self._produce_from_genome(genome, starting_symbol=starting_symbol)
        return coding_length

    def get_sentence_from_genome(self, genome: List[int], starting_symbol: str) -> str:
        sentence, _ = self._produce_from_genome(genome, starting_symbol=starting_symbol)
        return sentence

    def _produce_from_genome(self, genome: List[int], starting_symbol: str) -> Tuple[str, int]:
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

    def _produce(self, choice: List[str], non_terminals: List[str], terminals: List[str]) -> Tuple[list, list]:
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

    @property
    def terminals(self) -> List[str]:
        terminals = set()
        for _, productions in self.productions.items():
            for production in productions:
                for symbol in production:
                    if symbol not in self.non_terminals:
                        terminals.add(symbol)
        return list(terminals)

    @property
    def non_terminals(self) -> list:
        return list(self.productions.keys())

    def get_alternative_terminal(self, terminal: str) -> Union[str, None]:
        non_terminal = self.reductions[terminal]
        alternatives = [rule for rule in self.productions[non_terminal] if terminal not in rule]
        if len(alternatives) == 0:
            return None
        choice = random.randint(0, len(alternatives) - 1)
        return alternatives[choice][0]

    def _prepare_reductions(self) -> dict:
        reductions = {}
        for non_terminal, rules in self.productions.items():
            for rule in rules:
                symbol = rule[0]  # because we use prefix notation
                reductions[symbol] = non_terminal
        return reductions

    def get_reduction_to_type_non_terminal(self, terminal: str) -> str:
        reduction = self.reductions[terminal]
        if reduction not in ['NUM', 'BOOL']:
            reduction = self.reductions[reduction]
        return reduction
