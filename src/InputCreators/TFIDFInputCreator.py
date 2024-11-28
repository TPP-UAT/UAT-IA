from Database.File import File
from Database.Keyword import Keyword
from utils.articles_parser import get_tf_idf_words_from_file

class TFIDFInputCreator:

    def __init__(self, database = None, thesaurus = None):
        self.COMMON_WORDS = [
            'because', 'there', 'et', 'al', 'in', 'be', 'at', 'has', 'have', 'that', 'can',
            'was', 'its', 'both', 'may', 'we', 'not', 'will', 'or', 'it', 'they',
            'than', 'these', 'however', 'co', 'from', 'an', 'ah', 'for', 'by', 
            'would', 'also', 'to', 'and', 'the', 'this', 'of', 'on', 'as', 'with',
            'our', 'are', 'is', 'which', 'between', 'when', 'where', 'such', 'more',
            'along', 'using', 'data', 'figure', 'results', 'observed', 'obtained',
            'sample', 'values', 'shown', 'analysis', 'measurements', 'all', 'each',
            'used', 'were', 'been', 'different', 'two', 'other', 'set', 'work',
            'case', 'most', 'their', 'but', 'so', 'only', 'a', 'more', ''
        ]
        self.keywords_by_word = []
        self.folder_name = 'tf-idf'
        self.thesaurus = thesaurus

        # Database connection
        self.database = database
        self.file_db = File(database)

    def get_folder_name(self):
        return self.folder_name

    def parse_keywords(self, keywords):
        for phrase in keywords:
            words = phrase.split()
            self.keywords_by_word.extend(words)

        filtered_array = [word for word in self.keywords_by_word if word.lower() not in self.COMMON_WORDS]
        return filtered_array
    
    def get_file_data_input(self, file_id):
        try:
            full_text = self.file_db.get_full_text_by_file_id(file_id)
            keyword_table_db = Keyword(self.database)
            keywords_ids_by_text = keyword_table_db.get_keywords_by_file_id(file_id)
            keywords_by_text = []
            for keyword_id in keywords_ids_by_text:
                term = self.thesaurus.get_by_id(str(keyword_id))
                keyword = term.get_name()
                keywords_by_text.append(keyword)
            
            response = get_tf_idf_words_from_file(full_text, keywords_by_text)
            return response[0]
        except:
            print("Error trying to load file with path: ", file_id)
            