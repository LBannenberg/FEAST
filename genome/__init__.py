import random


class Genome:
    def __init__(self, length, codon_size=10000):
        self.length = length
        self.codon_size = codon_size
        self.genotype = []

    def __repr__(self):
        return ','.join([str(gene) for gene in self.genotype])

    def initialize_randomly(self):
        self.genotype = [random.randint(0, self.codon_size - 1) for i in range(self.length)]
