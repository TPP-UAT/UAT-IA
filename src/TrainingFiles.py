class TrainingFiles:
    def __init__(self):
        self.term_files = {}

    # Getters
    def get_term_files(self):
        return self.term_files
    
    def get_by_id(self, term_id):
        return self.term_files.get(term_id, None)

    def get_size(self):
        return len(self.term_files)

    def add_term_files(self, term_file):
        self.term_files[term_file.get_id()] = term_file

