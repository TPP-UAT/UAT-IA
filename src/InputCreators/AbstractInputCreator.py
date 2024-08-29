from Database.File import File

class AbstractInputCreator:
    def __init__(self, thesaurus, database):
        self.folder_name = 'abstract'
        self.thesaurus = thesaurus

        # Database connection
        self.database = database
        self.file_db = File(database)

    def get_folder_name(self):
        return self.folder_name

    def create_input_arrays(self, files_input, keywords):
        texts = []
        keywords_by_text = []

        for file_id, file_input in files_input.items():
            try:                
                abstract_text = self.file_db.get_abstract_by_file_id(file_id)
                if abstract_text:
                    texts.append(abstract_text)
                    keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_id)

        # TODO: Delete duplicates from texts, keep consistency in keywords_by_text
        return texts, keywords_by_text
    