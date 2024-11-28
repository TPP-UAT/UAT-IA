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
            # NormalInputCreator(database), 
            TFIDFInputCreator(database, thesaurus), 
            #AbstractInputCreator(database)
        ]

    # Entrypoint method
    def train_by_term_id(self, term_id):
        for input_creator in self.input_creators:
            term_trainer = TermTrainer(self.thesaurus, self.database)
            term_trainer.train_model(term_id, input_creator)

            del term_trainer
            gc.collect()
