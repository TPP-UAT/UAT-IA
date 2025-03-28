import os
import spacy
import random
import logging
from spacy.util import load_config, load_model_from_config
from sklearn.model_selection import train_test_split
from spacy.training import Example
from spacy.tokens import DocBin
from spacy.pipeline.textcat_multilabel import Config

from Database.Keyword import Keyword
from models.FileInputData import FileInputData

class TermTrainer:
    def __init__(self, thesaurus, database, config_path="config.cfg"):
        """
        Initializes the TermTrainer class by loading an existing spaCy model and
        setting up the thesaurus and database.

        :param thesaurus: Object that contains terms and their relationships
        :param database: Database connection to retrieve keywords and store results
        :param config_path: The path to the spaCy configuration file
        """
        self.thesaurus = thesaurus
        self.database = database
        config = load_config(config_path)
        self.nlp = load_model_from_config(config)
        # self.nlp = spacy.blank('en')

        # Quantity of models created
        self.models_created = 0
        
        # Logging, change log level if needed
        logging.basicConfig(filename='logs/trainer.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('my_logger')

    def train_group(self, term_id, children, input_creator):
        """
        Trains a spaCy model for a group of terms.
        :param term_id: ID of the term for which the model is being trained
        :param children: List of term objects that are children of the term
        :param input_creator: Input creator responsible for generating data for training
        """
        # Prepare training data (training_data: { 'file_path': FileInputData(file_categories , text_input) })
        training_data = self.prepare_training_data(children, input_creator)

        if training_data:
            first_file_path = next(iter(training_data))  # Obtener la primera clave del diccionario
            first_file_data = training_data[first_file_path]  # Obtener el valor correspondiente
            print(f"Text input for the first file: {first_file_data.get_text_input()}", flush=True)
                # If training_data is less than 20, it's not worth training the model
        if len(training_data) < 20:
            self.log.info(f"Training data for term {term_id} has less than 20 files. Skipping training.")
            return
        
        # Split data into train and test sets
        train_data, test_data = self.split_data(training_data)

        # Train the model with the training data
        self.train(train_data, children)
        print("Model trained", flush=True)
        # Evaluate the model using the test set
        accuracy = self.test_model(test_data)
        print(f"Model accuracy: {accuracy}")
        self.log.info(f"Model accuracy: {accuracy}")

        # Saved trained model
        self.save_trained_model(term_id, input_creator.get_folder_name())

        # Chequear como hacer si el modelo no tiene ninguna categoria con "1"
        # if len(keywords_by_text):
        #     self.generate_model_for_group_of_terms(texts, keywords_by_text, term_id, training_input_creator)
        #     self.models_created += 1
    
    def split_data(self, training_data):
        """
        Splits the training data into training and testing sets.
        """
        file_paths = list(training_data.keys())
        train_paths, test_paths = train_test_split(file_paths, test_size=0.15, random_state=42)
        
        train_data = {fp: training_data[fp] for fp in train_paths}
        test_data = {fp: training_data[fp] for fp in test_paths}
        
        return train_data, test_data
    
    def prepare_training_data(self, children, training_input_creator):
        keyword_table_db = Keyword(self.database)
        # training_files_input: { 'file_path': FileInputData(file_categories , text_input) }. The categories dictionaty of 0s and 1s represents the keywords for the file
        # file_categories: {'102': 0, '1129': 0, '1393': 0, '661': 1}
        # text_input: "e.g. abstract from an article"
        training_files_input = {}

        for child in children:
            # Get all children recursively from the child term (To associate all child files to the term child)
            term_children = self.thesaurus.get_branch_children(child)
            term_children_ids = [term.get_id() for term in term_children]
            term_children_ids.insert(0, child)

            files_paths = keyword_table_db.get_file_ids_by_keyword_ids(term_children_ids)
            self.log.info(f"Child: {child} has {len(term_children_ids)} children and {len(files_paths)} files")
            for file_path in files_paths:
                # If the file_path is not in files_input dictionary, creates a new item with the path as the key and an input array filled with 0s
                if file_path not in training_files_input:
                    file_categories = { child: 0 for child in children }
                    text_input = training_input_creator.get_file_data_input(file_path)
                    training_files_input[file_path] = FileInputData(file_categories, text_input)
                
                # Set the child as category with 1 insted of 0
                training_files_input[file_path].set_category(child)

        return training_files_input

    def test_model(self, test_data):
        """
        Evaluates the model on the test set and returns the accuracy.
        """
        examples = []
        for _, file_input_data in test_data.items():
            text_input = file_input_data.get_text_input()
            categories = file_input_data.get_categories()
            doc = self.nlp.make_doc(text_input)
            example = Example.from_dict(doc, {"cats": categories})
            examples.append(example)

        scorer = self.nlp.evaluate(examples)

        for key, value in scorer.items():
            print(f"{key}: {value}")
            self.log.info(f"{key}: {value}")

        return scorer["cats_score"]  # Return the accuracy of the model

    def train(self, train_data, categories):
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
            print("Adding category: ", category, flush=True)
            if category not in textcat.labels:
                textcat.add_label(category)

        optimizer = self.nlp.initialize()

        print("PIPELINE: ", self.nlp.pipe_names)

        doc_bin = DocBin(store_user_data=True)
        texts = [file_input_data.get_text_input() for _, file_input_data in train_data.items()]
        categories_list = [file_input_data.get_categories() for _, file_input_data in train_data.items()]

        # Batch processing the texts
        for doc, categories in zip(self.nlp.pipe(texts), categories_list):
            doc.cats = categories  # Assign categories to the doc
            doc_bin.add(doc)  # Add the doc to the DocBin

        print(f"Total documents: {len(doc_bin)}", flush=True)
        print(f"---------------------------", flush=True)
    
        # Train the model for a specified number of epochs
        # optimizer = self.nlp.resume_training() # Inicializa correctamente el optimizador
        batch_size = 128
        for i in range(30):  # Adjust necessary epochs
            try: 
                print("Starting epoch: ", i + 1, flush=True)
                losses = {}
        
                docs = list(doc_bin.get_docs(self.nlp.vocab))
                random.shuffle(docs)
                
                for batch_start in range(0, len(docs), batch_size):
                    batch_docs = docs[batch_start:batch_start + batch_size]
                    examples = [Example.from_dict(doc, {"cats": doc.cats}) for doc in batch_docs]
                    
                    try:
                        self.nlp.update(examples, sgd=optimizer, losses=losses)
                    except Exception as e:
                        print("Error en la actualización:", e, flush=True)
                
                print(f"Epoch {i + 1} - Losses: {losses}", flush=True)
            except Exception as e:
                print("Error: ", e, flush=True)
                continue

    def save_trained_model(self, term_id, folder_name):
        # Create folder if it doesn't exist
        if not os.path.exists('./models/' + folder_name):
            os.makedirs('./models/' +  folder_name)

        model_save_path = f"./models/{folder_name}/{term_id}"
        self.nlp.to_disk(model_save_path)

        self.log.info(f"Model saved at: {model_save_path}")

    # Entrypoint method
    def train_model(self, term_id, input_creator):
        """
        Entrypoint method to train the spaCy model with data corresponding to a specific term.

        :param term_id: ID of the term for which the model is being trained
        :param input_creator: Input creator responsible for generating data for training
        """
        self.log.info(f"---------------------------------")
        self.log.info(f"Started training for term ID: {term_id}")

        # Check if the term is already trained
        term_is_trained = False
        folder_name = input_creator.get_folder_name()
        if os.path.exists('./models/' + folder_name):
            if os.path.exists(f"./models/{folder_name}/{term_id}"):
                self.log.info(f"Model for term {term_id} already exists")
                term_is_trained = True

        # Get children of the term
        term_children = self.thesaurus.get_by_id(term_id).get_children()

        # If the term has no children, there is no need to train a model
        if not term_children:
            self.log.info(f"Term {term_id} has no children")
            return
        
        # Train the model if it hasn't been trained yet
        if (not term_is_trained):
            self.train_group(term_id, term_children, input_creator)