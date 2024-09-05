import fitz
import re
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer

equation_fonts = ["TimesLTStd-Roman",
                   "STIXTwoMath", 
                   "TimesLTStd-Italic", 
                   "EuclidSymbol", 
                   "AdvTTec1d2308.I+03", 
                   "STIXGeneral-Regular", 
                   "EuclidSymbol-Italic",
                   "AdvTTab7e17fd+22",
                   "EuclidMathTwo"
                   ]

# TODO: Delete this function
def save_string_to_file(string, filename):
  """Saves a string to a file.

  Args:
    string: The string to be saved.
    filename: The name of the file to be created.
  """

  try:
    with open(filename, 'w') as file:
      file.write(string)
    print(f"String saved to file: {filename}")
  except Exception as e:
    print(f"Error saving string to file: {e}")
    
# Retrieves the text from a page and returns it filtered by different criteria
def get_text_from_page(page):
    blocks = page.get_text("dict")["blocks"]

    page_spans = []
    bold_text = []
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    page_spans.append(span)
                    text = span["text"]
                    font_name = span["font"]

                    if "Bold" in font_name or ".B" in font_name or "Black" in font_name:
                        bold_text.append(text)
    
    # Guarda los spans en un archivo
    objects_string = json.dumps(page_spans, indent=2)
    save_string_to_file(objects_string, 'spans.txt')

    # First filter using the full span element (more properties)
    # comentar esto para ver diferencias
    page_spans = clean_spans_from_page(page_spans)

    # The text is reconstructed from the spans without any line breaks
    text = ""
    for span in page_spans:
        text += span["text"] + " "

    return text, bold_text

# Retrieve the full text from an article removing the unnecessary information
def get_full_text_from_file(file_path):
    pdf_document = fitz.open('data/' + file_path)
    full_text = ""
    bold_text = []
    for page_number in range(1):
        # Numero de pagina - 1 que el pdf
        page = pdf_document[1]
        text, bold_text_from_page = get_text_from_page(page)
        # text = page.get_text()

        # ctrl+shift+p: toggle word wrap para evitar scroll
        save_string_to_file(text, 'text.txt')

        # bold_text.append(bold_text_from_page)
        full_text += text + "\n\n"

    pdf_document.close()

    # Second filter using the only the text
    # comentar esto para ver diferencias
    # full_text = clean_plain_text(full_text, bold_text)
    return full_text

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

''' Cleans the text by applying a series of text processing functions 
    Params: The plain text of the full article and an array of bold texts
'''
def clean_plain_text(text, bold_text):
    #text = clean_header_from_text(text)
    # text = clean_footer_from_text(text)
   
    #text = clean_authors_from_text(text)
    # text = clean_references_from_text(text)
    # text = clean_urls_from_text(text)
    return text

def clean_header_from_text(text):
 # Pattern to capture the header for different journal names
    header_pattern = r"(The (Astrophysical Journal|Astronomical Journal|Astrophysical Journal Letters|Astrophysical Journal Supplement Series).*)(?:\n\n|\Z)"
    return re.sub(header_pattern, "", text, flags=re.DOTALL)

def clean_footer_from_text(text):
    # Removes footer-like patterns containing publication information
    footer_pattern = r"\bThe Astrophysical Journal.*?\b(?:\n|\Z)"
    return re.sub(footer_pattern, "", text)

def clean_authors_from_text(text):
    # Removes author names and affiliations
    authors_pattern = r"(?:^|\n)(?:[A-Z]\.\s?[A-Za-z]+,\s?)+\n(?:[A-Za-z,]+\s?)+"
    return re.sub(authors_pattern, "", text)

def clean_references_from_text(text):
    # Removes references to sections, papers, or figures
    references_pattern = r"\(.*?Sections?.*?\)|\[.*?\]"
    return re.sub(references_pattern, "", text)
    
''' Cleans the text as spans by applying a series of text processing functions 
    Params: The spans from each page
'''
def clean_spans_from_page(spans):
    spans = clean_tables_from_text(spans)
    spans = clean_urls_from_text(spans)
    spans = clean_equations_from_text(spans)
    spans = clean_years_from_text(spans)
    
    return spans

# Removes the tables from the text (Between "Table _number_" and "Note.")
# TODO: Improve the table detection if Note. is not present (Using position?)
def clean_tables_from_text(spans):
    # We have to iterate through the spans to find the start and end of the tables
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None

        # Find an element that matches "Table _number_"
        for j in range(i, len(spans)):
            if re.match(r'^Table \d+', spans[j]['text']) and ".B" in spans[j]["font"]:
                start_index = j
                break

        # Find an element that matches "Note. (This usually indicates the end of the table)"
        if start_index is not None:        
            for k in range(start_index, len(spans)):
                if spans[k]['text'] == 'Note.' and ".B" in spans[j]["font"]:
                    end_index = k + 1
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1
        
    return spans

def clean_urls_from_text(spans):
    # We have to iterate through the spans to find the start and end of the links
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        text_color = 0

        # Find an element that matches a URL
        for j in range(i, len(spans)):
            if "http" in spans[j]["text"]:
                start_index = j
                text_color = spans[j]["color"]
                break

        # Find the ending of the URL 
        if start_index is not None:
            for k in range(start_index, len(spans)):
                if spans[k]['color'] != text_color:
                    end_index = k
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans

def clean_equations_from_text(spans):
    # We have to iterate through the spans to find the start and end of the equations
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None

        # Find an element that matches an equation (It has a different font)
        # If it's only one line, it's not an equation
        for j in range(i, len(spans)):
            if spans[j]["font"] in equation_fonts:
                start_index = j
                break

        # Find the ending of the equation 
        if start_index is not None:
            for k in range(start_index, len(spans)):
                if spans[k]["font"] not in equation_fonts:
                    end_index = k
                    if (end_index - start_index) < 2:
                        start_index = None
                        end_index = None
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans

def clean_years_from_text(spans):
    # We have to iterate through the spans to find the start and end of the years
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None

        # Find an element that matches a "( "
        for j in range(i, len(spans)):
            if (re.match(r'\s?\(', spans[j]['text']) and re.match(r'\d{4}', spans[j+1]['text']) and re.match(r'\s?\)', spans[j+2]['text'])):
                start_index = j
                end_index = j + 3
                break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans