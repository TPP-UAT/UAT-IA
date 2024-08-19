import gc
import json
import os
import multiprocessing
import signal
import sys
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer

from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator

class Trainer:
    def __init__(self, inital_term_ids, thesaurus):
        self.initial_term_ids = inital_term_ids
        self.thesaurus = thesaurus
        self.input_creators = [
            # NormalInputCreator(), 
            # TFIDFInputCreator(), 
            AbstractInputCreator()
        ]
        self.processes = []

    ''' Save Methods '''
    def save_term_trainer(self, term_trainer: TermTrainer):
        self.save_keywords_by_term(term_trainer.get_keywords_by_term())

    def save_keywords_by_term(self, keywords_by_term):
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

    def train_by_term_id(self, term_id, training_files):
        print("----------------term_id: ", term_id)
        for input_creator in self.input_creators:
            term_trainer = TermTrainer(training_files)
            term_trainer.train_model_by_thesaurus(self.thesaurus, term_id, input_creator)

            self.save_term_trainer(term_trainer)

    # Entrypoint method
    def train(self):
        # Create training files
        term_file_mapper = TermFileMapper()
        term_file_mapper.create_training_files(self.thesaurus)

        # Handle signal for Ctrl+C
        original_sigint_handler = signal.signal(signal.SIGINT, self.signal_handler)

        try:
            # Launch processes sequentially
            for term_id in term_file_mapper.get_training_files().get_term_files():
                p = multiprocessing.Process(target=self.train_by_term_id, args=(term_id, term_file_mapper.get_training_files()))
                self.processes.append(p)
                p.start()
                p.join()  # Wait for the subprocess to finish
                gc.collect()
        finally:
            signal.signal(signal.SIGINT, original_sigint_handler)

    # Method to allow the user to terminate the processes with Ctrl+C
    def signal_handler(self, signal, frame):
        print("Interruption detected, terminating processes...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()
        sys.exit(0)
