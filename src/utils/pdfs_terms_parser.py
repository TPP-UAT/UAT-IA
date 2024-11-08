import fitz
import re
import json
import os
import logging

from Database.File import File
from Database.Keyword import Keyword
from utils.articles_parser import get_abstract_from_file

PDFS_PATH = './PDFs'

# Logging, change log level if needed
logging.basicConfig(filename='logs/file_generation.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger('my_logger')

def count_files(pdf_directory):
    count = 0
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            count += 1
    return count

def upload_data(pdf_directory, thesaurus, database):
    file_db = File(database)
    keyword_db = Keyword(database)

    root_term = thesaurus.get_by_id("1")
    root_term_children = root_term.get_children()

    root_term_grandchildren = []

    for children_id in root_term_children:
        try:
            children_of_children = thesaurus.get_by_id(children_id).get_children()
            for grandchild_id in children_of_children:
                root_term_grandchildren.append(grandchild_id)
        except Exception as e:
            log.error(f"Error processing children of {children_id}: {e}")
            continue

    file_count = count_files(pdf_directory)
    log.info(f"Saving in db with {file_count} files.")

    count = 0
    for filename in os.listdir(pdf_directory):
        if (count % 50 == 0):
            log.info(f"Processing file {count} of {file_count}")

        if filename.endswith(".pdf"):
            try:
                file_id = filename.replace(".pdf", "")
                pdf_file_path = os.path.join(pdf_directory, filename)
                file_path = os.path.join("PDFs", filename)

                # Open the PDF file
                pdf_document = fitz.open(pdf_file_path)
                print("Processing file ID:", filename)
                log.info(f"Processing file ID: {filename}")

                # Get the necessary information from the PDF file
                full_text = ""  # Aquí no se utiliza get_full_text_from_file
                abstract, keywords = get_abstract_from_file(file_path, True)

                result = file_db.add(file_id=file_id, abstract=abstract, full_text=full_text)
                if result != False:
                    for keyword in keywords:
                        if keyword in root_term_children or keyword in root_term_grandchildren:
                            keyword_db.add(file_id=file_id, keyword_id=keyword, order=1)
                        else:
                            keyword_db.add(file_id=file_id, keyword_id=keyword, order=2)

                pdf_document.close()
                count += 1

            except Exception as e:
                # Guardar el nombre del archivo que generó el error junto con el error en el log
                log.error(f"Error processing file {filename}: {e}")
                continue

    # Iterates over all the keywords_ids of the thesaurus and if does not exist, saves the keywords with empty documents
    try:
        all_keywords_id = list(thesaurus.get_terms().keys())
        for keyword_id in all_keywords_id:
            count = keyword_db.get_count_by_keyword_id(keyword_id)
            if count == 0:
                keyword_db.add(keyword_id=keyword_id, file_id=None, order=2)
    except Exception as e:
        log.error(f"Error processing keywords: {e}")