from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences


class TermPrediction:

    def __init__(self, trained_models, keywords_by_term):
        self.trained_models = trained_models
        self.keywords_by_term = keywords_by_term

    def get_predicted_ids(self, threshold, predictions, keywords):
        predicted_categories = []
        for prediction in predictions:
            predicted_category = [1 if prob >= threshold else 0 for prob in prediction]
            predicted_categories.append(predicted_category)

        predictions_ids = []
        for prediction_by_text in predicted_categories:
            predicted_terms = []
            for term, index in keywords.items():
                if prediction_by_text[index] == 1:
                    predicted_terms.append(term.get_id())
            if len(predicted_terms):
                predictions_ids.append(predicted_terms)

        return predictions_ids

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
        predicted_ids = self.get_predicted_ids(prediction_threshold, predictions, keywords)

        selected_children_threshold = 0.5
        selected_children_ids = self.get_predicted_ids(selected_children_threshold, predictions, keywords)
        return predicted_ids, selected_children_ids

    # TODO no deberiamos necesitar un term_id inicial
    def predict_texts(self, texts, term_id, predicted_ids):
        model_for_term_children = self.trained_models.get_by_id(term_id)
        if not model_for_term_children:
            return
        selected_ids, selected_children_ids = self.predict_texts_with_model(
            texts, model_for_term_children,
            self.keywords_by_term.get(term_id, None)
        )
        predicted_ids.extend(selected_ids)
        for selected_id in selected_children_ids[0]:
            self.predict_texts(texts, selected_id, predicted_ids)

        return predicted_ids
