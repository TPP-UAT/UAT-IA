import json
from Thesaurus import Thesaurus
from Term import Term


class UATMapper:
    def __init__(self, file_name):
        self.file_name = file_name
    def map_json_id_to_term_id(self, json_key):
        return json_key.split("/")[-1]

    def map_json_terms_to_term_attributes(self, term_keys, term_values):
        obj = {}
        for index, key in enumerate(term_keys):
            if "prefLabel" in key:
                obj["name"] = term_values[index][0]["value"]
            if "altLabel" in key:
                obj["altNames"] = [value["value"] for value in term_values[index]]
            if "definition" in key:
                obj["definition"] = term_values[index][0]["value"]
            if "broader" in key:
                obj["broaders"] = [value["value"].split("/")[-1] for value in term_values[index]]
            if "narrower" in key:
                obj["narrowers"] = [value["value"].split("/")[-1] for value in term_values[index]]
        return obj

    def map_json_to_term(self, json_key, json_terms):
        term_key = self.map_json_id_to_term_id(json_key)
        term = Term(term_key)
        attributes = self.map_json_terms_to_term_attributes(list(json_terms.keys()), list(json_terms.values()))
        if "narrowers" in attributes and "broaders" in attributes and "name" in attributes and "altNames" in attributes:
            term.set_attributes(attributes["name"],
                                attributes["narrowers"],
                                attributes["broaders"],
                                attributes["altNames"])

        return term

    def map_to_thesaurus(self):
        json_data = json.load(open(self.file_name))

        thesaurus = Thesaurus("UAT")
        for key, obj in json_data.items():
            term = self.map_json_to_term(key, obj)
            thesaurus.add_term(term)

        print(thesaurus.get_by_id('0'))
