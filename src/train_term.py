import gc
import sys
import os
from dotenv import load_dotenv

from Trainer import Trainer
from UATMapper import UATMapper
from Database.Database import Database

if __name__ == "__main__":
    load_dotenv() # Load environment variables
    term_id = sys.argv[1]

    gc.set_debug(gc.DEBUG_SAVEALL)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # Database connection
    db_url = os.getenv('DB_URL')
    database = Database(db_url)
    engine = database.get_engine()
    connection = engine.connect()
    database.init_db()

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()
    
    trainer = Trainer(thesaurus, database)
    trainer.train_by_term_id(term_id)

    connection.close()
