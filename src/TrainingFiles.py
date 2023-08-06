from TermFiles import TermFiles

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

    def get_files_from_children(self, children, files_paths):
        for child_id in children:
            child_term_file = self.term_files.get(child_id, None)
            children_of_the_child = child_term_file.get_children()
            files_paths.extend(child_term_file.get_files_paths())
            if len(children_of_the_child) > 0:
                files_paths = self.get_files_from_children(children_of_the_child, files_paths)

        return files_paths

    def get_term_file_with_children_files(self, term_id):
        term_file = self.term_files.get(term_id, None)
        children = term_file.get_children()
        files_paths = term_file.get_files_paths()

        files_paths = self.get_files_from_children(children, files_paths)

        return TermFiles(term_file.get_id(), files_paths, term_file.get_children())

