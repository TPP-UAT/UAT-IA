import fitz
import re
import json
import os

PDFS_PATH = './PDFs'

def write_document(concepts):
    # Specify the output file path
    output_file = "./data/pdfs.json"

    # Write the JSON data to the output file
    with open(output_file, 'w') as json_file:
        json.dump(list(concepts.values()), json_file, indent=4)

    print(f"JSON data saved to {output_file}")

def generate_json(pdf_directory, thesaurus):
    regex = r'Uniﬁed Astronomy Thesaurus concepts:\s*((?:[^;)]+\(\d+\);\s*)+[^;)]+\(\d+\))' # regex pattern to find URLs
    concepts_dict = {}  # Dictionary to store IDs and associated files

    # Loop through all files in the directory
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(pdf_directory, filename)
            pdf_file_path = os.path.join(PDFS_PATH, filename)

            # Open the PDF file
            pdf_document = fitz.open(pdf_file)

            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                text = page.get_text()

                # Find all URLs using the regex pattern
                terms = re.findall(regex, text)
                if len(terms) > 0:
                    concepts = terms[0]  # Assuming there's only one match per page

                    # Find the IDs in the terms
                    ids = re.findall(r'\((\d+)\)', concepts)

                    for id in ids:
                        id_str = str(id)

                        # Add the ID to the dictionary if it doesn't exist
                        if id_str not in concepts_dict:
                            concepts_dict[id_str] = {
                                'id': id_str,
                                'files': []
                            }

                        # Add the file to the dictionary if it doesn't exist
                        if pdf_file_path not in concepts_dict[id_str]['files']:
                            concepts_dict[id_str]['files'].append(pdf_file_path)

            # Close the PDF document
            pdf_document.close()

    # If the thesaurus term is not present in any file, add it as an empty term
    for thesaurus_term_id in thesaurus.get_terms():
        concept_term = concepts_dict.get(thesaurus_term_id, None)
        if concept_term == None:
            concepts_dict[thesaurus_term_id] = {
                                'id': thesaurus_term_id,
                                'files': []
                            }
    write_document(concepts_dict)
