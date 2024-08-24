from utils.articles_parser import get_abstract_from_file

class AbstractInputCreator:
    def __init__(self, thesaurus):
        self.folder_name = 'abstract'
        self.thesaurus = thesaurus

    def get_folder_name(self):
        return self.folder_name

    def create_input_arrays(self, files_input, keywords):
        texts = []
        keywords_by_text = []

        for file_path, file_input in files_input.items():
            try:
                abstract_text = get_abstract_from_file(file_path)
                if abstract_text:
                    texts.append(abstract_text)
                    keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        # TODO: Delete duplicates from texts, keep consistency in keywords_by_text
        return texts, keywords_by_text
    