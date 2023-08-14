from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from Prediction import Prediction


class TermPrediction:

    def __init__(self, trained_models, keywords_by_term, train_multiplier):
        self.trained_models = trained_models
        self.keywords_by_term = keywords_by_term
        self.train_multiplier = train_multiplier

    def get_predicted_ids(self, predictions):
        predicted_ids = []
        for prediction in predictions:
            term = prediction.get_term()
            predicted_ids.append(term.get_id())
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
        # Tokenización
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(texts)

        sequences = tokenizer.texts_to_sequences(texts)

        # Convertir secuencias a vectores de longitud fija (rellenando con ceros si es necesario)
        max_sequence_length = 12
        sequences_padded = pad_sequences(sequences, maxlen=max_sequence_length)

        # Realizar las predicciones
        predictions = model.predict(sequences_padded)

        prediction_threshold = 0.7
        predicted_terms = self.get_predictions(prediction_threshold, predictions, keywords)

        selected_children_threshold = 0.5
        predicted_children_terms = self.get_predictions(selected_children_threshold, predictions, keywords)
        return predicted_terms, predicted_children_terms

    # TODO no deberiamos necesitar un term_id inicial
    def predict_texts(self, texts, term_id, predicted_terms):
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
