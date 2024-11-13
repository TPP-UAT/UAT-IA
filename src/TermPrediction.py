import glob
import logging
import os
import spacy
from utils.input_creators import get_prediction_multiplier
from Prediction import Prediction

CHILDREN_THRESHOLD = 0.2
PREDICTION_THRESHOLD = 0.5

logging.basicConfig(filename='logs/predictor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TermPrediction:

    def __init__(self, input_creator):
        self.input_creator = input_creator
        self.nlp = None
        self.log = logging.getLogger('predictor_logger')

    def get_model_for_term(self, term_id):
        """
        Retrieve and load the saved spaCy model for a specific term.
        The model should have been previously saved to disk.
        """
        model_path = f"./models/{self.input_creator.get_folder_name()}/{term_id}"
        
        try:
            # Check if the model path exists, then load the model
            if not glob.glob(model_path):
                self.log.error(f"Model for term {term_id} not found at path: {model_path}")
                return False
            else:
                # Load the saved spaCy model from disk
                print(f"Loading spaCy model from: {model_path}", flush=True)
                self.nlp = spacy.load(model_path)  # Load the specific model for this term
                return True
        except Exception as e:
            self.log.error(f"Error loading model for term {term_id}: {e}")
            return False

    def predict_texts_with_model(self, texts):
        """
        Perform prediction using a specific spaCy model loaded for the term.
        """

        predicted_terms = []
        predicted_children_ids = []
        for text in texts:
            print("Processing text...", text[0], flush=True)
            doc = self.nlp(text[0])  # Process the text with the loaded spaCy model
            for cat, score in doc.cats.items():
                print(f"{cat}: {score:.4f}", flush=True)
                if score > PREDICTION_THRESHOLD:
                    prediction_obj = Prediction(cat, doc.cats[cat], get_prediction_multiplier(self.input_creator))

                    predicted_terms.append(prediction_obj)
                if score > CHILDREN_THRESHOLD:
                    predicted_children_ids.append(cat)

        return predicted_terms, predicted_children_ids

        # Score supera PREDCITION -> guardar como un predicted term
         #            prediction_obj = Prediction(term, doc.cats[term], get_prediction_multiplier(self.input_creator))
        #             predicted_terms.append(prediction_obj)
        # Score supera CHILDREN PREDCITION -> guardar como un id y apendearlo a un predicted_children_terms (son ids)



            # Check the categories (terms) predicted by spaCy's text classifier
        #     for term, index in keywords.items():
        #         if doc.cats.get(term, 0) >= PREDICTION_THRESHOLD:  # Check threshold
        #             prediction_obj = Prediction(term, doc.cats[term], get_prediction_multiplier(self.input_creator))
        #             predicted_terms.append(prediction_obj)

        #     if predicted_terms:
        #         predictions_with_prob.append(predicted_terms)

        # return predictions_with_prob, []

    # Recursive function to predict the terms (Initially predicted terms are empty)
    def predict_texts(self, texts, term_id, predicted_terms):
        self.log.info(f"Started predicting for term: {term_id}")
        print(f"Started predicting for term: {term_id}", flush=True)

        # Load the saved spaCy model for the term
        model_has_loaded = self.get_model_for_term(term_id)
        if model_has_loaded is not True:
            return predicted_terms  # Skip if the model for the term is not found

        # Use the loaded model to predict the terms
        selected_terms, selected_children_ids = self.predict_texts_with_model(texts)

        if selected_terms:
            predicted_terms.extend(selected_terms)

        # If the prediction returns children, recursively predict for them
        if len(selected_children_ids):
            for selected_children_id in selected_children_ids:
                self.predict_texts(texts, selected_children_id, predicted_terms)

        return predicted_terms
