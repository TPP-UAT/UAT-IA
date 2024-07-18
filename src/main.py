import gc
import sys
from Predictor import Predictor
from Trainer import Trainer
from UATMapper import UATMapper
from utils.pdfs_terms_parser import generate_json 
from Constants import pdfs_directory, uat_file

from utils.articles_parser import get_full_text_from_file, get_abstract_from_file, get_tf_idf_words_from_file

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    # 1 - Change document/articles files: Toma de la carpeta todos los pdfs y hace el mappeo de sobre qué palabra 
    # clave corresponde a qué pdf y eso lo guarda en un json llamado pdfs.json. Esto es para que cada vez que cambien 
    # los archivos se re-genere el archivo
    # 2 - Train with documents and save: Toma el pdfs.json para entrenar y guarda
    # 3 - Predict with existent model: Toma todos los modelos y predice
    # 4 - Find shortest path between two terms: Con lo que devuelve 3, calcula la distancia entre dos términos, si el
    # el número es muy grande significa que predijo mal y están muy alejados

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
        generate_json(pdfs_directory)
    
    # Train the models
    elif (training_option == "2"):
        # Father terms: 104, 343, 486, 563, 739, 804, 847, 1145, 1476, 1529, 1583
        # Root term: 1
        initial_term_ids = ['1']

        trainer = Trainer(initial_term_ids, thesaurus)
        trainer.train()

    # Predict with existent model
    elif (training_option == "3"):
        file_name = input("Insert the file name from the file to predict: ")
        initial_term_id = '1'
        
        predictor = Predictor(initial_term_id, thesaurus, file_name)
        predictor.predict()

    # Find shortest path between two terms
    elif (training_option == "4"):
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
                