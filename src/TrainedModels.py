class TrainedModels:
    def __init__(self):
        self.models = {}

    # Getters
    def get_by_id(self, term_id):
        return self.models.get(term_id, None)

    def add_model_for_term_children(self, term_id, model):
        self.models[term_id] = model

