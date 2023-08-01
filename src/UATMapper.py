import json
from Thesaurus import Thesaurus
from Term import Term


class UATMapper:
    def __init__(self, file_name):
        self.file_name = file_name
    def map_json_id_to_term_id(self, json_key):
        return json_key.split("/")[-1]

    def map_json_to_term(self, json_key, json_term):
        term_key = self.map_json_id_to_term_id(json_key)
        term = Term(term_key)
        print(enumerate(list(json_term.keys())))

        return term

    def map_to_thesaurus(self):
        json_data = json.load(open(self.file_name))

        thesaurus = Thesaurus("UAT")
        for key, obj in json_data.items():
            term = self.map_json_to_term(key, obj)
