import gc
import subprocess
import sys
import os
from dotenv import load_dotenv
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from Predictor import Predictor
from Database.Database import Database
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

        if mode == "generate":
            pdf_directory = "./data/PDFs"
            mapper = UATMapper("./data/UAT-filtered.json")
            thesaurus = mapper.map_to_thesaurus()
            upload_data(pdf_directory, thesaurus, database)

        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

