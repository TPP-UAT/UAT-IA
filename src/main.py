import gc
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

    print("Training options: \n 1 - Change document/articles files \n 2 - Train with documents and save \n 3 - Predict with existent model \n Insert option number: ")
    training_option = input()

    # Change document/articles files for training the models
    if (training_option == "1"):
        # Generate json file with terms associated to pdfs
        generate_json("./data/PDFs")
    
    # Train the models by initial term ids
    elif (training_option == "2"):
        # Father terms: 104, 343, 486, 563, 739, 804, 847, 1145, 1476, 1529, 1583
        # Root term: 1
        initial_term_ids = ['1145', '1476', '739', '847']

        trainer = Trainer(initial_term_ids, thesaurus)
        trainer.train()

    # Predict with existent model
    elif (training_option == "3"):
        initial_term_id = '1'
        
        predictor = Predictor(initial_term_id, thesaurus)
        predictor.predict()
