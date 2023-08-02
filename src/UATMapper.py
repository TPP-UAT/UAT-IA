import json
from Thesaurus import Thesaurus
from Term import Term


class UATMapper:
    def __init__(self, file_name):
        self.file_name = file_name
    def map_json_id_to_term_id(self, json_key):
        return json_key.split("/")[-1]

    def map_json_terms_to_term_attributes(self, term_keys, term_values):
        attributes = {}
        for index, key in enumerate(term_keys):
            if "prefLabel" in key:
                attributes["name"] = term_values[index][0]["value"]
            if "altLabel" in key:
                attributes["altNames"] = [value["value"] for value in term_values[index]]
            # if "definition" in key:
               # attributes["definition"] = term_values[index][0]["value"]
            if "broader" in key:
                attributes["broader"] = [value["value"].split("/")[-1] for value in term_values[index]]
            if "narrower" in key:
                attributes["narrower"] = [value["value"].split("/")[-1] for value in term_values[index]]
        return attributes

    def map_json_to_term(self, json_key, json_terms):
        term_key = self.map_json_id_to_term_id(json_key)
        term = Term(term_key)
        attributes = self.map_json_terms_to_term_attributes(list(json_terms.keys()), list(json_terms.values()))
        if "name" in attributes:
            term.set_name(attributes["name"])
            term.set_children(attributes["narrower"] if "narrower" in attributes else [])
            term.set_parents(attributes["broader"] if "broader" in attributes else [])
            term.set_alt_names(attributes["altNames"] if "altNames" in attributes else [])

        return term

    def map_to_thesaurus(self):
        json_data = json.load(open(self.file_name))

        thesaurus = Thesaurus("UAT")
        for key, obj in json_data.items():
            term = self.map_json_to_term(key, obj)
            thesaurus.add_term(term)

        print(thesaurus.get_by_id('0').get_name())
