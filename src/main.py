import gc
import subprocess
import sys
import os
from dotenv import load_dotenv
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from Predictor import Predictor

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    load_dotenv() # Load environment variables
    mode = os.getenv('MODE')

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    # Father terms: 104, 343, 486, 563, 739, 804, 847, 1145, 1476, 1529, 1583
    # Root term: 1

    if (mode == 'train'):
        # Create training files
        term_file_mapper = TermFileMapper()
        term_file_mapper.create_training_files(thesaurus)

        try:
            # Launch subprocesses sequentially
            for term_id in term_file_mapper.get_training_files().get_term_files():
                process = subprocess.Popen([sys.executable, 'src/train_term.py', term_id])
                process.wait()  # Ensure the process completes before starting the next
                gc.collect()  # Explicitly collect garbage after each process
        finally:
            gc.collect()
            sys.exit(0)
    elif (mode == 'predict'):
        initial_term_id = '1'
        file_name = os.getenv('FILE_TO_PREDICT')
        
        predictor = Predictor(initial_term_id, thesaurus, file_name)
        predictor.predict()