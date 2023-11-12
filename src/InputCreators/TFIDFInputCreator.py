from utils.articles_parser import get_tf_idf_words_from_file

class TFIDFInputCreator:

    def __init__(self):
        self.COMMON_WORDS = ['et', 'al', 'in', 'be', 'at', 'has', 'that', 'can', 'was', 'its', 'both', 'may', 'we', 'not', 'will', 'or', 'it', 'they', 'than', 'these', 'however', 'co', 'from', 'an', 'ah', 'for', "by", "would", "also", "to", 'and', 'the', 'this', "of", "the", "on", "as", "with", "our", "are", "is"]
        self.keywords_by_word = []

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
                text_modified = get_tf_idf_words_from_file(file_path, self.keywords_by_word)
                
                if text_modified[0] not in texts:
                    texts.append(text_modified[0])
                    keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        # TODO: Delete duplicates from texts, keep consistency in keywords_by_text
        return texts, keywords_by_text
    