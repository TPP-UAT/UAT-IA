import gc
import spacy
from spacy.tokens import DocBin

class TermTrainer:
    def __init__(self, thesaurus, database, model_name="en_core_news_md"):
        """
        Initializes the TermTrainer class by loading an existing spaCy model and
        setting up the thesaurus and database.

        :param thesaurus: Object that contains terms and their relationships
        :param database: Database connection to retrieve keywords and store results
        :param model_name: The name of the pre-trained spaCy model to load (default: 'en_core_news_md')
        """
        self.thesaurus = thesaurus
        self.database = database
        self.nlp = spacy.load(model_name)  # Load a pre-trained spaCy model

    def train_model(self, term_id, input_creator):
        """
        Main method to train the spaCy model with data corresponding to a specific term.

        :param term_id: ID of the term for which the model is being trained
        :param input_creator: Input creator responsible for generating data for training
        """
        # Fetch keywords associated with the term from the database using input_creator
        keywords = input_creator.get_keywords_by_term(term_id)

        # Prepare training data in a spaCy-compatible format
        training_data = self.prepare_training_data(keywords)

        # Fine-tune the pre-trained spaCy model using the prepared training data
        self.fine_tune_spacy_model(training_data, model_output=f"./models/{term_id}")

    def prepare_training_data(self, keywords):
        """
        Converts keywords into training data using spaCy's DocBin format for efficient storage.

        :param keywords: List of tuples where each tuple contains a keyword and its associated label
        :return: DocBin object containing spaCy documents with assigned categories
        """
        doc_bin = DocBin()
        for keyword, label in keywords:
            doc = self.nlp(keyword)  # Process keyword using the existing spaCy model
            doc.cats = {label: 1.0}  # Assign category (label) to the document
            doc_bin.add(doc)  # Add the document to DocBin
        return doc_bin

    def fine_tune_spacy_model(self, training_data, model_output):
        """
        Fine-tunes the existing spaCy model by updating it with new training data.

        :param training_data: DocBin object containing the training data (spaCy documents)
        :param model_output: Path where the fine-tuned model will be saved
        """
        # Get or add the 'textcat' component for text classification
        if "textcat" not in self.nlp.pipe_names:
            textcat = self.nlp.add_pipe("textcat", last=True)
        else:
            textcat = self.nlp.get_pipe("textcat")

        # Add new labels to the 'textcat' component based on the training data
        for label in self.get_labels_from_training_data(training_data):
            if label not in textcat.labels:
                textcat.add_label(label)

        # Resume training from the loaded model
        optimizer = self.nlp.resume_training()

        # Train the model for a specified number of epochs
        for i in range(10):  # You can adjust the number of epochs
            losses = {}
            for doc in training_data.get_docs(self.nlp.vocab):
                self.nlp.update([doc], sgd=optimizer, losses=losses)
            print(f"Epoch {i + 1} - Losses: {losses}")

        # Save the fine-tuned model to disk
        self.nlp.to_disk(model_output)

    def get_labels_from_training_data(self, training_data):
        """
        Extracts the unique set of labels from the training data for classification purposes.

        :param training_data: DocBin object containing spaCy documents with category assignments
        :return: List of unique labels found in the training data
        """
        labels = set()
        for doc in training_data.get_docs(self.nlp.vocab):
            labels.update(doc.cats.keys())
        return list(labels)

    def get_keywords_by_term(self, term_id):
        """
        Retrieves the keywords indexes.

        :param term_id: ID of the term for which to fetch keywords
        :return: List of keywords and their corresponding labels
        """
        # Retrieve the keywords from the thesaurus or database based on term_id
        return []