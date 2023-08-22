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
    
    def add_term_file(self, term_id, term_name, term_children, file_paths):
        term_files = TermFiles(term_id, term_name, file_paths, term_children)
        self.training_files.add_term_files(term_files)

    def create_training_files(self, thesaurus):
        json_data = json.load(open('./data/pdfs.json'))

        # TODO: Add term event if it doesnt have any document (e.g. Lunar Phase)
        for term in json_data:
            id = term['id']
            thesaurus_term = thesaurus.get_by_id(str(id))
            if thesaurus_term:
                name = thesaurus_term.get_name()
                children = thesaurus.get_by_id(id).get_children()
                self.add_term_file(id, name, children, term['files'])
