from UATMapper import UATMapper
import json
from TrainingFiles import TrainingFiles
from TermFiles import TermFiles

def create_training_files(thesaurus):
    json_data = json.load(open('./data/training_files.json'))

    training_files = TrainingFiles()
    for key, term_files in json_data.items():
        term_files = TermFiles(key, term_files["files"], thesaurus.get_by_id(key).get_children())
        training_files.add_term_files(term_files)

    return training_files


if __name__ == '__main__':
    mapper = UATMapper("./data/UAT.json")
    thesaurus = mapper.map_to_thesaurus()

    branch_tesaurus = thesaurus.get_branch('972')

    branch_tesaurus.print_names_and_ids()

    training_files = create_training_files(branch_tesaurus)
    print(training_files.get_term_files())
