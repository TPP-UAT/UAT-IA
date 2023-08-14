import json
from transformers import BartForConditionalGeneration, BartTokenizer


class SummarizeInputCreator:

    def summarize_text(self, text):
        print('text: ', text)
        # Cargar el modelo y el tokenizador
        model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
        tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

        test = 'aaaaa'
        # Tokenizar y generar resumen abstractivo
        inputs = tokenizer.encode("summarize: " + test, return_tensors="pt", max_length=1024, truncation=True)
        print('1')
        summary_ids = model.generate(inputs, max_length=300, min_length=100, length_penalty=1.5, num_beams=4, early_stopping=True)
        print('2')
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print('summary: ', summary)
        return summary

    def create_input_arrays(self, files_input, keywords):
        texts = []
        keywords_by_text = []

        for file_path, file_input in files_input.items():
            try:
                file = json.load(open(file_path))
                summarized_text = self.summarize_text(file['text'])
                print("Summarize: ", summarized_text)
                texts.append(summarized_text)
                keywords_by_text.append(file_input)
            except:
                print("Error trying to load file with path: ", file_path)

        return texts, keywords_by_text
