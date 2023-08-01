class Term:
    def __init__(self, id):
        self.id = id
        self.name = ""
        self.children = []
        self.parents = []
        self.alt_labels = []

    # Getters
    def get_id(self):
        return self.id

    def get_children(self):
        return self.children

    def get_parents(self):
        return self.parents

    # Setters
    def set_attributes(self, name, children, parents, alt_labels):
        self.name = name
        self.children = children
        self.parents = parents

    def get_by_id(self, id):
        if self.id == id:
            return self.name
