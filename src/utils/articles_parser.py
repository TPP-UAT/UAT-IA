import fitz
import re
from sklearn.feature_extraction.text import TfidfVectorizer


def get_bold_text_from_page(page):
    bold_text = []
    blocks = page.get_text("dict")["blocks"]

    # page_text = ""
    for block in blocks:
        if "lines" in block:  
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    # page_text += text + " "
                    font_name = span["font"]

                    if "Bold" in font_name or ".B" in font_name or "Black" in font_name:
                        bold_text.append(text)
    return bold_text

# Retrieve the full text from an article
def get_full_text_from_file(file_path):
    pdf_document = fitz.open('data/' + file_path)
    full_text = ""
    bold_texts = []
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = page.get_text()
        full_text += text + "\n\n"

        bold_texts = bold_texts + get_bold_text_from_page(page)

    pdf_document.close()
    full_text = clean_text(full_text, bold_texts)
    return full_text

# Cleans the text by applying a series of text processing functions
def clean_text(text, bold_texts):
    text = clean_urls_from_text(text)
    text = clean_header_from_text(text)
    text = clean_footer_from_text(text)
    text = clean_references_from_text(text)
    text = clean_orcidIds_from_text(text)
    text = clean_authors_from_text(text, bold_texts)

    return text

def clean_header_from_text(text):
 # Pattern to capture the header for different journal names
    header_pattern = r"(The (Astrophysical Journal|Astronomical Journal|Astrophysical Journal Letters|Astrophysical Journal Supplement Series).*)(?:\n\n|\Z)"
    return re.sub(header_pattern, "", text, flags=re.DOTALL)

def clean_footer_from_text(text):
    # Removes footer-like patterns containing publication information
    footer_pattern = r"\bThe (Astrophysical Journal|Astronomical Journal|Astrophysical Journal Letters|Astrophysical Journal Supplement Series).*?(?:\n|\Z)"
    return re.sub(footer_pattern, "", text)

def clean_authors_from_text(text, bold_texts):
    # Find the index of "Abstract" in bold_texts
    try:
        abstract_index = bold_texts.index('Abstract')
    except ValueError:
        # If "Abstract" is not in bold_texts, return the original text
        return text

    # Find the bold text immediately before "Abstract"
    if abstract_index > 0:
        previous_bold_text = bold_texts[abstract_index - 1]
    else:
        # If "Abstract" is the first item, there is no previous bold text
        return text

    # Find the start index of the previous bold text in the text
    start_index = text.find(previous_bold_text)
    if start_index == -1:
        # If the previous bold text is not found in the text, return the original text
        return text

    # Find the start index of "Abstract"
    abstract_start_index = text.find('Abstract', start_index)
    if abstract_start_index == -1:
        # If "Abstract" is not found after the previous bold text, return the original text
        return text

    # Remove text between the end of the previous bold text and the start of "Abstract"
    end_of_previous_bold = start_index + len(previous_bold_text)
    
    result_text = text[:end_of_previous_bold] + "\n" + text[abstract_start_index:]

    return result_text


def clean_references_from_text(text):
    #Removes all content from the last occurrence of 'References' to the end.
    last_occurrence = text.rfind("References")
    if last_occurrence != -1:
        return text[:last_occurrence]
    else:
        return text

def clean_urls_from_text(text):
    # Removes URLs and DOIs
    urls_pattern = r"https?://\S+|doi:\S+"
    return re.sub(urls_pattern, "", text)

def clean_orcidIds_from_text(text):
    #Removes all content from the last occurrence of 'ORCID iDs' to the end."
    last_occurrence = text.rfind("ORCID iDs")
    if last_occurrence != -1:
        return text[:last_occurrence]
    else:
        return text

# Retrieve the abstract from an article
def get_abstract_from_file(file_path):
    full_text = get_full_text_from_file(file_path)
    regex_pattern = r'Abstract([\s\S]*?)Uniﬁed Astronomy Thesaurus concepts:'
    extracted_text = ''
    match = re.search(regex_pattern, full_text)

    if match:
        extracted_text += match.group(1) 

    extracted_text = extracted_text.replace('\n', ' ').strip()
    return extracted_text

def get_keywords_from_file(file_path):
    regex = r'Uniﬁed Astronomy Thesaurus concepts:\s*((?:[^;)]+\(\d+\);\s*)+[^;)]+\(\d+\))' # regex pattern to find URLs
    text = get_full_text_from_file(file_path)
    terms = re.findall(regex, text)
    ids = []
    if len(terms) > 0:
        concepts = terms[0]  # Assuming there's only one match per page

        # Find the IDs in the terms
        ids = re.findall(r'\((\d+)\)', concepts)
    return ids
    

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
