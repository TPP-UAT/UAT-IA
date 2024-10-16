import gc
import json
import os
from TermTrainer import TermTrainer

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator

class Trainer:
    def __init__(self, thesaurus, database):
        self.thesaurus = thesaurus
        self.database = database
        self.input_creators = [
            # NormalInputCreator(), 
            # TFIDFInputCreator(), 
            AbstractInputCreator(database)
        ]

    ''' Save Methods '''
    def save_term_trainer(self, term_trainer: TermTrainer):
        self.save_keywords_by_term(term_trainer.get_keywords_by_term())

    def save_keywords_by_term(self, keywords_by_term):
        print("Saving keywords by term", flush=True)
        print(keywords_by_term, flush=True)

        file_path = "./data/keywords-by-term.json"
        
        # Check if the file already exists
        if os.path.exists(file_path):
            # If the file exists, read the existing data
            with open(file_path, "r") as file:
                existing_data = json.load(file)
            
            # Update the existing data with new keywords_by_term
            existing_data.update(keywords_by_term)
        else:
            existing_data = keywords_by_term

        # Write the updated data back to the file
        with open(file_path, "w") as file:
            json.dump(existing_data, file)
    ''' End Save Methods '''

    # Entrypoint method
    def train_by_term_id(self, term_id):
        for input_creator in self.input_creators:
            term_trainer = TermTrainer(self.thesaurus, self.database)
            term_trainer.train_model(term_id, input_creator)
            self.save_term_trainer(term_trainer)

            del term_trainer
            gc.collect()


