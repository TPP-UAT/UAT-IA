class Thesaurus:
    def __init__(self, name):
        self.terms = {}
        self.name = name

    # Getters
    def get_by_id(self, term_id):
        return self.terms.get(term_id, None)

    def get_branch(self, term_id):
        root_term = self.get_by_id(term_id)
        branch_thesaurus = Thesaurus("branch" + root_term.get_name())
        branch_thesaurus.add_term(root_term)
        self.add_children_of_term(branch_thesaurus, root_term)
        return branch_thesaurus

    def get_size(self):
        return len(self.terms)

    def get_terms(self):
        return self.terms

    def get_by_name(self, name):
        for term in self.terms:
            if name == term.get_name():
                return term

    def print_names_and_ids(self):
        for term_key, term_value in self.terms.items():
            print("Id: ", term_key + " Name: " + term_value.get_name(), "Children: ", term_value.get_children())

    def add_children_of_term(self, thesaurus, term):
        if len(term.get_children()) != 0:
            for child in term.get_children():
                child_term = self.get_by_id(child)
                self.add_children_of_term(thesaurus, child_term)
                thesaurus.add_term(child_term)

    def add_term(self, term):
        self.terms[term.get_id()] = term
