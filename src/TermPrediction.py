from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from Prediction import Prediction
import logging

CHILDREN_THRESHOLD = 0.4
PREDICTION_THRESHOLD = 0.5

class TermPrediction:

    def __init__(self, trained_models, keywords_by_term, train_multiplier):
        self.trained_models = trained_models
        self.keywords_by_term = keywords_by_term
        self.train_multiplier = train_multiplier
        # Logging, change log level if needed
        logging.basicConfig(filename='predictor.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('my_logger')

    def get_predicted_ids(self, predictions):
        predicted_ids = []
        for prediction in predictions:
            term = prediction.get_term()
            predicted_ids.append(term)
        return predicted_ids

    def get_predictions(self, threshold, predictions, keywords):
        predicted_categories = []
        for prediction in predictions:
            predicted_category = [1 if prob >= threshold else 0 for prob in prediction]
            predicted_categories.append(predicted_category)

        term_predictions = []
        for prediction_by_text in predicted_categories:
            predictions_with_prob = []
            for term, index in keywords.items():
                if prediction_by_text[index] == 1:
                    # Create Prediction class. The [0] is because we only have one text
                    prediction_obj = Prediction(term, predictions[0][index], self.train_multiplier)
                    predictions_with_prob.append(prediction_obj)

            if len(predictions_with_prob):
                term_predictions.append(predictions_with_prob)
        return term_predictions

    def predict_texts_with_model(self, texts, model, keywords):
        # Get model information
        input_shape = model.layers[0].input_shape
        dimension = input_shape[1]

        # Tokenization
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(texts)

        sequences = tokenizer.texts_to_sequences(texts)

        # Convert sequences to fixed length vectors (padding with zeros if necessary)
        max_sequence_length = dimension
        sequences_padded = pad_sequences(sequences, maxlen=max_sequence_length)
        
        # Make predictions
        predictions = model(sequences_padded)

        # Generate predictions for term_ids that match the criteria
        prediction_threshold = PREDICTION_THRESHOLD
        predicted_terms = self.get_predictions(prediction_threshold, predictions, keywords)

        # Find terms that may have predictions in the children
        selected_children_threshold = CHILDREN_THRESHOLD
        predicted_children_terms = self.get_predictions(selected_children_threshold, predictions, keywords)

        return predicted_terms, predicted_children_terms

    def predict_texts(self, texts, term_id, predicted_terms):

        self.log.info(f"Started predicting for term: {term_id}")
        print(f"Started predicting for term: {term_id}")
        print(f"Predicted terms: {predicted_terms}")
        model_for_term_children = self.trained_models.get_by_id(term_id)

        if not model_for_term_children:
            return
    
        selected_terms, selected_children = self.predict_texts_with_model(
            texts, model_for_term_children,
            self.keywords_by_term.get(term_id, None)
        )

        if len(selected_children):
            selected_children_ids = self.get_predicted_ids(selected_children[0])
            predicted_terms.extend(selected_terms)
            
            for selected_children_id in selected_children_ids :
                self.predict_texts(texts, selected_children_id, predicted_terms)

        return predicted_terms
