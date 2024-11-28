import gc
import subprocess
import sys
import os
from dotenv import load_dotenv
from UATMapper import UATMapper
from Database.Database import Database
from utils.pdfs_terms_parser import upload_data 

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    load_dotenv() # Load environment variables
    db_url = os.getenv('DB_URL')
    mode = os.getenv('MODE')

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
            # children = thesaurus.get_branch_children("1")
            children = []
            children.insert(0, root_term)

            # Only for testing purposes
            # eleven_children = root_term.get_children()
            # for child_id in eleven_children:
            #     children.append(thesaurus.get_by_id(child_id))
            # print("CHILDREN: ", children)
        
            for child in children:
                process = subprocess.Popen([sys.executable, 'src/train_term.py', child.get_id()])
                process.wait()  # Ensure the process completes before starting the next
                gc.collect()  # Explicitly collect garbage after each process
        else:
            print("Invalid mode")
        
        connection.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
        connection.close()
