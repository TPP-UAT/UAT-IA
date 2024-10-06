import gc
import os
import spacy
import logging
from spacy.training import Example
from spacy.lookups import Lookups


from Database.Keyword import Keyword
from FileInputData import FileInputData

class TermTrainer:
    def __init__(self, thesaurus, database, model_name="en_core_web_md"):
        """
        Initializes the TermTrainer class by loading an existing spaCy model and
        setting up the thesaurus and database.

        :param thesaurus: Object that contains terms and their relationships
        :param database: Database connection to retrieve keywords and store results
        :param model_name: The name of the pre-trained spaCy model to load (default: 'en_core_web_md')
        """
        self.thesaurus = thesaurus
        self.database = database
        self.nlp = spacy.load(model_name)  # Load a pre-trained spaCy model

        # Quantity of models created
        self.models_created = 0
        
        # Logging, change log level if needed
        logging.basicConfig(filename='trainer.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('my_logger')

    def train_model(self, term_id, input_creator):
        """
        Main method to train the spaCy model with data corresponding to a specific term.

        :param term_id: ID of the term for which the model is being trained
        :param input_creator: Input creator responsible for generating data for training
        """
        self.log.info(f"---------------------------------")
        self.log.info(f"Started training for term ID: {term_id}")

        # Check if the term is already trained
        term_is_trained = False
        folder_name = input_creator.get_folder_name()
        if os.path.exists('./models/' + folder_name):
            if os.path.exists(f"./models/{folder_name}/{term_id}.keras"):
                self.log.info(f"Model for term {term_id} already exists")
                term_is_trained = True

        term_children = self.thesaurus.get_by_id(term_id).get_children()
        if not term_children:
            self.log.info(f"Term {term_id} has no children")
            return
        
        if (not term_is_trained):
            self.train_group(term_id, term_children, input_creator)

        # Fetch keywords associated with the term from the database using input_creator
        # keywords = input_creator.get_keywords_by_term(term_id)

        # Prepare training data in a spaCy-compatible format
        # training_data = self.prepare_training_data(keywords)

        # Fine-tune the pre-trained spaCy model using the prepared training data
        # self.fine_tune_spacy_model(training_data, model_output=f"./models/{term_id}")

    def train_group(self, term_id, children, input_creator):
        training_data = self.prepare_training_data(children, input_creator)
        self.fine_tune_spacy_model(training_data, children, model_output=f"./models/{input_creator.get_folder_name()}/{term_id}")
        # if len(keywords_by_text):
        #     self.generate_model_for_group_of_terms(texts, keywords_by_text, term_id, training_input_creator)
        #     self.models_created += 1
    
    def prepare_training_data(self, children, training_input_creator):
        print("Children: ", children)
        keyword_table_db = Keyword(self.database)
        # training_files_input: { 'file_path': FileInputData(file_categories , text_input) }. The categories dictonary of 0s and 1s represents the keywords for the file
        # file_categories: {'102': 0, '1129': 0, '1393': 0, '661': 1}
        # text_input: "Hola pepito como andas"
        training_files_input = {}

        for child in children:
            # Get all children recursively from the child term (To associate all child files to the term child)
            term_children = self.thesaurus.get_branch_children(child)
            term_children_ids = [term.get_id() for term in term_children]
            term_children_ids.insert(0, child)

            files_paths = keyword_table_db.get_file_ids_by_keyword_ids(term_children_ids)
            for file_path in files_paths:
                # If the file_path is not in files_input dictionary, creates a new item with the path as the key and an input array filled with 0s
                if file_path not in training_files_input:
                    file_categories = { child: 0 for child in children }
                    text_input = training_input_creator.get_file_data_input(file_path)
                    training_files_input[file_path] = FileInputData(file_categories, text_input)
                
                # Set the child as category with 1 insted of 0
                training_files_input[file_path].set_category(child)

        # Converts keywords into training data using spaCy's DocBin format for efficient storage.
        return training_files_input

    def fine_tune_spacy_model(self, examples, categories, model_output):
        """
        Fine-tunes the existing spaCy model by updating it with new training data.

        :param examples: List of Example objects containing the training data (text and annotations)
        :param model_output: Path where the fine-tuned model will be saved
        """
        # Get or add the 'textcat_multilabel' component for multilabel text classification
        if "textcat_multilabel" not in self.nlp.pipe_names:
            textcat = self.nlp.add_pipe("textcat_multilabel", last=True)
        else:
            textcat = self.nlp.get_pipe("textcat_multilabel")

        # Add new labels to the 'textcat_multilabel' component based on the examples
        for category in categories:
            if category not in textcat.labels:
                textcat.add_label(category)

        # Train the model for a specified number of epochs
        optimizer = self.nlp.initialize()  # Inicializa correctamente el optimizador
        for i in range(10):  # Ajusta el número de épocas según sea necesario
            losses = {}
            self.nlp.update(examples, sgd=optimizer, losses=losses)  # Actualiza usando los objetos Example
            print(f"Epoch {i + 1} - Losses: {losses}")

        # Save the fine-tuned model to disk
        self.nlp.to_disk(model_output)
