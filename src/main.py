from UATMapper import UATMapper
import json
from TrainingFiles import TrainingFiles
from TermFiles import TermFiles
from TermFileMapper import TermFileMapper

'''
def create_training_files(thesaurus):
    json_data = json.load(open('./data/training_files.json'))

    training_files = TrainingFiles()
    for key, term_files in json_data.items():
        term_files = TermFiles(key, term_files["files"], thesaurus.get_by_id(key).get_children())
        training_files.add_term_files(term_files)

    return training_files
'''

if __name__ == '__main__':
    mapper = UATMapper("./data/UAT.json")
    thesaurus = mapper.map_to_thesaurus()

    branch_tesaurus = thesaurus.get_branch('972')

    term_file_mapper = TermFileMapper()
    term_file_mapper.create_training_files(branch_tesaurus)

    training_files = term_file_mapper.get_training_files()
    term_files = training_files.get_term_files()
    for key, term_file in term_files.items():
        print(key, term_file.get_files(), term_file.get_children())

    print("Training files Size: ", training_files.get_size())
    print("Thesaurus Size: ", branch_tesaurus.get_size())