from keras.models import Sequential

class TrainedModels:
    def __init__(self):
        self.models = {}

    # Getters
    def get_models(self):
        return self.models

    def get_by_id(self, term_id):
        return self.models.get(term_id, None)

    # Setters
    def add_model_for_term_children(self, term_id, model: Sequential):
        self.models[term_id] = model

