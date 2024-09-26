import os
import glob
import json
import tensorflow as tf
from TrainedModels import TrainedModels
from TermPrediction import TermPrediction
from utils.articles_parser import get_abstract_from_file

from utils.input_creators import get_prediction_multiplier

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator

class Predictor:
    def __init__(self, initial_term_id, thesaurus, file_name_to_predict):
        self.initial_term_id = initial_term_id
        self.thesaurus = thesaurus
        self.file_name_to_predict = file_name_to_predict
        self.input_creators = [
            NormalInputCreator(), 
            TFIDFInputCreator(), 
            AbstractInputCreator()
        ]
        self.predictions = {}
        self.predictions_by_term = {}

    def print_predictions(self):
        print('----------------------------- Predictions ----------------------------')

        if len(self.predictions) == 0:
            print("There are no predictions")

        else:
            for term_id, prediction in self.predictions.items():
                print(f"Term: {term_id}, Probabilities: {prediction.get_probabilities()}, Multipliers: {prediction.get_multipliers()}")

            for term_id, final_prediction in self.predictions_by_term.items():
                print(f"Term: {term_id}, Probability: {final_prediction}")

    ''' Load methods '''
    def load_keywords_by_term(self):
        file = open("./data/keywords-by-term.json", "r")
        keywords_by_term = file.read()
        keywords_by_term = json.loads(keywords_by_term)
        file.close()
        return keywords_by_term

    def load_trained_models(self, folder_name):
        models = {}
        for model_path in glob.glob("./models/" + folder_name + "/*.keras"):
            term_id = os.path.basename(model_path).replace(".keras", "")
            models[term_id] = tf.keras.models.load_model(model_path)

        trained_models = TrainedModels()
        for term_id, model in models.items():
            trained_models.add_model_for_term_children(term_id, model)

        return trained_models
    ''' Finish Load methods '''

    def predict_terms(self, term_id, input_creator, trained_models, keywords_by_term, abstract):
        train_multiplier = input_creator
        term_predicton = TermPrediction(trained_models, keywords_by_term, train_multiplier)

        predicted_terms = []
        # First parameter is an array because we can have multiple texts to predict
        predictions = term_predicton.predict_texts([abstract], term_id, predicted_terms)

        return predictions

    def generate_predictions(self, predictions):
        print("predictions", predictions)
        # Combine predictions from different input creators if the term is already in the predictions
        for prediction in predictions:
            for predicted_term in prediction:
                if predicted_term.get_term() not in self.predictions:
                    self.predictions[predicted_term.get_term()] = predicted_term
                else:
                    probability = predicted_term.get_probabilities()[0]
                    self.predictions[predicted_term.get_term()].add_probability(probability)
                    self.predictions[predicted_term.get_term()].add_multiplier(predicted_term.get_multipliers()[0])

        # Generate prediction object with the final probabilities
        final_predictions = {}
        for term_id, prediction in self.predictions.items():
            final_prediction = 0
            for pred, multiplier in zip(prediction.get_probabilities(), prediction.get_multipliers()):
                final_prediction += pred * multiplier
            final_predictions[term_id] = final_prediction

        self.predictions_by_term = final_predictions

    # Entrypoint method
    def predict(self):
        # The index of the keyword matches the position of the training input { 'term_id': index }
        keywords_by_term = self.load_keywords_by_term()
        abstract = get_abstract_from_file('prediction_files/' + self.file_name_to_predict + '.pdf', True)

        # Iterate through the input creators
        for input_creator in self.input_creators:
            trained_models = self.load_trained_models(input_creator.get_folder_name())
            predictions = self.predict_terms(self.initial_term_id, get_prediction_multiplier(input_creator), trained_models, keywords_by_term, abstract)
            self.generate_predictions(predictions)

        self.print_predictions()
