class TermFiles:
    def __init__(self, id, name, files_paths=None, children=None):
        if children is None:
            children = []
        if files_paths is None:
            files_paths = []

        self.id = id
        self.name = name
        self.files_paths = files_paths
        self.children = children

    # Getters
    def get_id(self):
        return self.id

    def get_files_paths(self):
        return self.files_paths

    def get_children(self):
        return self.children
    
    def get_name(self):
        return self.name
    
    def add_file_path(self, file_path):
        self.files_paths.append(file_path)

    def add_children(self, children):
        self.children = children
