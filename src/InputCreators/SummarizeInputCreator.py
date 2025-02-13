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
        self.nlp = spacy.load('en_core_web_lg')

        # Database connection
        self.database = database
        self.file_db = File(database)

    def get_folder_name(self):
        return self.folder_name

    def _remove_consecutive_repeats(self, text, max_repeats=3):
        """Remove words/numbers/symbols that are repeated consecutively more than max_repeats times."""
        words = text.split()
        cleaned_words = []
        repeat_count = 1
        
        for i in range(len(words)):
            if i > 0 and words[i] == words[i-1]:
                repeat_count += 1
            else:
                repeat_count = 1
                
            if repeat_count <= max_repeats:
                cleaned_words.append(words[i])
                
        return ' '.join(cleaned_words)

    def _remove_figure_sentences(self, text):
        """Remove sentences that contain the word 'Figure'."""
        sentences = text.split('.')
        cleaned_sentences = []
        
        for sentence in sentences:
            if 'Figure' not in sentence and 'figure' not in sentence:
                cleaned_sentences.append(sentence)
                
        return '.'.join(cleaned_sentences)

    def summarize_text(self, text, min_chars=5000, max_chars=7000, additional_stopwords=None):
        """
        Summarizes a scientific article with improved coherence and generalization.

        Parameters:
        - text (str): The text to summarize
        - min_chars (int): Minimum character length for the summary (default: 4000)
        - max_chars (int): Maximum character length for the summary (default: 6000)
        - additional_stopwords (set): Custom stopwords to exclude from frequency calculation (optional)

        Returns:
        - str: A structured summary within the specified length range
        """
        if not text.strip():
            return "The provided text is empty or invalid."

        # Pre-process text to remove figures and repeated elements
        text = self._remove_figure_sentences(text)
        text = self._remove_consecutive_repeats(text)

        # Clean the text
        text = clean_summarized_text(text)

        # Process text with spaCy
        doc = self.nlp(text)

        # Define stopwords dynamically
        stop_words = STOP_WORDS.union(additional_stopwords or set())

        # Compute word frequencies while prioritizing key terms
        word_frequencies = Counter()
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.like_num and
                token.pos_ in {'NOUN', 'PROPN', 'VERB', 'ADJ'}):
                word_frequencies[token.lemma_] += 1

        # Normalize frequencies
        max_freq = max(word_frequencies.values(), default=1)
        word_frequencies = {word: freq / max_freq for word, freq in word_frequencies.items()}

        # Sentence scoring
        sentence_scores = {}
        for sent in doc.sents:
            if len(sent.text.split()) < 5:  # Skip very short sentences
                continue

            score = sum(word_frequencies.get(token.lemma_, 0) for token in sent)

            # Boost scores for sentences with scientific indicators
            scientific_indicators = {'study', 'research', 'analysis', 'results', 'findings', 'method', 'experiment'}
            if any(word in sent.text.lower() for word in scientific_indicators):
                score *= 1.3

            sentence_scores[sent] = score

        # Select top-ranked sentences dynamically
        selected_sentences = []
        current_length = 0
        sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)

        for sent, _ in sorted_sentences:
            if current_length >= max_chars:
                break

            sent_text = sent.text.strip()
            if sent_text not in {s.text.strip() for s in selected_sentences}:  # Avoid duplicates
                # Additional check for repeated elements in the sentence
                cleaned_sent = self._remove_consecutive_repeats(sent_text)
                if cleaned_sent and 'Figure' not in cleaned_sent and 'figure' not in cleaned_sent:
                    selected_sentences.append(sent)
                    current_length += len(cleaned_sent) + 1  # +1 for space

            if min_chars <= current_length <= max_chars:
                break

        # Sort sentences by their original order
        selected_sentences.sort(key=lambda s: s.start)

        # Join sentences with proper formatting and do final cleaning
        summary = ' '.join(sent.text.strip() for sent in selected_sentences)
        summary = self._remove_consecutive_repeats(summary)  # Final check for repeats
        
        # Final length check
        if len(summary) > max_chars:
            while len(summary) > max_chars and len(selected_sentences) > 1:
                selected_sentences.pop()
                summary = ' '.join(s.text.strip() for s in selected_sentences)
                summary = self._remove_consecutive_repeats(summary)

        return summary if summary else "Could not generate a suitable summary."

    def get_file_data_input(self, file_id):
        """
        Retrieves summarized data for a given file.
        """
        try:
            return self.file_db.get_summarized_text_by_file_id(file_id)
        except Exception as e:
            print(f"Error loading file with ID {file_id}: {str(e)}")
            return None
