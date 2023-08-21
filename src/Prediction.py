class Prediction:
    def __init__(self, term, probability, multiplier):
        self.term = term
        self.probability = probability
        self.multiplier = multiplier

    def get_term(self):
        return self.term

    def get_probability(self):
        return self.probability

    def get_multiplier(self):
        return self.multiplier
