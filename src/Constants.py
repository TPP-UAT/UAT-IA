import os


root_directory = os.path.abspath(os.path.dirname(__file__))

data_directory = root_directory + "/data/"

uat_file = data_directory + "UAT-filtered.json"
pdfs_directory = data_directory + "PDFs"
pdfs_json = data_directory + "pdfs.json"
keywords_by_term_json = data_directory + "keywords-by-term.json"