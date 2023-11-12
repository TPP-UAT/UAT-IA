import os
import glob
import json
import tensorflow as tf
from TrainedModels import TrainedModels
from TermPrediction import TermPrediction
from utils.articles_parser import get_abstract_from_file

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator

NORMAL_TRAIN = 0.55
TFIDF_TRAIN = 0.45
ABSTRACT_TRAIN = 0.5

class Predictor:
    def __init__(self, initial_term_id, thesaurus):
        self.initial_term_id = initial_term_id
        self.thesaurus = thesaurus

    def get_prediction_multiplier(self, input_creator):
        if isinstance(input_creator, NormalInputCreator):
            return NORMAL_TRAIN
        elif isinstance(input_creator, TFIDFInputCreator):
            return TFIDF_TRAIN
        elif isinstance(input_creator, AbstractInputCreator):
            return ABSTRACT_TRAIN
        else:
            return 0

    ''' Load methods '''
    def load_keywords_by_term(self):
        file = open("./data/keywords-by-term.json", "r")
        keywords_by_term = file.read()
        keywords_by_term = json.loads(keywords_by_term)
        file.close()
        return keywords_by_term

    def load_trained_models(self):
        models = {}
        for model_path in glob.glob("./models/*.keras"):
            term_id = os.path.basename(model_path).replace(".keras", "")
            models[term_id] = tf.keras.models.load_model(model_path)

        trained_models = TrainedModels()
        for term_id, model in models.items():
            trained_models.add_model_for_term_children(term_id, model)

        return trained_models
    ''' Finish Load methods '''

    # TODO: No se deberia necesitar un term_id, tampoco en predict_texts()
    def predict_terms(self, term_id, input_creator, trained_models, keywords_by_term, abstract):
        train_multiplier = self.get_prediction_multiplier(input_creator)
        term_predicton = TermPrediction(trained_models, keywords_by_term, train_multiplier)

        predicted_terms = []
        predictions = term_predicton.predict_texts([abstract], term_id , predicted_terms)

        print('----------------------------- Predictions ----------------------------')

        if all(len(prediction) == 0 for prediction in predictions):
            print("No prediction for the text")

        else:
            # First iterator if we have multiple texts to predict
            for prediction in predictions:
                # Second iterator if we have multiple predictions in same level
                for predicted_term in prediction:
                    term_id = predicted_term.get_term()
                    probability = format(predicted_term.get_probability(), ".2f")
                    term_name = self.thesaurus.get_by_id(term_id).get_name()
                    print(f"Term: {term_name}, Probability: {probability}, Multiplier: {predicted_term.get_multiplier()}")

        return predictions

    # Entrypoint method
    def predict(self):
        keywords_by_term = self.load_keywords_by_term()
        trained_models = self.load_trained_models()

        abstract = get_abstract_from_file("prediction_files/aca3a8.pdf")
        self.predict_terms(self.initial_term_id, AbstractInputCreator(), trained_models, keywords_by_term, abstract)