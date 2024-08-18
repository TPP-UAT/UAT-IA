import gc
import sys
from UATMapper import UATMapper
from utils.pdfs_terms_parser import generate_json 

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    print(
"""-----------------------------------------------
Training options:
        1 - Change document/articles files
        2 - Find shortest path between two terms
Insert option number: """)
    training_option = input()

    # Change document/articles files
    if (training_option == "1"):
        # Generate json file with terms associated to pdfs
        generate_json("./data/PDFs", thesaurus)

    # Find shortest path between two terms
    elif (training_option == "2"):
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
