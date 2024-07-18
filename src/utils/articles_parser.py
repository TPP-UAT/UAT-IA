import fitz
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from Constants import data_directory

# Retrieve the full text from an article
def get_full_text_from_file(file_path):
    pdf_document = fitz.open(data_directory + file_path)
    full_text = []
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = page.get_text()

        full_text.append(text)
    
    pdf_document.close()
    return full_text[0]

# Retrieve the abstract from an article
def get_abstract_from_file(file_path):
    full_text = get_full_text_from_file(file_path)

    regex_pattern = r'Abstract([\s\S]*?)Uniﬁed Astronomy Thesaurus concepts:'
    extracted_text = ''
    match = re.search(regex_pattern, full_text)

    if match:
        extracted_text += match.group(1) 

    return extracted_text

# Retrieve the top 50 words from an article based on TF-IDF
# keywords_by_word is a list of words that will be given a higher TF-IDF value, [] if not used
def get_tf_idf_words_from_file(file_path, keywords_by_word):
    full_text = get_full_text_from_file(file_path)

    COMMON_WORDS = ['et', 'al', 'in', 'be', 'at', 'has', 'that', 'can', 'was', 'its', 'both', 'may', 'we', 'not', 'will', 'or', 'it', 'they', 'than', 'these', 'however', 'co', 'from', 'an', 'ah', 'for', "by", "would", "also", "to", 'and', 'the', 'this', "of", "the", "on", "as", "with", "our", "are", "is"]
    words_quantity = 50

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([full_text])
    terms = vectorizer.get_feature_names_out()
    common_indices = [terms.tolist().index(word) for word in COMMON_WORDS if word in terms]

    # Set the TF-IDF values of the common words to 0
    for i in range(len(X.toarray())):
        for idx in common_indices:
            X[i, idx] = 0.0

    # If keywords_by_word is not empty, increase the TF-IDF value of the words in the list
    X_modified = X.toarray()
    for i in range(len(full_text)):
        for word in keywords_by_word:
            word_lower = word.lower() 
            if word_lower in terms:
                idx = terms.tolist().index(word_lower)
                tfidf_value = X_modified[i, idx]
                new_tfidf_value = tfidf_value * 2
                X_modified[i, idx] = new_tfidf_value

    top_words_per_document = []
    for doc_tfidf in X_modified:
        top_word_indices = doc_tfidf.argsort()[-words_quantity:][::-1]
        top_words = [(terms[i], doc_tfidf[i]) for i in top_word_indices]
        top_words_per_document.append(top_words)

    top_words_strings = []
    for doc_tfidf in X_modified:
        top_word_indices = doc_tfidf.argsort()[-words_quantity:][::-1]
        top_words = [terms[i] for i in top_word_indices]
        top_words_string = ' '.join(top_words)
        top_words_strings.append(top_words_string)

    return top_words_strings
