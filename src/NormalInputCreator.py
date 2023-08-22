import fitz

class NormalInputCreator:
    def create_input_arrays(self, files_input, keywords):
        texts = []
        keywords_by_text = []

        for file_path, file_input in files_input.items():
            try:
                pdf_document = fitz.open('data/' + file_path)
                full_text = []
                for page_number in range(len(pdf_document)):
                    page = pdf_document[page_number]
                    text = page.get_text()

                    full_text.append(text)
                texts.append(full_text)
                keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        return texts, keywords_by_text
    