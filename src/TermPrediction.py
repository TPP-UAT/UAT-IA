import glob
import logging
import spacy
from utils.input_creators import get_prediction_multiplier
from Prediction import Prediction

CHILDREN_THRESHOLD = 0.000001
PREDICTION_THRESHOLD = 0.000001

class TermPrediction:

    def __init__(self, keywords_by_term, input_creator):
        self.keywords_by_term = keywords_by_term
        self.input_creator = input_creator
        # Logging, change log level if needed
        logging.basicConfig(filename='predictor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('my_logger')

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
                return None
            else:
                # Load the saved spaCy model from disk
                print(f"Loading spaCy model from: {model_path}", flush=True)
                return spacy.load(model_path)  # Load the specific model for this term
        except Exception as e:
            self.log.error(f"Error loading model for term {term_id}: {e}")
            return None

    def predict_texts_with_model(self, texts, model, keywords):
        """
        Perform prediction using a specific spaCy model loaded for the term.
        """
        print(f"Predicting with spaCy model for term", flush=True)

        predictions_with_prob = []
        for text in texts:
            doc = model(text)  # Process the text with the loaded spaCy model
            predicted_terms = []

            # Check the categories (terms) predicted by spaCy's text classifier
            for term, index in keywords.items():
                if doc.cats.get(term, 0) >= PREDICTION_THRESHOLD:  # Check threshold
                    prediction_obj = Prediction(term, doc.cats[term], get_prediction_multiplier(self.input_creator))
                    predicted_terms.append(prediction_obj)

            if predicted_terms:
                predictions_with_prob.append(predicted_terms)

        return predictions_with_prob, []

    # Recursive function to predict the terms (Initially predicted terms are empty)
    def predict_texts(self, texts, term_id, predicted_terms):
        self.log.info(f"Started predicting for term: {term_id}")
        print(f"Started predicting for term: {term_id}", flush=True)

        # Load the saved spaCy model for the term
        model_for_term = self.get_model_for_term(term_id)
        if model_for_term is None:
            return predicted_terms  # Skip if the model for the term is not found

        # Use the loaded model to predict the terms
        selected_terms, selected_children = self.predict_texts_with_model(
            texts, model_for_term,
            self.keywords_by_term.get(term_id, None)
        )

        if selected_terms:
            predicted_terms.extend(selected_terms)

        # If the prediction returns children, recursively predict for them
        if len(selected_children):
            selected_children_ids = self.get_predicted_ids(selected_children[0])
            for selected_children_id in selected_children_ids:
                self.predict_texts(texts, selected_children_id, predicted_terms)

        return predicted_terms
