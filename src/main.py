import gc
import subprocess
import sys
import os
from dotenv import load_dotenv
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from Predictor import Predictor
from Database import Database
from DatabaseModels import File, Keyword

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    load_dotenv() # Load environment variables
    db_url = os.getenv('DB_URL')

    # Initialize database
    try:
        database = Database(db_url)
        engine = database.get_engine()

        # Verifica la conexión con una simple consulta
        connection = engine.connect()
        print("Database connection successful.")
        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

    database.init_db()

    new_file = File(file_id='aac435', abstract='Example test.', full_text='Example test 2')
    print("File ID: ", new_file.file_id)

    try:
        database.add(new_file)
    except Exception as e:
        print(f"Error: {e}")

    print("Querying database...")
    files = database.query('SELECT * FROM "Files"')
    for file in files:
        print("from db: ", file.file_id, file.abstract, file.full_text)

    database.close()
