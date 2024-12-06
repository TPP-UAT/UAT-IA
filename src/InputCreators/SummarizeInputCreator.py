from Database.File import File
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from collections import Counter
from utils.articles_parser import clean_summarized_text

class SummarizeInputCreator:
    def __init__(self, database = None):
        self.folder_name = 'summarize'
        self.nlp = spacy.load('en_core_web_md')

        # Database connection
        self.database = database
        self.file_db = File(database)

    def get_folder_name(self):
        return self.folder_name
    
    def summarize_text(self, text, percentage=0.15, max_sentences=10, additional_stopwords=None):
        """
        Summarizes a scientific article, ensuring clarity, conciseness, and coherent starting points.

        Parameters:
        - text (str): The text to summarize.
        - percentage (float): Proportion of sentences to include in the summary (default: 15%).
        - max_sentences (int): Maximum number of sentences in the summary (default: 10).
        - additional_stopwords (set): Custom stopwords to exclude from frequency calculation (optional).

        Returns:
        - str: A concise and coherent summary.
        """
        if not text.strip():
            return "The provided text is empty or invalid."

        # Clean the text and remove unnecessary content
        text = clean_summarized_text(text)
        
        # Process the text with spaCy
        doc = self.nlp(text)

        # Combine default and additional stopwords
        stop_words = STOP_WORDS.union(additional_stopwords or set())

        # Calculate word frequencies, ignoring stopwords, punctuation, and numerical tokens
        word_frequencies = Counter(
            token.text.lower() for token in doc
            if token.text.lower() not in stop_words
            and token.text not in punctuation
            and not token.is_digit
        )

        # Normalize word frequencies
        max_freq = max(word_frequencies.values(), default=1)
        word_frequencies = {word: freq / max_freq for word, freq in word_frequencies.items()}

        # Score sentences based on word frequencies and named entities
        sentence_scores = {}
        for sent in doc.sents:
            token_count = 0
            sent_score = 0

            for token in sent:
                word_lower = token.text.lower()
                if word_lower in word_frequencies:
                    sent_score += word_frequencies[word_lower]
                    token_count += 1

                # Boost scores for named entities or scientific terms
                if token.ent_type_ in {"PERSON", "ORG", "GPE", "DATE", "NORP", "FAC"} or token.pos_ in {"NOUN", "PROPN"}:
                    sent_score += 2

            if token_count > 0:
                sentence_scores[sent] = sent_score / token_count

        # Find the most suitable introductory sentence
        intro_sentences = [
            sent for sent in doc.sents if "phenomenon" in sent.text.lower() or "X-ray" in sent.text.lower()
        ]
        if intro_sentences:
            starting_sentence = max(intro_sentences, key=lambda sent: sentence_scores.get(sent, 0))
        else:
            starting_sentence = max(doc.sents, key=lambda sent: sentence_scores.get(sent, 0))

        # Filter out irrelevant or overly short sentences
        filtered_sentences = {
            sent: score for sent, score in sentence_scores.items()
            if len(sent.text.split()) > 8
            and not any(keyword in sent.text.lower() for keyword in ["appendix", "section", "figure", "license", "acknowledgment"])
        }

        # Determine the number of sentences dynamically
        total_sentences = len(list(doc.sents))
        num_sentences = min(max_sentences, max(3, int(total_sentences * percentage)))

        # Select top sentences based on scores
        selected_sentences = nlargest(num_sentences, filtered_sentences, key=filtered_sentences.get)

        # Ensure the starting sentence is included
        if starting_sentence and starting_sentence not in selected_sentences:
            selected_sentences = [starting_sentence] + selected_sentences[:-1]

        # Sort sentences by their order in the original text
        final_summary = sorted(selected_sentences, key=lambda s: list(doc.sents).index(s))

        # Remove duplicates and create the summary
        seen = set()
        unique_sentences = [
            sent.text.strip() for sent in final_summary
            if sent.text.strip() not in seen and not seen.add(sent.text.strip())
        ]

        # Join selected sentences into a coherent summary
        summary = " ".join(unique_sentences)

        # Handle cases where no valid sentences are selected
        if not summary:
            return "No suitable summary could be generated from the given text."

        return summary

    def get_file_data_input(self, file_id):
        try:
            summarized_text = self.file_db.get_summarized_text_by_file_id(file_id)
            return summarized_text
        except:
            print("Error trying to load file with path: ", file_id)