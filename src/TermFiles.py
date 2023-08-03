class TermFiles:
    def __init__(self, id):
        self.id = id
        self.files = []
        self.children = []

    # Getters
    def get_id(self):
        return self.id

    def get_files(self):
        return self.files

    def get_children(self):
        return self.children
    
    def add_file(self, file):
        self.files.append(file)

    def add_children(self, children):
        self.children = children
