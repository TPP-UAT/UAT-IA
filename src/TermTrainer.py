import json

class TermTrainer:
    def __init__(self, training_files):
        self.training_files = training_files

    def create_input_arrays(self, files_input):
        texts = []
        keywords_by_text = []

        for file_path, file_input in files_input.items():
            try:
                file = json.load(open(file_path))
                texts.append(file['text'])
                keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        return texts, keywords_by_text
    
    '''
        Creates the input data for the training as two arrays:
        - texts: array of texts for traning
        - keywords_by_text: array of arrays of keywords for each text. 1 if it matches the keyword, 0 if not
    '''
    def create_data_input(self, group_of_term_files):
        # The index of the keyword matches the position of the training input { 'term_id': index }
        # E.g. { '54': 0, '23': 1, '457': 2, '241': 3 }
        keywords_indexes = {}
        for i in range(len(group_of_term_files)):
            keywords_indexes[group_of_term_files[i]] = i
        files_input = {}

        for term_files in group_of_term_files:
            files_paths = term_files.get_files_paths()
            for file_path in files_paths:
                # If the file_path is not in files_input dictionary, creates a new item with the path as the key and an input array filled with 0s
                if file_path not in files_input:
                    files_input[file_path] = [0] * len(group_of_term_files)
                files_input[file_path][keywords_indexes[term_files]] = 1

        return self.create_input_arrays(files_input)

    def train_group(self, group_of_term_files):
        texts, keywords_by_text = self.create_data_input(group_of_term_files)
        print("Texts: ", texts)
        print("Keywords by text: ", keywords_by_text)
