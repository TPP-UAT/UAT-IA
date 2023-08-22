from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer
from TermPrediction import TermPrediction
from NormalInputCreator import NormalInputCreator
from TFIDFInputCreator import TFIDFInputCreator

NORMAL_TRAIN = 0.55
TFIDF_TRAIN = 0.45


def get_prediction_multiplier(input_creator):
    if isinstance(input_creator, NormalInputCreator):
        return NORMAL_TRAIN
    elif isinstance(input_creator, TFIDFInputCreator):
        return TFIDF_TRAIN
    else:
        return 0


def train_and_predict(input_creator):
    term_id = '972'
    term_trainer = TermTrainer(training_files)

    term_trainer.train_model_by_thesaurus(branch_thesaurus, term_id, input_creator)

    trained_models = term_trainer.get_trained_models()
    keywords_by_term = term_trainer.get_keywords_by_term()

    train_multiplier = get_prediction_multiplier(input_creator)

    term_predicton = TermPrediction(trained_models, keywords_by_term, train_multiplier)
    texts = ["Mineralogy mineralogy mineralogy mineralogy mineralogy mineralogy mineralogy"]

    predicted_terms = []
    predictions = term_predicton.predict_texts(texts, term_id, predicted_terms)

    print('----------------------------- Predictions ----------------------------')
    if all(len(prediction) == 0 for prediction in predictions):
        print("No prediction for the text")
    else:
        # First iterator if we have multiple texts to predict
        for prediction in predictions:
            # Second iterator if we have multiple predictions in same level
            for predicted_term in prediction:
                term = predicted_term.get_term()
                probability = format(predicted_term.get_probability(), ".2f")
                print(f"Term: {term.get_name()}, Probability: {probability}, Multiplier: {predicted_term.get_multiplier()}")


if __name__ == '__main__':
    mapper = UATMapper("./data/UAT.json")
    thesaurus = mapper.map_to_thesaurus()

    branch_thesaurus = thesaurus.get_branch('972')

    term_file_mapper = TermFileMapper()
    term_file_mapper.create_training_files(branch_thesaurus)

    training_files = term_file_mapper.get_training_files()
    term_files = training_files.get_term_files()

    print('----------------------------- Normal train ----------------------------')
    train_and_predict(NormalInputCreator())
    print('----------------------------- TFIDF train -----------------------------')
    train_and_predict(TFIDFInputCreator())
    
