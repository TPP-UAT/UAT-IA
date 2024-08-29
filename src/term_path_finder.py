import gc
import sys
from UATMapper import UATMapper
from utils.pdfs_terms_parser import generate_json 

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    while True:
        start_term_id = input("Insert the ID from the first term (q for quit): ")
        end_term_id = input("Insert the ID from the second term (q for quit): ")

        if start_term_id == 'q' or end_term_id == 'q':
            sys.exit()

        shortest_path = thesaurus.find_shortest_path(start_term_id, end_term_id)

        if shortest_path:
            print("The shortest path is:", shortest_path)
            print("------------------")
        else:
            print("There's no path between the terms.")
            print("------------------")
