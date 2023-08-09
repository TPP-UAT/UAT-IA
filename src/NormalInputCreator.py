import json

class NormalInputCreator:
    def create_input_arrays(self, files_input, keywords):
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
    