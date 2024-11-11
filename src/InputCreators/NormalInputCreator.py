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

    def get_file_data_input(self, file_id):
        try:
            return self.file_db.get_full_text_by_file_id(file_id)
        except:
            print("Error trying to load file with path: ", file_id)