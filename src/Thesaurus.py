class Thesaurus:
    def __init__(self, name):
        self.terms = {}
        self.name = name

    def get_by_id(self, term_id):
        return self.terms[term_id]

    def add_term(self, term):
        self.terms[term.id] = term

