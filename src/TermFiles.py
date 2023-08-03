class TermFiles:
    def __init__(self, id, files, children):
        self.id = id
        self.files = files
        self.children = children

    # Getters
    def get_id(self):
        return self.id

    def get_files(self):
        return self.files

    def get_children(self):
        return self.children
