import json
import tensorflow as tf
from TermPrediction import TermPrediction
from utils.articles_parser import get_abstract_from_file
import logging

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator

class Predictor:
    def __init__(self, initial_term_id, file_name_to_predict):
        self.initial_term_id = initial_term_id
        self.file_name_to_predict = file_name_to_predict
        self.input_creators = [
            # NormalInputCreator(), 
            # TFIDFInputCreator(), 
            AbstractInputCreator()
        ]
        self.predictions = {}
        self.predictions_by_term = {}
        # Logging, change log level if needed
        logging.basicConfig(filename='predictor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('my_logger')

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

    def predict_terms(self, term_id, input_creator, keywords_by_term, abstract):
        term_predicton = TermPrediction(keywords_by_term, input_creator)

        predicted_terms = []
        # First parameter is an array because we can have multiple texts to predict
        predictions = term_predicton.predict_texts([abstract], term_id, predicted_terms)

        return predictions

    # Entrypoint method
    def predict(self):
        self.log.info(f"---------------------------------")
        self.log.info(f"Predicting for file id: {self.file_name_to_predict}")
        # The index of the keyword matches the position of the training input { 'term_id': index }
        keywords_by_term = self.load_keywords_by_term()
        abstract = get_abstract_from_file('prediction_files/' + self.file_name_to_predict + '.pdf')

        # Iterate through the input creators
        for input_creator in self.input_creators:
            self.log.info(f"Predicting with input creator: {input_creator.get_folder_name()}")
            predictions = self.predict_terms(self.initial_term_id, input_creator, keywords_by_term, abstract)
            self.generate_predictions(predictions)

        self.print_predictions()

    def generate_predictions(self, predictions):
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
