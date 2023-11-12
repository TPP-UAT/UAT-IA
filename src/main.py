import json
import os
import glob
import tensorflow as tf
from utils.pdfs_terms_parser import generate_json
from TrainedModels import TrainedModels
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer
from TermPrediction import TermPrediction
from NormalInputCreator import NormalInputCreator
from TFIDFInputCreator import TFIDFInputCreator
from AbstractInputCreator import AbstractInputCreator
import gc

NORMAL_TRAIN = 0.55
TFIDF_TRAIN = 0.45
ABSTRACT_TRAIN = 0.5

def get_prediction_multiplier(input_creator):
    if isinstance(input_creator, NormalInputCreator):
        return NORMAL_TRAIN
    elif isinstance(input_creator, TFIDFInputCreator):
        return TFIDF_TRAIN
    elif isinstance(input_creator, AbstractInputCreator):
        return ABSTRACT_TRAIN
    else:
        return 0

def train(term_id, input_creator, training_files, branch_thesaurus):
    term_trainer = TermTrainer(training_files)
    term_trainer.train_model_by_thesaurus(branch_thesaurus, term_id, input_creator)

    return term_trainer

# TODO: No se deberia necesitar un term_id, tampoco en predict_texts()
def predict(term_id, input_creator, trained_models, keywords_by_term):
    train_multiplier = get_prediction_multiplier(input_creator)

    term_predicton = TermPrediction(trained_models, keywords_by_term, train_multiplier)
    texts = ["Mineralogy mineralogy mineralogy mineralogy mineralogy mineralogy mineralogy"]

    predicted_terms = []
    predictions = term_predicton.predict_texts(texts, term_id , predicted_terms)

    print('----------------------------- Predictions ----------------------------')
    if all(len(prediction) == 0 for prediction in predictions):
        print("No prediction for the text")
    else:
        # First iterator if we have multiple texts to predict
        for prediction in predictions:
            # Second iterator if we have multiple predictions in same level
            for predicted_term in prediction:
                term_id = predicted_term.get_term()
                probability = format(predicted_term.get_probability(), ".2f")
                term_name = thesaurus.get_by_id(term_id).get_name()
                print(f"Term: {term_name}, Probability: {probability}, Multiplier: {predicted_term.get_multiplier()}")

    return predictions

# Save methods
def save_term_trainer(term_trainer: TermTrainer):
    save_trained_models(term_trainer.get_trained_models())
    save_keywords_by_term(term_trainer.get_keywords_by_term())

def save_keywords_by_term(keywords_by_term):
    file_path = "./models/keywords-by-term.json"
    
    # Check if the file already exists
    if os.path.exists(file_path):
        # If the file exists, read the existing data
        with open(file_path, "r") as file:
            existing_data = json.load(file)
        
        # Update the existing data with new keywords_by_term
        existing_data.update(keywords_by_term)
    else:
        existing_data = keywords_by_term

    # Write the updated data back to the file
    with open(file_path, "w") as file:
        json.dump(existing_data, file)

def save_trained_models(trained_models: TrainedModels):
    models = trained_models.get_models()
    for term_id, model in models.items():
        if model is not None:
            model_save_path = f"./models/{term_id}.keras"
            model.save(model_save_path)

# Load methods
def load_keywords_by_term():
    file = open("./models/keywords-by-term.json", "r")
    keywords_by_term = file.read()
    keywords_by_term = json.loads(keywords_by_term)
    file.close()
    return keywords_by_term

def load_trained_models():
    models = {}
    for model_path in glob.glob("./models/*.keras"):
        term_id = os.path.basename(model_path).replace(".keras", "")
        models[term_id] = tf.keras.models.load_model(model_path)

    # Create TrainedModels object
    trained_models = TrainedModels()
    for term_id, model in models.items():
        trained_models.add_model_for_term_children(term_id, model)

    return trained_models

def train_branch(term_id):
    branch_thesaurus = thesaurus.get_branch(term_id)

    term_file_mapper = TermFileMapper()
    term_file_mapper.create_training_files(branch_thesaurus)

    training_files = term_file_mapper.get_training_files()

    term_trainer = train(term_id, NormalInputCreator(), training_files, branch_thesaurus)

    save_term_trainer(term_trainer)

def generate_documents_json():
    # Generate json file with terms associated to pdfs
    generate_json("./data/PDFs")

if __name__ == '__main__':
    gc.set_debug(gc.DEBUG_SAVEALL)
    # This term (modified a bit on the json) has 11 children that covers the whole thesaurus
    mapper = UATMapper("./data/UAT-filtered.json")
    thesaurus = mapper.map_to_thesaurus()

    # Father terms: 104, 343, 486, 563, 739, 804, 847, 1145, 1476, 1529, 1583
    initial_term_id = ['104', '343', '486', '563']
    father_term_id = '343'

    print("Training options: \n 1 - Change document files \n 2 - Train with files and save \n 3 - Load existent model \n Insert option number: ")
    training_option = input()

    # Select between training or loading model
    if (training_option == "1"):
        generate_documents_json()
    
    elif (training_option == "2"):
        for term_id in initial_term_id:
            train_branch(term_id)
            gc.collect()
    
    elif (training_option == "3"):
        keywords_by_term = load_keywords_by_term()
        trained_models = load_trained_models()
        predict(father_term_id, NormalInputCreator(), trained_models, keywords_by_term)

    
