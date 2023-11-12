import json
import os
import glob
import tensorflow as tf
from TrainedModels import TrainedModels
from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer
from TermPrediction import TermPrediction
from NormalInputCreator import NormalInputCreator
from TFIDFInputCreator import TFIDFInputCreator
from AbstractInputCreator import AbstractInputCreator

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

def train(term_id, input_creator):
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
    file = open("./models/keywords-by-term.json", "w")
    json.dump(keywords_by_term, file)
    file.close()

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

if __name__ == '__main__':
    mapper = UATMapper("./data/UAT.json")
    thesaurus = mapper.map_to_thesaurus()

    branch_thesaurus = thesaurus.get_branch('972')

    term_file_mapper = TermFileMapper()
    term_file_mapper.create_training_files(branch_thesaurus)

    training_files = term_file_mapper.get_training_files()
    term_files = training_files.get_term_files()

    training_files.print_term_files()

    print('----------------------------- Normal train ----------------------------')
    test_term_id = "972"

    print("Training options: \n 1 - Train with files and save \n 2- Load existent model \n Insert option number: ")
    training_option = input()

    # Select between training or loading model
    if (training_option == "1"):
        term_trainer = train(test_term_id, NormalInputCreator())

        # Obtain trained models and keywords_by_term
        trained_models = term_trainer.get_trained_models()
        keywords_by_term = term_trainer.get_keywords_by_term()
        save_term_trainer(term_trainer)
    elif (training_option == "2"):
        keywords_by_term = load_keywords_by_term()
        trained_models = load_trained_models()

    predict(test_term_id, NormalInputCreator(), trained_models, keywords_by_term)

    """
    print('----------------------------- TFIDF train -----------------------------')
    train_and_predict(TFIDFInputCreator())
    print('----------------------------- Abstract train -----------------------------')
    train_and_predict(AbstractInputCreator())
    """
    
