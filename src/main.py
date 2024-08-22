import gc
import subprocess
import sys
import os
from dotenv import load_dotenv
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from Predictor import Predictor
from Database.Database import Database
from Database.Keyword import Keyword
from Database.File import File

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    load_dotenv() # Load environment variables
    db_url = os.getenv('DB_URL')

    # Initialize database
    try:
        database = Database(db_url)
        engine = database.get_engine()

        # Verifies connection to the database
        connection = engine.connect()
        print("Database connection successful.")

        database.init_db()

        print("Querying database...")

        file = File(database)
        new_file = file.add_file("abc126", "This is an abstract", "This is the full text")
        print("file aaaa: ", new_file)
        keyword = Keyword(database)
        print("dsdsad: ")
        keyword.add_keyword(1, "abc126", 1)

        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

