import json
from TermFiles import TermFiles
from TrainingFiles import TrainingFiles

class TermFileMapper:
    def __init__(self):
        self.term_file_ids = []
        self.training_files = TrainingFiles()

    # Getters
    def get_training_files(self):
        return self.training_files
    
    def add_term_file(self, term_id, term_children, file_path):
        # If term_id is not in term_file_ids, add it to term_file_ids and create a new TermFiles object
        if term_id not in self.term_file_ids:
            self.term_file_ids.append(term_id)
            term_files = TermFiles(term_id)
            term_files.add_children(term_children)
            term_files.add_file_path(file_path)
            self.training_files.add_term_files(term_files)
        # Else, add the file into the TermFiles object
        else:
            term_files = self.training_files.get_by_id(term_id)
            term_files.add_file_path(file_path)

    def add_keywords_for_thesaurus_terms(self, keywords, thesaurus, file_path):
        for keyword in keywords:
            for _, term_value in thesaurus.get_terms().items():
                if keyword == term_value.get_name():
                    term_id = term_value.get_id()
                    term_children = term_value.get_children()
                    self.add_term_file(term_id, term_children, file_path)
                    
    def create_training_files(self, thesaurus):
        json_data = json.load(open('./data/training_files.json'))

        files = json_data["files"]
        for file_name in files:
            file = json.load(open('./data/' + file_name))
            file_path = './data/' + file_name
            keywords = file["keywords"]
            self.add_keywords_for_thesaurus_terms(keywords, thesaurus, file_path)
