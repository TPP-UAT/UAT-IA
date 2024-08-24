import gc
import subprocess
import sys
import os
from dotenv import load_dotenv
from UATMapper import UATMapper
from Predictor import Predictor
from Database.Database import Database
from Database.Keyword import Keyword
from utils.pdfs_terms_parser import upload_data 

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    load_dotenv() # Load environment variables
    db_url = os.getenv('DB_URL')
    mode = os.getenv('MODE')

    # Initialize database
    try:
        database = Database(db_url)
        engine = database.get_engine()

        # Verifies connection to the database
        connection = engine.connect()
        print("Database connection successful.")

        database.init_db()

        print("Querying database...")

        pdf_directory = "./data/PDFs"
        mapper = UATMapper("./data/UAT-filtered.json")
        thesaurus = mapper.map_to_thesaurus()
        if (mode == "generate"):
            upload_data(pdf_directory, thesaurus, database)
        elif (mode == "train"):
            # Iterate over all the children of the root term (We're missing the training for the root term)
            children = thesaurus.get_branch_children("1")
            for child in children:
                print("Training term id: ", child.get_id())
                process = subprocess.Popen([sys.executable, 'src/train_term.py', child.get_id()])
                process.wait()  # Ensure the process completes before starting the next
                gc.collect()  # Explicitly collect garbage after each process
        
        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

