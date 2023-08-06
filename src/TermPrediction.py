from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

class TermPrediction:

    def __init__(self, trained_models, keywords_by_term):
        self.trained_models = trained_models
        self.keywords_by_term = keywords_by_term

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

        # Asignar etiquetas basadas en el umbral (0.5 en este caso)
        threshold = 0.5
        predicted_categories = []
        for prediction in predictions:
            predicted_category = [1 if prob >= threshold else 0 for prob in prediction]
            predicted_categories.append(predicted_category)

        print("predicted_categories", predicted_categories)

        predictions_ids = []
        for prediction_by_text in predicted_categories:
            predicted_terms = []
            for term, index in keywords.items():
                if prediction_by_text[index] == 1:
                    predicted_terms.append(term.get_id())
            predictions_ids.append(predicted_terms)

        return predictions_ids


    # TODO no deberiamos necesitar un term_id inicial
    def predict_texts(self, texts, term_id, predicted_ids):
        print("term_id", term_id)
        model_for_term_children = self.trained_models.get_by_id(term_id)
        if not model_for_term_children:
            return
        selected_ids = self.predict_texts_with_model(texts, model_for_term_children, self.keywords_by_term.get(term_id, None))
        print("selected_ids", selected_ids)
        predicted_ids.extend(selected_ids)
        for selected_id in selected_ids[0]:
            self.predict_texts(texts, selected_id, predicted_ids)

        return predicted_ids