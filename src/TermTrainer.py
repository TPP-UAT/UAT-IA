import os
import spacy
import random
import logging
import optuna
import math
from spacy.util import load_config, load_model_from_config
from sklearn.model_selection import train_test_split
from spacy.training import Example
from spacy.tokens import DocBin
from sklearn.metrics import f1_score
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
        self.config = load_config(config_path)

        # Quantity of models created
        self.models_created = 0
        
        # Logging, change log level if needed
        logging.basicConfig(filename='logs/trainer.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger('my_logger')

    def create_fresh_model(self):
        """
        Creates a new spaCy model from condig.
        """
        return load_model_from_config(self.config)

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

        # If training_data is less than 20, it's not worth training the model
        if len(training_data) < 20:
            self.log.info(f"Training data for term {term_id} has less than 20 files. Skipping training.")
            return

        # Split data into train and test sets
        train_data, validation_data, test_data = self.split_data(training_data)

        # Create validation examples that will be used for both optimization and final evaluation
        validation_examples = [
            Example.from_dict(
                self.create_fresh_model().make_doc(file_input_data.get_text_input()), 
                {"cats": file_input_data.get_categories()}
            )
            for file_input_data in validation_data.values()
        ]

        # Evaluate the final model with test data
        test_examples = [
            Example.from_dict(self.create_fresh_model().make_doc(file_input_data.get_text_input()), 
                {"cats": file_input_data.get_categories()}
            )
            for file_input_data in test_data.values()
        ]

        self.log.info(f"Training data for term ID {term_id} has size: {len(train_data)} - Validation data size: {len(validation_data)} - Test data size: {len(test_data)}")

        # Run Optuna to find best hyperparameters
        study = optuna.create_study(direction="maximize", pruner=optuna.pruners.HyperbandPruner(min_resource=7, max_resource=20, reduction_factor=3))
        best_model_path = f"./temp_models/best_model_{term_id}"
        best_accuracy = -float("inf")

        def objective_wrapper(trial):
            nonlocal best_accuracy
            accuracy, model = self.objective(trial, train_data, validation_examples, test_examples, children)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                if not os.path.exists('./temp_models'):
                    os.makedirs('./temp_models')
                model.to_disk(best_model_path)
                self.log.info(f"Saved best model for term {term_id} with accuracy {accuracy} at trial {trial.number}")
            return accuracy
        
        study.optimize(objective_wrapper, n_trials=12)

        # Retrieve best hyperparameters
        best_params = study.best_params
        best_trial = study.best_trial
        self.log.info(f"Best hyperparameters for term {term_id} with accuracy {best_trial.value}: {best_params}")

        # Combine train and validation data for final training
        # final_train_data = {**train_data, **validation_data}

        self.log.info(f"Training data for term ID {term_id} has size: {len(train_data)} - Test data size: {len(test_data)}")
        # Train final model with optimized hyperparameters
        final_model = self.final_train(train_data, test_examples, children, best_params, term_id)

        accuracy, loss = self.evaluate_model(test_examples, final_model)
        self.log.info(f"Final model for Term ID {term_id} - Accuracy: {accuracy}, Loss: {loss}")

        # Saved trained model
        self.save_trained_model(term_id, input_creator.get_folder_name(), final_model)
    
    def split_data(self, training_data):
        """
        Splits the training data into training (70%), validation (15%) and testing (15%) sets.
        """
        file_paths = list(training_data.keys())
        train_val_paths, test_paths = train_test_split(file_paths, test_size=0.15, random_state=42)

        val_size = 0.176  # Here, 15% of total is (0.15 / 0.85) ~17.6% of the train_val set.
        train_paths, val_paths = train_test_split(train_val_paths, test_size=val_size, random_state=42)
        
        train_data = {fp: training_data[fp] for fp in train_paths}
        val_data = {fp: training_data[fp] for fp in val_paths}
        test_data = {fp: training_data[fp] for fp in test_paths}
        
        return train_data, val_data, test_data
    
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

    def objective(self, trial, train_data, validation_examples, test_examples, categories):
        print(f"***** Running trial: {trial.number} *****")
        nlp = self.create_fresh_model()

        learn_rate = trial.suggest_float("learn_rate", 1e-6, 1e-3, log=True)
        batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
        dropout = trial.suggest_float("dropout", 0.2, 0.5)
        epochs = trial.suggest_int("epochs", 10, 20)
        weight_decay = trial.suggest_float("weight_decay", 1e-6, 1e-2, log=True)

        if "textcat_multilabel" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat_multilabel", last=True)
        else:
            textcat = nlp.get_pipe("textcat_multilabel")

        for category in categories:
            if category not in textcat.labels:
                textcat.add_label(category)

        optimizer = nlp.initialize()

        if hasattr(optimizer, "param_groups"):
            for param_group in optimizer.param_groups:
                param_group["lr"] = learn_rate
                param_group['weight_decay'] = weight_decay

        doc_bin = DocBin(store_user_data=True)
        texts = [file_input_data.get_text_input() for _, file_input_data in train_data.items()]
        categories_list = [file_input_data.get_categories() for _, file_input_data in train_data.items()]
        examples = []

        for doc, categories in zip(nlp.pipe(texts), categories_list):
            doc.cats = categories
            example = Example.from_dict(doc, {"cats": categories})  
            examples.append(example)
            doc_bin.add(doc)

        for epoch in range(epochs):  
            print(f"Starting epoch {epoch + 1}", flush=True)
            losses = {}
            docs = list(doc_bin.get_docs(nlp.vocab))
            random.shuffle(docs)

            for batch_start in range(0, len(docs), batch_size):
                batch_docs = docs[batch_start:batch_start + batch_size]
                examples = [Example.from_dict(doc, {"cats": doc.cats}) for doc in batch_docs]

                # Perform training step
                nlp.update(examples, sgd=optimizer, losses=losses, drop=dropout)

            accuracy, _loss = self.evaluate_model(validation_examples, nlp)

            # To compare the the accuracy on the test test
            accuracy_test, _loss_test = self.evaluate_model(test_examples, nlp)

            # Log accuracy
            self.log.info(f"Trial {trial.number} - Epoch {epoch + 1}: Accuracy {accuracy} - Loss {losses} - Test Accuracy {accuracy_test}")

            # Report accuracy to Optuna for pruning decisions
            trial.report(accuracy, epoch)

            if trial.should_prune():
                self.log.info(f"Trial {trial.number} pruned at epoch {epoch + 1}")
                raise optuna.exceptions.TrialPruned()
            
        # Log final result of trial
        self.log.info(
            f"Trial {trial.number} finished with value: {accuracy} and parameters: {trial.params}. "
        )

        return accuracy, nlp

    def final_train(self, train_data, test_examples, categories, best_params, term_id):
        """
        Train the final model using the best hyperparameters found by Optuna.
        """       
        # Load the best model from the trial with the best hyperparameters
        best_model_path = f"./temp_models/best_model_{term_id}"
        if not os.path.exists(best_model_path):
            raise FileNotFoundError(f"Best model not found at {best_model_path}")
        
        nlp = spacy.load(best_model_path)
        self.log.info(f"Loaded best model from {best_model_path} for final training")

        # Retrieve the pipeline to set up the ngram size
        # Check for existing component before adding
        if "textcat_multilabel" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat_multilabel", last=True)
        else:
            textcat = nlp.get_pipe("textcat_multilabel")

        # Add the labels to the textcat pipe
        for category in categories:
            if category not in textcat.labels:
                textcat.add_label(category)

        batch_size = best_params["batch_size"]
        dropout = best_params["dropout"]
        epochs = best_params["epochs"]
        learn_rate = best_params["learn_rate"]
        weight_decay = best_params["weight_decay"]

        print(f"Final training with best hyperparameters: {batch_size} - {dropout} - {epochs} - {learn_rate}", flush=True)

        optimizer = nlp.resume_training()
        
        # Debug optimizer
        print(f"Optimizer type: {type(optimizer)}", flush=True)
        print(f"Initial learn_rate: {optimizer.learn_rate}, Initial L2 (weight_decay): {optimizer.L2}", flush=True)

        doc_bin = DocBin(store_user_data=True)
        texts = [data.get_text_input() for data in train_data.values()]
        cats = [data.get_categories() for data in train_data.values()]

        # Set hyperparameters directly on the Thinc optimizer
        optimizer.learn_rate = learn_rate
        optimizer.L2 = weight_decay 

        print(f"Updated learn_rate: {optimizer.learn_rate}, Updated L2 (weight_decay): {optimizer.L2}", flush=True)
        
        for doc, cat in zip(nlp.pipe(texts), cats):
            doc.cats = cat
            doc_bin.add(doc)
        
        print(f"Total documents: {len(doc_bin)}", flush=True)
        print(f"---------------------------", flush=True)

        for epoch in range(epochs):
            try:
                print("Starting epoch: ", epoch + 1, flush=True)

                # Log all hyperparameters being used in this epoch
                current_params = {
                    "learn_rate": optimizer.learn_rate,
                    "weight_decay": optimizer.L2,
                    "batch_size": batch_size,
                    "dropout": dropout,
                    "epochs": epochs
                }
                print(f"Epoch {epoch + 1} - Current hyperparameters: {current_params}", flush=True)
                print(f"Epoch {epoch + 1} - Best hyperparameters for comparison: {best_params}", flush=True)
                
                losses = {}
                docs = list(doc_bin.get_docs(nlp.vocab))
                random.shuffle(docs)
                
                for batch_start in range(0, len(docs), batch_size):
                    batch_docs = docs[batch_start:batch_start + batch_size]
                    examples = [Example.from_dict(doc, {"cats": doc.cats}) for doc in batch_docs]
                    nlp.update(examples, sgd=optimizer, losses=losses, drop=dropout)

                # Evalute the model after each epoch
                f1, loss = self.evaluate_model(test_examples, nlp)
                self.log.info(f"Epoch {epoch + 1} - Test F1: {f1}, Loss: {loss}")
            except Exception as e:
                print("Error: ", e, flush=True)
                continue

        # Clean up temporary models
        if os.path.exists('./temp_models'):
            import shutil
            shutil.rmtree('./temp_models')

        return nlp

    def evaluate_model(self, examples, model):
        """
        Evaluates the trained model on new predictions and returns the accuracy.
        """
        true_labels = []
        pred_labels = []
        total_loss = 0.0

        for example in examples:
            doc = model(example.text)
            preds = doc.cats
            trues = example.reference.cats

            # Calculate cross-entropy loss
            loss = sum(
                trues[label] * -math.log(preds.get(label, 1e-9)) 
                for label in trues
            )
            total_loss += loss

            # Apply threshold for multilabel predictions
            threshold = 0.5
            true_labels.append([trues[label] for label in sorted(trues)])
            pred_labels.append([int(preds.get(label, 0) >= threshold) 
                              for label in sorted(trues)])

        # Calculate micro F1 score
        f1 = f1_score(true_labels, pred_labels, average='weighted', zero_division=0)
        avg_loss = total_loss / len(examples) if examples else 0
        return f1, avg_loss

    def save_trained_model(self, term_id, folder_name, nlp):
        # Create folder if it doesn't exist
        if not os.path.exists('./models/' + folder_name):
            os.makedirs('./models/' +  folder_name)

        model_save_path = f"./models/{folder_name}/{term_id}"
        nlp.to_disk(model_save_path)

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
