import os
import spacy
import random
import logging
import optuna
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
            first_file_path = next(iter(training_data))  # Get the first key in the dictionary
            first_file_data = training_data[first_file_path]  # Get the data for the first file
            print(f"Text input for the first file: {first_file_data.get_text_input()}", flush=True)

        # Split data into train and test sets
        train_data, test_data = self.split_data(training_data)

        self.log.info(f"Training data size: {len(train_data)}")
        self.log.info(f"Test data size: {len(test_data)}")

        # Run Optuna to find best hyperparameters
        study = optuna.create_study(direction="maximize", pruner=optuna.pruners.MedianPruner())
        study.optimize(lambda trial: self.objective(trial, train_data, test_data, children), n_trials=6)  # Reduced trials

        # Retrieve best hyperparameters
        best_params = study.best_params
        self.log.info(f"Best hyperparameters for term {term_id}: {best_params}")

        # Train final model with optimized hyperparameters
        self.final_train(train_data, children, best_params)

        # Evaluate the final model
        test_examples = [
            Example.from_dict(self.nlp.make_doc(file_input_data.get_text_input()), {"cats": file_input_data.get_categories()})
            for file_input_data in test_data.values()
        ]
        accuracy = self.evaluate_model(test_examples, True)
        self.log.info(f"Final model accuracy for term {term_id}: {accuracy}")

        # Saved trained model
        self.save_trained_model(term_id, input_creator.get_folder_name())
    
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

    def objective(self, trial, train_data, test_data, categories):
        """
        Objective function for Optuna hyperparameter tuning.
        """
        print(f"***** Running trial: {trial.number} *****")

        learn_rate = trial.suggest_float("learn_rate", 1e-5, 1e-3)
        batch_size = trial.suggest_categorical("batch_size", [4, 8, 16, 32])
        dropout = trial.suggest_float("dropout", 0.1, 0.5)
        epochs = trial.suggest_int("epochs", 5, 20)
        ngram_size = trial.suggest_int("ngram_size", 1, 3)

        if "textcat_multilabel" not in self.nlp.pipe_names:
            textcat = self.nlp.add_pipe("textcat_multilabel", last=True)
        else:
            textcat = self.nlp.get_pipe("textcat_multilabel")

        # Adjust the quantity of embedding layers
        textcat.cfg["ngram_size"] = ngram_size

        for category in categories:
            if category not in textcat.labels:
                textcat.add_label(category)

        optimizer = self.nlp.initialize()

        if hasattr(optimizer, "param_groups"):
            for param_group in optimizer.param_groups:
                param_group["lr"] = learn_rate

        doc_bin = DocBin(store_user_data=True)
        texts = [file_input_data.get_text_input() for _, file_input_data in train_data.items()]
        categories_list = [file_input_data.get_categories() for _, file_input_data in train_data.items()]
        examples = []

        for doc, categories in zip(self.nlp.pipe(texts), categories_list):
            doc.cats = categories
            example = Example.from_dict(doc, {"cats": categories})   # Save ground truth categories for evaluation
            examples.append(example)
            doc_bin.add(doc)

        for epoch in range(epochs):  # Train only 5 epochs per trial
            print("Starting epoch: ", epoch + 1, flush=True)
            losses = {}
            docs = list(doc_bin.get_docs(self.nlp.vocab))
            random.shuffle(docs)

            for batch_start in range(0, len(docs), batch_size):
                batch_docs = docs[batch_start:batch_start + batch_size]
                examples = [Example.from_dict(doc, {"cats": doc.cats}) for doc in batch_docs]

                self.nlp.update(examples, sgd=optimizer, losses=losses, drop=dropout)

            # Create test examples for evaluation only using 50% of the data
            test_size = max(1, int(len(test_data) * 0.5))
            test_samples = random.sample(list(test_data.values()), test_size)

            test_texts = [file_input_data.get_text_input() for file_input_data in test_samples]
            test_examples = [
                Example.from_dict(self.nlp.make_doc(text), {"cats": sample.get_categories()})
                for text, sample in zip(test_texts, test_samples)
            ]

            # Evaluate the model
            accuracy = self.evaluate_model(test_examples, False)
            trial.report(accuracy, epoch)

            # Pruning: Stop bad trials early
            if trial.should_prune():
                raise optuna.exceptions.TrialPruned()

        return accuracy

    def final_train(self, train_data, categories, best_params):
        """
        Train the final model using the best hyperparameters found by Optuna.
        """
        batch_size = best_params["batch_size"]
        dropout = best_params["dropout"]

        optimizer = self.nlp.initialize()
        if hasattr(optimizer, "param_groups"):
            for param_group in optimizer.param_groups:
                param_group["lr"] = best_params["learn_rate"]

        doc_bin = DocBin(store_user_data=True)
        texts = [file_input_data.get_text_input() for _, file_input_data in train_data.items()]
        categories_list = [file_input_data.get_categories() for _, file_input_data in train_data.items()]

        # Batch processing the texts
        for doc, categories in zip(self.nlp.pipe(texts), categories_list):
            doc.cats = categories  # Assign categories to the doc
            doc_bin.add(doc)  # Add the doc to the DocBin

        print(f"Total documents: {len(doc_bin)}", flush=True)
        print(f"---------------------------", flush=True)

        for epoch in range(20):  # Full training for best hyperparameters
            try:
                print("Starting epoch: ", epoch + 1, flush=True)
                losses = {}
                docs = list(doc_bin.get_docs(self.nlp.vocab))
                random.shuffle(docs)

                for batch_start in range(0, len(docs), batch_size):
                    batch_docs = docs[batch_start:batch_start + batch_size]
                    examples = [Example.from_dict(doc, {"cats": doc.cats}) for doc in batch_docs]
                    self.nlp.update(examples, sgd=optimizer, losses=losses, drop=dropout)
            except Exception as e:
                print("Error: ", e, flush=True)
                continue

    def evaluate_model(self, examples, show_logs=False):
        """
        Evaluates the trained model on new predictions and returns the accuracy.
        """
        if (show_logs):
            self.log.info("Evaluating model...")

        correct = 0
        total = 0

        if isinstance(examples[0], str):
            raise ValueError("`evaluate_model()` received raw text instead of `Example` objects!")

        texts = [example.text if isinstance(example, Example) else example for example in examples]
        predicted_docs = list(self.nlp.pipe(texts))  # Process in batch

        if (show_logs):
            self.log.info(f"Total predicted docs: {len(predicted_docs)}")
        print("Total predicted docs: ", len(predicted_docs), flush=True)

        for doc, example in zip(predicted_docs, examples):
            pred_label = max(doc.cats, key=doc.cats.get)  # Predicted label
            gold_label = max(example.reference.cats, key=example.reference.cats.get)  # Ground truth

            if pred_label == gold_label:
                correct += 1
            total += 1

        accuracy = correct / total if total > 0 else 0  # Return accuracy
        if (show_logs):
            self.log.info(f"new method Accuracy: {accuracy}")

        print("new method Accuracy: ", accuracy, flush=True)

        return accuracy
        """
        Evaluates the model on the test set and returns the accuracy.
        """
        if (show_logs):
            self.log.info("Old method Evaluating model...")

        examples = []
        for _, file_input_data in test_data.items():
            text_input = file_input_data.get_text_input()
            categories = file_input_data.get_categories()
            doc = self.nlp.make_doc(text_input)
            example = Example.from_dict(doc, {"cats": categories})
            examples.append(example)

        if (show_logs):
            self.log.info(f"Total test examples: {len(examples)}")
        print("Total test examples: ", len(examples), flush=True)

        scorer = self.nlp.evaluate(examples)

        for key, value in scorer.items():
            print(f"{key}: {value}")
            self.log.info(f"{key}: {value}")

        accuracy = scorer["cats_score"]
        print(f"old method Accuracy: {accuracy}")
        self.log.info(f"old method Accuracy: {accuracy}")

        return accuracy

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