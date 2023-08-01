class Thesaurus:
    def __init__(self, name):
        self.terms = {}
        self.name = name

    def get_by_id(self, term_id):
        return self.terms.get(term_id, None)

    def add_term(self, term):
        self.terms[term.get_id()] = term

