import fitz
from Database.File import File
from utils.articles_parser import get_full_text_from_file

class NormalInputCreator:
    def __init__(self, database = None):
        self.folder_name = 'normal'

        # Database connection
        self.database = database
        self.file_db = File(database)

    def get_folder_name(self):
        return self.folder_name

    def create_input_arrays(self, files_input, keywords):
        texts = []
        keywords_by_text = []

        for file_path, file_input in files_input.items():
            try:
                full_text = get_full_text_from_file(file_path)
                texts.append(full_text)
                keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        return texts, keywords_by_text
    