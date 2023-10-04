import json
from sklearn.feature_extraction.text import TfidfVectorizer
import fitz
import re

class AbstractInputCreator:

    def get_abstract(self, text):
        regex_pattern = r'Abstract([\s\S]*?)Uniﬁed Astronomy Thesaurus concepts:'
        extracted_text = ''
        match = re.search(regex_pattern, text[0])

        if match:
            extracted_text += match.group(1) 

        return extracted_text

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
                
                abstract_text = self.get_abstract([full_text[0]])
                if abstract_text:
                    texts.append(abstract_text)
                    keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        # TODO: Delete duplicates from texts, keep consistency in keywords_by_text
        return texts, keywords_by_text
    