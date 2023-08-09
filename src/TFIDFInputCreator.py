import json
from sklearn.feature_extraction.text import TfidfVectorizer

class TFIDFInputCreator:

    def __init__(self):
        self.COMMON_WORDS = ['for', "by", "would", "also", "to", 'and', 'the', 'this', "of", "the", "on", "as", "with", "our", "are", "is"]
        self.words_quantity = 30
        self.keywords_by_word = []

    def generate_tf_idf(self, texts):
        # Inicializar el vectorizador TF-IDF
        vectorizer = TfidfVectorizer()

        # Ajustar y transformar los documentos
        X = vectorizer.fit_transform(texts)

        # Obtener las palabras (términos) en orden
        terms = vectorizer.get_feature_names_out()

        # Encontrar los índices de las palabras que son palabras comunes
        common_indices = [terms.tolist().index(word) for word in self.COMMON_WORDS if word in terms]

        # Asegurarse de que esos índices tengan peso cero en la matriz TF-IDF
        for i in range(len(X.toarray())):
            for idx in common_indices:
                X[i, idx] = 0.0

        # Modificar manualmente los valores TF-IDF para las palabras seleccionadas
        X_modified = X.toarray()
        for i in range(len(texts)):
            for word in self.keywords_by_word:  # Iterate through words directly, not through filtered_array
                word_lower = word.lower()  # Convert the word to lowercase
                if word_lower in terms:  # Check if the lowercase word is in the terms list
                    idx = terms.tolist().index(word_lower)
                    tfidf_value = X_modified[i, idx]
                    new_tfidf_value = tfidf_value * 2  # Aumentar el valor del TF-IDF para las palabras seleccionadas
                    X_modified[i, idx] = new_tfidf_value

        top_words_per_document = []
        for doc_tfidf in X_modified:
            top_word_indices = doc_tfidf.argsort()[-self.words_quantity:][::-1]
            top_words = [(terms[i], doc_tfidf[i]) for i in top_word_indices]
            top_words_per_document.append(top_words)

        top_words_strings = []
        for doc_tfidf in X_modified:
            top_word_indices = doc_tfidf.argsort()[-self.words_quantity:][::-1]
            top_words = [terms[i] for i in top_word_indices]
            top_words_string = ' '.join(top_words)
            top_words_strings.append(top_words_string)

        return top_words_strings

    def parse_keywords(self, keywords):
        for phrase in keywords:
            words = phrase.split()
            self.keywords_by_word.extend(words)

        filtered_array = [word for word in self.keywords_by_word if word.lower() not in self.COMMON_WORDS]
        return filtered_array

    def create_input_arrays(self, files_input, keywords):
        texts = []
        keywords_by_text = []
        self.parse_keywords(keywords)

        for file_path, file_input in files_input.items():
            try:
                file = json.load(open(file_path))
                text_modified = self.generate_tf_idf([file['text']])
                texts.append(text_modified[0])
                keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        # TODO: Delete duplicates from texts, keep consistency in keywords_by_text
        return texts, keywords_by_text
    