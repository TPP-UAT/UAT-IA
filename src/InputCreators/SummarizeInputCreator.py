from Database.File import File
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from collections import Counter


class SummarizeInputCreator:
    def __init__(self, database = None):
        self.folder_name = 'summarize'
        self.nlp = spacy.load('en_core_web_md')

        # Database connection
        self.database = database
        self.file_db = File(database)

    def get_folder_name(self):
        return self.folder_name
    
    def summarize_text(self, text, percentage=0.1):
# Process the text with spaCy
        doc = self.nlp(text)
        
        # Tokenize and calculate word frequencies, ignoring stopwords and punctuation
        word_frequencies = Counter(
            token.text.lower() for token in doc 
            if token.text.lower() not in STOP_WORDS and token.text not in punctuation
        )
        
        # Normalize the frequencies by dividing by the maximum frequency
        max_freq = max(word_frequencies.values(), default=1)
        for word in word_frequencies.keys():
            word_frequencies[word] /= max_freq

        # Score sentences based on word frequencies and named entity presence
        sentence_scores = {}
        for sent in doc.sents:
            sent_score = 0
            for token in sent:
                word_lower = token.text.lower()
                if word_lower in word_frequencies:
                    sent_score += word_frequencies[word_lower]
                # Add extra weight for sentences with named entities
                if token.ent_type_ in {"PERSON", "ORG", "GPE", "DATE"}:
                    sent_score += 1
            # Store the sentence and its score
            sentence_scores[sent] = sent_score

        # Determine the number of sentences to include in the summary
        num_sentences = max(1, int(len(list(doc.sents)) * percentage))
        
        # Select the top sentences based on their scores
        selected_sentences = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        
        # Sort the selected sentences by their order in the original text
        final_summary = sorted(selected_sentences, key=lambda s: list(doc.sents).index(s))
        
        # Convert the summary sentences into a single string
        summary_text = " ".join([sent.text for sent in final_summary])
        
        return summary_text

    def get_file_data_input(self, file_id):
        try:
            full_text = self.file_db.get_full_text_by_file_id(file_id)
            summarized_text = self.summarize_text(full_text)
            return summarized_text
        except:
            print("Error trying to load file with path: ", file_id)