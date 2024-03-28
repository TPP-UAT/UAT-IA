class Prediction:
    def __init__(self, term, probability, multiplier):
        self.term = term

        # These are arrays because we can have multiple predictions for the same term
        self.probabilities = [probability.numpy()]
        self.multipliers = [multiplier]

    def add_probability(self, probability):
        self.probabilities.append(probability)

    def add_multiplier(self, multiplier):
        self.multipliers.append(multiplier)

    def get_term(self):
        return self.term

    def get_probabilities(self):
        return self.probabilities

    def get_multipliers(self):
        return self.multipliers
