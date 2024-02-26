import gc
import sys
from Predictor import Predictor
from Trainer import Trainer
from UATMapper import UATMapper
from utils.pdfs_terms_parser import generate_json 

from utils.articles_parser import get_full_text_from_file, get_abstract_from_file, get_tf_idf_words_from_file

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    print(
"""-----------------------------------------------
Training options:
        1 - Change document/articles files
        2 - Train with documents and save
        3 - Predict with existent model
        4 - Find shortest path between two terms
Insert option number: """)
    training_option = input()

    # Change document/articles files
    if (training_option == "1"):
        # Generate json file with terms associated to pdfs
        generate_json("./data/PDFs")
    
    # Train the models
    elif (training_option == "2"):
        # Father terms: 104, 343, 486, 563, 739, 804, 847, 1145, 1476, 1529, 1583
        # Root term: 1
        initial_term_ids = ['104']

        trainer = Trainer(initial_term_ids, thesaurus)
        trainer.train()

    elif (training_option == "4"):
        # Find shortest path between two terms
        start_term_id = input("Insert the ID from the first term: ")
        end_term_id = input("Insert the ID from the second term: ")

        shortest_path = thesaurus.find_shortest_path(start_term_id, end_term_id)

        if shortest_path:
            print("The shortest path is:", shortest_path)
        else:
            print("There's no path between the terms.")

    # Predict with existent model
    elif (training_option == "3"):
        initial_term_id = '104'
        
        predictor = Predictor(initial_term_id, thesaurus)
        predictor.predict()
