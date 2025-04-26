import fitz
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer

equation_fonts = ["TimesLTStd-Roman",
                  "TimesLTStd-BoldItalic",
                   "STIXTwoMath", 
                   "TimesLTStd-Italic", 
                   "EuclidSymbol", 
                   "AdvTTec1d2308.I+03", 
                   "STIXGeneral-Regular", 
                   "EuclidSymbol-Italic",
                   "AdvTTab7e17fd+22",
                   "EuclidMathTwo",
                   "EuclidMathOne",
                   "EuclidExtra",
                   "EuclidSymbol-BoldItalic",
                   "AdvOTb4af3d5d.I",
                   "AdvOT564e738a.BI"
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
    #print(f"String saved to file: {filename}")
  except Exception as e:
    print(f"Error saving string to file: {e}")
    
# Retrieves the text from a page and returns it filtered by different criteria
def get_text_from_page(page, remove_abstract, filename):
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
    # objects_string = json.dumps(page_spans, indent=2)
    # save_string_to_file(objects_string, 'spans1.txt')

    keywords = get_keywords_from_text(page_spans)

    link = ""
    if (page.number == 0):
        # Get the link from the first page
        link = get_link_from_text(page_spans, filename)

    # First filter using the full span element (more properties)
    page_spans = clean_spans_from_page(page_spans, remove_abstract)
    # objects_string2 = json.dumps(page_spans, indent=2)
    # save_string_to_file(objects_string2, 'spans2.txt')

    # The text is reconstructed from the spans without any line breaks
    text = ""
    for span in page_spans:
        text += span["text"] + " "

    return text, bold_text, keywords, link

# Retrieve the title form an article
def get_title_from_file(file_path):
    pdf_document = fitz.open('data/' + file_path)
    page = pdf_document[0]
    blocks = page.get_text("dict")["blocks"]
    spans = []
    bold_text = []
    title = ""
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    spans.append(span)
                    text = span["text"]
                    font_name = span["font"]

                    if "Bold" in font_name or ".B" in font_name or "Black" in font_name:
                        bold_text.append(text)

    i = 0
    while i < len(spans):
        start_index = None
        end_index = None

        for j in range(i, len(spans)):
            if spans[j]["size"] == 13.947600364685059:
                start_index = j
                break

        # Find the ending of the title 
        if start_index is not None:
            for k in range(start_index, len(spans)):
                if spans[k]["size"] != 13.947600364685059:
                    end_index = k
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            for index in range(start_index, end_index):
                if not index == end_index:
                    title += spans[index]["text"] + ' '
                else:
                    title += spans[index]["text"] + '\n'
            break

    pdf_document.close()
    return title

def get_keywords_from_text(spans):
    keywords = []
    i = 0

    while i < len(spans):
        start_index = None
        end_index = None
        # Find an element that matches a "concepts:"
        for j in range(i, len(spans)):
            if ("concepts:" in spans[j]['text']):
                start_index = j
                break

        if start_index is not None:
            for k in range(start_index, len(spans)):
                if spans[k]["text"] == "1. Introduction":
                    end_index = k
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            text = ' '
            for index in range(start_index, end_index):
                text += spans[index]["text"] + ' '
            
            ids = re.findall(r'\d+', text)
            keywords = ids
            break
        else:
            i += 1

    return keywords

def get_link_from_text(spans, file_id):
    link = ""
    i = 0

    while i < len(spans):
        start_index = None
        end_index = None
        # Find an element that matches a "concepts:"
        for j in range(i, len(spans)):
            if ("https:" in spans[j]['text']):
                start_index = j
                break

        if start_index is not None:
            for k in range(start_index, len(spans)):
                if spans[k]["text"] == file_id:
                    end_index = k
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            for index in range(start_index, end_index + 1):
                link += spans[index]["text"]
            break
        else:
            i += 1

    return link

''' Cleans the text by applying a series of text processing functions 
    Params: The plain text of the full article and an array of bold texts
'''
def clean_plain_text(text, bold_text):
    text = replace_special_characters(text)
    text = join_apostrophes(text)
    text = clean_header_from_text(text)
    text = clean_orcidIds_from_text(text)
    text = clean_authors_from_text(text, bold_text)
    text = clean_references_from_text(text)
    text = clean_erratum_from_text(text)
    text = fix_word_breaks(text)
    return text

def join_apostrophes(text):
    text = re.sub(r'(\S)\s’\ss', r"\1's", text) # Join the word with ’ followed by s, converting to 's
    text = re.sub(r'(\S)\s’', r"\1'", text) # Join the word with ’ when it's not followed by s
    return text

def replace_special_characters(text):
    # Join to the previous and next word if there's a single space around "ﬁ"
    text = re.sub(r'(\S)\sﬁ\s(\S)', r'\1fi\2', text)
    
    # Handle case of two spaces after "ﬁ", keep as separate words and remove extra space
    text = re.sub(r'(\S)\sﬁ(\s{2,})(\S)', r'\1fi \3', text)
    
    # Handle case of two spaces before "ﬁ", keep as separate words and remove extra space
    text = re.sub(r'(\s{2,})ﬁ\s(\S)', r' fi\2', text)

    # Join to the previous and next word if there's a single space around "ﬂ"
    text = re.sub(r'(\S)\sﬂ\s(\S)', r'\1fl\2', text)
    
    # Handle case of two spaces after "ﬂ", keep as separate words and remove extra space
    text = re.sub(r'(\S)\sﬂ(\s{2,})(\S)', r'\1fl \3', text)
    
    # Handle case of two spaces before "ﬂ", keep as separate words and remove extra space
    text = re.sub(r'(\s{2,})ﬂ\s(\S)', r' fl\2', text)
    return text

def clean_header_from_text(text):
    header_pattern = r"The (Astrophysical Journal Supplement Series|Astronomical Journal|Astrophysical Journal Letters|Astrophysical Journal)[^.]*\."
    matches = re.finditer(header_pattern, text)
    sections_to_remove = []
    
    for match in matches:
        section = match.group(0)
        # If the match does NOT contain "Unified Astronomy Thesaurus concepts", add it to remove list
        if "Unified Astronomy Thesaurus concepts" not in section:
            sections_to_remove.append(re.escape(section))  # Escape the section for use in the regular expression
    
    if sections_to_remove:
        remove_pattern = "|".join(sections_to_remove)
        text = re.sub(remove_pattern, ".", text)
    return text

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

# Removes all content from the last occurrence of 'References' to the end.
def clean_references_from_text(text):
    last_occurrence = text.rfind("References")
    if last_occurrence != -1:
        return text[:last_occurrence]
    else:
        return text
    
# Removes all content from the last occurrence of 'Erratum' to the end.
def clean_erratum_from_text(text):
    last_occurrence = text.rfind("Erratum")
    if last_occurrence != -1:
        return text[:last_occurrence]
    else:
        return text

# Removes all content from the last occurrence of 'ORCID iDs' to the end."
def clean_orcidIds_from_text(text):
    last_occurrence = text.rfind("ORCID iDs")
    if last_occurrence != -1:
        return text[:last_occurrence]
    else:
        return text

# Fix word breaks when a line finishes with a "-". E.g. "This is a long- " and continues on the next line
def fix_word_breaks(text):
    fixed_text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    return fixed_text

''' Cleans the text as spans by applying a series of text processing functions 
    Params: The spans from each page
'''
def clean_spans_from_page(spans, remove_abstract):
    spans = clean_tables_from_spans(spans)
    spans = clean_urls_from_spans(spans)
    spans = clean_equations_from_spans(spans)
    spans = clean_years_from_spans(spans)
    spans = clean_example_years_from_spans(spans)
    spans = clean_parenthesis_with_years_from_spans(spans)
    spans = clean_small_references_from_spans(spans)
    if (remove_abstract):
        spans = clean_authors_and_abstract_from_spans(spans)
    spans = clean_metadata_from_spans(spans)
    spans = clean_titles_from_spans(spans)
    spans = clean_parenthesis_with_references_from_spans(spans)
    spans = clean_symbols_from_spans(spans)
    spans = clean_orcids_from_spans(spans)
    spans = clean_page_number_from_spans(spans)
    
    return spans

# Removes the tables from the text (Between "Table _number_" and "Note.")
# TODO: Improve the table detection if Note. is not present (Using position?)
def clean_tables_from_spans(spans):
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
            for k in range(start_index + 1, len(spans)):
                if (('References.' in spans[k]['text'] or 'Note.' in spans[k]['text'] or 'Notes.' in spans[k]['text']) and ".B" in spans[j]["font"]):
                    #End table with Note or references
                    end_index = k + 1
                    break
                if re.match(r'^Table \d+', spans[k]['text']) and ".B" in spans[k]["font"]:
                    # Another table
                    end_index = k - 1
                    break

                if re.match(r'^Figure \d+\.', spans[k]['text']) and ".B" in spans[k]["font"]:
                    # A figure
                    end_index = k
                    break
            
                if ('The Astrophysical' in spans[k]['text'] or 'The Astronomical' in spans[k]['text']):
                    # A figure
                    end_index = k
                    for index in range(1, 10):
                        # Check if we reached the end of the document
                        if (k + index >= len(spans)):
                            end_index = k + index - 1
                            break
                        if ('et al' in spans[k+index]['text']):
                            end_index = k + index
                            break
                    break


        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1
        
    return spans

def clean_urls_from_spans(spans):
    # We have to iterate through the spans to find the start and end of the links
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        should_skip = False
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

        if end_index and start_index and (end_index - start_index) >= 8 and text_color == 0 :
            should_skip = True

        if should_skip:
            i = end_index
            start_index = None
            end_index = None
        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans

def clean_equations_from_spans(spans):
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

def clean_years_from_spans(spans):
    # We have to iterate through the spans to find the start and end of the years
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        should_skip = False
        # Find an element that matches a "( "
        for j in range(i, len(spans)):
            if (re.match(r'\s?\(', spans[j]['text']) and re.match(r'\d{4}', spans[j+1]['text']) and re.match(r'\s?\)', spans[j+2]['text'])):
                if (spans[j]['color'] == 255):
                    should_skip = True
                
                start_index = j
                end_index = j + 3
                break

        if should_skip:
            i = end_index
            continue
            
        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans

# Removes examples years in parenthesis like (e.g. Author 2019). BUG: If the first span is ") (" it will not be removed
def clean_example_years_from_spans(spans):
    # We have to iterate through the spans to find the start and end of the years
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        # Find an element that matches a "( "
        for j in range(i, len(spans)):
            words = ["e.g.", "e.g.,"]
            if(re.match(r'\s?\(', spans[j]['text']) and any(words in spans[j+1]['text'] for words in words)):
                start_index = j
                break


        if start_index is not None:
            for k in range(start_index, len(spans)):
                if spans[k]["text"] == ")":
                    end_index = k + 1
                    break

        # If both elements were found, remove the elements between them
        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans

def clean_parenthesis_with_years_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        should_skip = False
        for j in range(i, len(spans)):
            if "(" in spans[j]["text"] and spans[j]["color"] == 0:
                start_index = j
                break

        if start_index is not None:
            for k in range(start_index, len(spans)):
                if ")" in spans[k]['text']:
                    end_index = k + 1
                    if re.search(r'\d{4}', spans[k - 1]['text']):
                        break
                    else:
                        should_skip = True
                        break

        if end_index and start_index and (end_index - start_index) >= 30:
            should_skip = True

        if should_skip:
            i = end_index
            start_index = None
            end_index = None

        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1
    return spans

def clean_small_references_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        for j in range(i, len(spans)):
            if spans[j].get('size') == 7.044162273406982 and spans[j].get('color') == 255:
                start_index = j
                break

        if start_index is not None:
            del spans[start_index:start_index + 1]
            i = start_index 
        else:
            i += 1

    return spans

# Cleans small text like header and footer (e.g. Original content..., Published by..., The Astrophysical Journal...)
def clean_metadata_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        for j in range(i, len(spans)):
            allowed_sizes = [5.977700233459473, 7.970200061798096, 6.339683532714844]
            if spans[j].get('size') in allowed_sizes:
                start_index = j
                break

        if start_index is not None:
            for k in range(start_index, len(spans)):
                 # Reached End of page
                 if (k + 1) == len(spans):
                    end_index = k + 1
                    break
                 # Check if the next element is not a small text
                 disallowed_sizes = [5.977700233459473, 7.970200061798096, 6.339683532714844]
                 if spans[k].get('size') not in disallowed_sizes:
                    # print("REMOVED: ", spans[k]['text'], flush=True)
                    end_index = k
                    break

        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1

    return spans

# Cleans everything between title and text (Abstract, Keywords, Authors). Adds an enter after the title
def clean_authors_and_abstract_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        # Find the end of the title text
        for j in range(i, len(spans)):
            if (spans[j].get('size') == 13.947600364685059 and ".B" in spans[j]["font"] and ".B" not in spans[j + 1]["font"]):                
                start_index = j + 1
                break
            # If the abstract occupies more than one page, we need to check for "Introduction" and remove everything until there
            if "1. Introduction" in spans[j]['text']:
                start_index = 0
                end_index = j + 1
                del spans[start_index:end_index]
                return spans

        if start_index is not None:
            for k in range(start_index, len(spans)):
                if "1. Introduction" in spans[k]['text']:
                    end_index = k + 1
                    break

        # If the abstract occupies more than one page, we need to remove everything until the end of the page from the title
        if end_index is None:
            end_index = len(spans)

        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            
            # Create line break span
            empty_span = {
                "text": "\n",
                "size": 13.947600364685059,
                "font": "TimesLTStd-Roman",
                "color": 0
            }
            spans.insert(start_index, empty_span)

            i = start_index
        else:
            i += 1
    return spans

# Cleans titles and subtitles from the text (Sections, subsections)
def clean_titles_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        # Find the end of the title text
        for j in range(i, len(spans)):
            # Find "1. Introduction" in bold or "1.1. Introduction" in italic
            if ((re.match(r'^\d+\.\s', spans[j]['text']) and ".B" in spans[j]["font"]) or
                ("Appendix" in spans[j]['text'] and ".B" in spans[j]["font"]) or
                (re.match(r'^\d+\.\d+\.\s', spans[j]['text']) and ".I" in spans[j]["font"])):
                start_index = j
                break

        if start_index is not None:
            del spans[start_index:start_index + 1]
            i = start_index 
        else:
            i += 1

    return spans

# Cleans parenthesis with references from the text like "(see Figure 5)"
def clean_parenthesis_with_references_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        # Find the start of parenthesis and the word "see "
        for j in range(i, len(spans) - 1):
            words = ["see", "Figure", "Figures", "Table", "Section"]
            if ("(" in spans[j]["text"] and any(word in spans[j + 1]["text"] for word in words)):
                start_index = j
                break

        if start_index is not None:
            for k in range(start_index, len(spans)):
                # Find the end of the parenthesis. If there's another parenthesis inside, skip it. E.g. (see Figure 5(a), left)
                if ")" in spans[k]["text"] and "(" not in spans[k - 2]["text"]:
                    end_index = k + 1
                    break

        if start_index is not None and end_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1
    return spans

# Cleans symbols like (Greater-than or equal to) and (Less-than or equal to) that are not displayed correctly
def clean_symbols_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        # Find the end of the title text
        for j in range(i, len(spans)):
            # Find weird simbols like (Greater-than or equal to) and (Less-than or equal to)
            symbols = ["\uf088", "\uf089", "\u0084", "\u0085", "\uf0d1"]
            if (any(symbol in spans[j]['text'] for symbol in symbols)):
                start_index = j
                break

        if start_index is not None:
            del spans[start_index:start_index + 1]
            i = start_index 
        else:
            i += 1

    return spans

# Clean the ORCID iDs from the text (Probably in last page). From the start of the ORCID iDs to the end of the page
def clean_orcids_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        end_index = None
        # Find the start of parenthesis and the word "see "
        for j in range(i, len(spans)):
            if ("ORCID iDs" in spans[j]["text"] and ".B" in spans[j]["font"]):
                start_index = j
                end_index = len(spans)
                break

        if start_index is not None:
            del spans[start_index:end_index]
            i = start_index
        else:
            i += 1
    return spans

# If the last span is a number, it's probably a page number. Remove it
def clean_page_number_from_spans(spans):
    i = 0
    while i < len(spans):
        start_index = None
        for j in range(i, len(spans)):
            if (re.match(r'\d+', spans[j]['text']) and j == len(spans) - 1):
                start_index = j
                break

        if start_index is not None:
            del spans[start_index:start_index + 1]
            i = start_index 
        else:
            i += 1

    return spans

'''
Cleans summarized text by applying a series of text processing functions 
'''
def clean_summarized_text(text):
    text = clean_parentesis_from_text(text)
    return text

def clean_parentesis_from_text(text):
    # Remove everything between parenthesis in text
    text = re.sub(r'\([^)]*\)', '', text)
    return text

# Retrieve the full text from an article removing the unnecessary information
def get_full_text_from_file(file_path, remove_abstract=True, filename=None):
    pdf_document = fitz.open('data/' + file_path)
    full_text = ""
    bold_text = []
    keywords = []
    file_link = ""

    for page_number in range(len(pdf_document)):
        # Numero de pagina - 1 que el pdf
        page = pdf_document[page_number]
        text, bold_text_from_page, keywords_by_page, link_by_page = get_text_from_page(page, remove_abstract, filename)
        # ctrl+shift+p: toggle word wrap para evitar scroll
        bold_text += bold_text_from_page
        keywords += keywords_by_page
        full_text += text + ""
        file_link += link_by_page

    pdf_document.close()
    # save_string_to_file(full_text, 'text1.txt')

    # Second filter using the only the text
    # comentar esto para ver diferencias
    full_text = clean_plain_text(full_text, bold_text)
    # save_string_to_file(full_text, 'text2.txt')

    return full_text, keywords, file_link

# Retrieve the abstract from an article
def get_abstract_from_file(file_path, get_title=False):
    full_text, keywords, _l = get_full_text_from_file(file_path, False)
    regex_pattern = r'Abstract([\s\S]*?)Unified Astronomy Thesaurus concepts:'
    extracted_text = ''
    match = re.search(regex_pattern, full_text)

    if match:
        extracted_text += match.group(1) 

    extracted_text = extracted_text.replace('\n', ' ').strip()

    if get_title:
        extracted_text = get_title_from_file(file_path) + extracted_text
    
    return extracted_text, keywords

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
