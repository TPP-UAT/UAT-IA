class TrainingFiles:
    def __init__(self):
        self.term_files = {}

    def get_term_files(self):
        return self.term_files

    def add_term_files(self, term_file):
        self.term_files[term_file.get_id()] = term_file

