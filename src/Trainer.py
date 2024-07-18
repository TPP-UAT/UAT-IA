import gc
import json
import os
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer
from Constants import keywords_by_term_json

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator

class Trainer:
    def __init__(self, inital_term_ids, thesaurus):
        self.initial_term_ids = inital_term_ids
        self.thesaurus = thesaurus
        self.input_creators = [
            NormalInputCreator(), 
            TFIDFInputCreator(), 
            AbstractInputCreator()
        ]

    ''' Save Methods '''
    def save_term_trainer(self, term_trainer: TermTrainer):
        self.save_keywords_by_term(term_trainer.get_keywords_by_term())

    def save_keywords_by_term(self, keywords_by_term):
        file_path = keywords_by_term_json
        
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

    def train_by_term_id(self, term_id, input_creator, training_files, branch_thesaurus):
        term_trainer = TermTrainer(training_files)
        term_trainer.train_model_by_thesaurus(branch_thesaurus, term_id, input_creator)

        return term_trainer

    def train_branch(self, term_id):
        branch_thesaurus = self.thesaurus.get_branch(term_id)

        term_file_mapper = TermFileMapper()
        term_file_mapper.create_training_files(branch_thesaurus)

        training_files = term_file_mapper.get_training_files()

        for input_creator in self.input_creators:
            term_trainer = self.train_by_term_id(term_id, input_creator, training_files, branch_thesaurus)
            self.save_term_trainer(term_trainer)

    # Entrypoint method
    def train(self):
        for term_id in self.initial_term_ids:
            self.train_branch(term_id)
            gc.collect()