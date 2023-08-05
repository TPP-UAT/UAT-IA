from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer

if __name__ == '__main__':
    mapper = UATMapper("./data/UAT.json")
    thesaurus = mapper.map_to_thesaurus()

    branch_tesaurus = thesaurus.get_branch('972')

    term_file_mapper = TermFileMapper()
    term_file_mapper.create_training_files(branch_tesaurus)

    training_files = term_file_mapper.get_training_files()
    term_files = training_files.get_term_files()

    for key, term_file in term_files.items():
        print(key, term_file.get_files_paths(), term_file.get_children())


    print("Training files Size: ", training_files.get_size())
    print("Thesaurus Size: ", branch_tesaurus.get_size())

    children = branch_tesaurus.get_by_id('975').get_children()
    group_of_term_files = []
    for child in children:
        term_file = training_files.get_by_id(child)
        group_of_term_files.append(term_file)

    term_trainer = TermTrainer(training_files)
    term_trainer.train_group(group_of_term_files)


