class TermFiles:
    def __init__(self, id):
        self.id = id
        self.files_paths = []
        self.children = []

    # Getters
    def get_id(self):
        return self.id

    def get_files_paths(self):
        return self.files_paths

    def get_children(self):
        return self.children
    
    def add_file_path(self, file_path):
        self.files_paths.append(file_path)

    def add_children(self, children):
        self.children = children
