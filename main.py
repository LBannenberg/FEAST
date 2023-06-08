from tree import Root
from grammar import Grammar
from genome import Genome

genome_length = 10
codon_size = 10000
wraparound = 3

observables_declaration = {'boolean': ['boolly'], 'numeric': ['nummy']}

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    grammar = Grammar(observable_declaration=observables_declaration)
    # print(grammar)
    genome = Genome(genome_length, codon_size=codon_size)
    invalid = True
    tries = 0
    while invalid:
        tries += 1
        genome.initialize_randomly()
        sentence = grammar.produce_from_genome(genome.genotype,
                                               initial_symbol='NUMERIC_EXPRESSION',
                                               wraparound=wraparound)
        sentence = grammar.produce_random_sentence()
        invalid = sentence == 'invalid'
        print(f"try {tries} valid: {not invalid}")
    print(sentence)

    tree = Root()
    tree.inflate(sentence)
    print(tree)

    observables = {
        'boolly': True,
        'nummy': 3
    }
    print(tree.evaluate(observables))

    print(tree.deflate())
    print(f"Correctly deflated: {sentence == tree.deflate()}")
