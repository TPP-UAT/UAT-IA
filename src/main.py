import gc
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
import subprocess
import sys

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    # Father terms: 104, 343, 486, 563, 739, 804, 847, 1145, 1476, 1529, 1583
    # Root term: 1
    initial_term_ids = ['1']

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
