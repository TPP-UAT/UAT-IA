import os
import re
import fitz  # PyMuPDF
import logging

# Configure logging
logging.basicConfig(filename='no_keyword_files_deleted.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the folder path and regex pattern
root_folder_path = os.getenv('DATA_PATH')
regex = r'Uniﬁed Astronomy Thesaurus concepts:\s*((?:[^;)]+\(\d+\);\s*)+[^;)]+\(\d+\))'

# Compile the regex pattern for efficiency
pattern = re.compile(regex)

# Phrase to check for
phrase_to_check = "Uniﬁed Astronomy Thesaurus concepts:"

def file_contains_regex(file_path, pattern, phrase):
    """Check if the file contains the regex pattern in its text."""
    try:
        # Open the PDF file
        pdf_document = fitz.open(file_path)
        text = ""
        # Extract text from each page
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        pdf_document.close()
        
        # Check if the text matches the regex pattern
        return phrase in text
        #return pattern.search(text) is not None
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return False

def process_folder(folder_path):
    """Process all PDF files in the given folder and its subdirectories."""
    for root, dirs, files in os.walk(folder_path):
        deleted_count = 0  # Initialize count for deleted files in this folder
        for filename in files:
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(root, filename)
                if not file_contains_regex(file_path, pattern, phrase_to_check):
                    # If the regex does not match, delete the file
                    try:
                        os.remove(file_path)
                        logging.info(f"Deleted: {file_path}")
                        deleted_count += 1  # Increment count
                    except Exception as e:
                        logging.error(f"Error deleting file {file_path}: {e}")
        
        # Log the number of deleted files in the current folder
        logging.info(f"Deleted {deleted_count} file(s) in folder: {root}")

if __name__ == "__main__":
    process_folder(root_folder_path)
