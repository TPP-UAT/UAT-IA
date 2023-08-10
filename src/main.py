from UATMapper import UATMapper
from TermFileMapper import TermFileMapper
from TermTrainer import TermTrainer
from TermPrediction import TermPrediction
from NormalInputCreator import NormalInputCreator
from TFIDFInputCreator import TFIDFInputCreator

def train_and_predict(input_creator):
    term_id = '974'
    term_trainer = TermTrainer(training_files)
    term_trainer.train_model_by_thesaurus(branch_thesaurus, term_id, input_creator)

    trained_models = term_trainer.get_trained_models()
    keywords_by_term = term_trainer.get_keywords_by_term()

    term_predicton = TermPrediction(trained_models, keywords_by_term)
    texts = ["Mineralogy mineralogy mineralogy mineralogy mineralogy mineralogy mineralogy"]

    predicted_ids = []
    predictions_ids = term_predicton.predict_texts(texts, term_id, predicted_ids)

    # TODO: Agregar term_name a termFile
    predicted_keywords = []
    for prediction_ids in predictions_ids:
        keywords_by_text = []
        for id in prediction_ids:
            keywords_by_text.append(branch_thesaurus.get_by_id(id).get_name())
        predicted_keywords.append(keywords_by_text)
    print("Predicciones: ", predicted_keywords)

    predicted_ids = []
    predictions_ids = term_predicton.predict_texts(texts, term_id, predicted_ids)

if __name__ == '__main__':
    mapper = UATMapper("./data/UAT.json")
    thesaurus = mapper.map_to_thesaurus()

    branch_thesaurus = thesaurus.get_branch('972')

    term_file_mapper = TermFileMapper()
    term_file_mapper.create_training_files(branch_thesaurus)

    training_files = term_file_mapper.get_training_files()
    term_files = training_files.get_term_files()

    print('Normal train')
    train_and_predict(NormalInputCreator())
    print('TFIDF train')
    train_and_predict(TFIDFInputCreator())
    
