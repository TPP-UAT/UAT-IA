import gc
from UATMapper import UATMapper
from Trainer import Trainer
import sys

if __name__ == "__main__":
    term_id = sys.argv[1]

    gc.set_debug(gc.DEBUG_SAVEALL)

    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()
    
    trainer = Trainer(thesaurus)
    trainer.train_by_term_id(term_id)
