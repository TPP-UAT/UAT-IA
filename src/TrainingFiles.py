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

    def print_term_files(self):
        for term_key, term_value in self.term_files.items():
            print("Id: ", term_key + " Name: " + term_value.get_name(), "Children: ", term_value.get_children(), "Files: ", term_value.get_files_paths())

    def add_term_files(self, term_file):
        self.term_files[term_file.get_id()] = term_file

    def get_files_from_children(self, children, files_paths):
        for child_id in children:
            child_term_file = self.term_files.get(child_id, None)
            if child_term_file:
                children_of_the_child = child_term_file.get_children()
                files_paths.extend(child_term_file.get_files_paths())
                if len(children_of_the_child) > 0:
                    files_paths = self.get_files_from_children(children_of_the_child, files_paths)

        return files_paths

    def get_term_file_with_children_files(self, term_id):
        term_file = self.term_files.get(term_id, None)
        if term_file:
            children = term_file.get_children()
            files_paths = term_file.get_files_paths()

            files_paths = self.get_files_from_children(children, files_paths)
            return TermFiles(term_file.get_id(), term_file.get_name(), files_paths, term_file.get_children())

    def to_dict(self):
        # Convert the term_files to a serializable dictionary
        return {
            term_id: {
                'name': term_file.get_name(),
                'children': term_file.get_children(),
                'files_paths': term_file.get_files_paths()
            } for term_id, term_file in self.term_files.items()
        }