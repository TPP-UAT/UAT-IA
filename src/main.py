import gc
import subprocess
import sys
import os
import tensorflow as tf
from dotenv import load_dotenv
from UATMapper import UATMapper
from Predictor import Predictor
from Database.Database import Database
from Database.Keyword import Keyword
from utils.pdfs_terms_parser import upload_data 

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    load_dotenv() # Load environment variables
    db_url = os.getenv('DB_URL')
    mode = os.getenv('MODE')
    file_to_predict = os.getenv('FILE_TO_PREDICT')

    # Check if GPU is used
    # print("TensorFlow version:", tf.__version__)
    # print("Is built with CUDA:", tf.test.is_built_with_cuda())
    # print("GPU devices:", tf.config.experimental.list_physical_devices('GPU'))

    try:
        # Initialize database
        database = Database(db_url)
        engine = database.get_engine()
        connection = engine.connect()
        database.init_db()

        pdf_directory = "./data/PDFs"
        mapper = UATMapper("./data/UAT-filtered.json")
        thesaurus = mapper.map_to_thesaurus()

        if (mode == "generate"):
            upload_data(pdf_directory, thesaurus, database)
        elif (mode == "train"):
            # Create a root term
            root_term = thesaurus.get_by_id("1")
            # Iterate over all the children of the root term (We're missing the training for the root term)
            children = thesaurus.get_branch_children("1")
            children.insert(0, root_term)
            for child in children:
                print("Training term id: ", child.get_id())
                process = subprocess.Popen([sys.executable, 'src/train_term.py', child.get_id()])
                process.wait()  # Ensure the process completes before starting the next
                gc.collect()  # Explicitly collect garbage after each process
        elif (mode == "predict"):
            root_term = thesaurus.get_by_id("1")
            predictor = Predictor(root_term.get_id(), file_to_predict)

            predictor.predict()
        
        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
        connection.close()
