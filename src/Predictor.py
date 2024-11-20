import json
import spacy
from TermPrediction import TermPrediction
from utils.articles_parser import get_abstract_from_file, get_full_text_from_file
import logging

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator
logging.basicConfig(filename='logs/predictor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Predictor:
    def __init__(self, initial_term_id, file_name_to_predict, thesaurus):
        self.initial_term_id = initial_term_id
        self.file_name_to_predict = file_name_to_predict
        self.input_creators = [
            NormalInputCreator(), 
            # TFIDFInputCreator(), 
            AbstractInputCreator()
        ]
        self.predictions = {}
        self.predictions_by_term = {}
        self.thesaurus = thesaurus
        self.log = logging.getLogger('predictor_logger')

    def print_predictions(self):
        print('----------------------------- Predictions ----------------------------')

        if len(self.predictions) == 0:
            print("There are no predictions")

        else:
            for term_id, prediction in self.predictions.items():
                term_obj = self.thesaurus.get_by_id(term_id)
                parents = term_obj.get_parents()
                print(f"Term: {term_id}, Probabilities: {prediction.get_probabilities()}, Multipliers: {prediction.get_multipliers()}, Parents: {parents}")

            for term_id, final_prediction in self.predictions_by_term.items():
                print(f"Term: {term_id}, Probability: {final_prediction}")

    ''' Load methods '''
    def load_keywords_by_term(self):
        file = open("./data/keywords-by-term.json", "r")
        keywords_by_term = file.read()
        keywords_by_term = json.loads(keywords_by_term)
        file.close()
        return keywords_by_term

    def predict_terms(self, term_id, input_creator, abstract):
        term_prediction = TermPrediction(input_creator)

        predicted_terms = []
        # First parameter is an array because we can have multiple texts to predict
        predictions = term_prediction.predict_texts([abstract], term_id, predicted_terms)
        return predictions

    def generate_predictions(self, predictions):
        # Combine predictions from different input creators if the term is already in the predictions
        for prediction in predictions:
            if prediction.get_term() not in self.predictions:
                self.predictions[prediction.get_term()] = prediction
            else:
                probability = prediction.get_probabilities()[0]
                self.predictions[prediction.get_term()].add_probability(probability)
                self.predictions[prediction.get_term()].add_multiplier(prediction.get_multipliers()[0])

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
        print(f"---------------------------------")
        print(f"Predicting for file id: {self.file_name_to_predict}")
        # The index of the keyword matches the position of the training input { 'term_id': index }
        abstract = get_abstract_from_file('prediction_files/' + self.file_name_to_predict + '.pdf')
        full_text = get_full_text_from_file('prediction_files/' + self.file_name_to_predict + '.pdf')

        data_input = {"abstract": abstract, "normal": full_text, "tf-idf": full_text}
        # Iterate through the input creators
        for input_creator in self.input_creators:
            self.log.info(f"Predicting with input creator: {input_creator.get_folder_name()}")
            predictions = self.predict_terms(self.initial_term_id, input_creator, data_input[input_creator.get_folder_name()])
            self.generate_predictions(predictions)

        self.print_predictions()
