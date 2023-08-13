class Prediction:
    def __init__(self, term, probability, input_training):
        self.term = term
        self.probability = probability
        self.input_training = input_training

    def get_term(self):
        return self.term

    def get_probability(self):
        return self.probability

    def get_input_training(self):
        return self.input_training
