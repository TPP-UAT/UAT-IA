from InputCreators.NormalInputCreator import NormalInputCreator
from InputCreators.AbstractInputCreator import AbstractInputCreator
from InputCreators.TFIDFInputCreator import TFIDFInputCreator

NORMAL_TRAIN = 0.3
TFIDF_TRAIN = 0.3
ABSTRACT_TRAIN = 0.4

def get_prediction_multiplier(input_creator):
    if isinstance(input_creator, NormalInputCreator):
        return NORMAL_TRAIN
    elif isinstance(input_creator, TFIDFInputCreator):
        return TFIDF_TRAIN
    elif isinstance(input_creator, AbstractInputCreator):
        return ABSTRACT_TRAIN
    else:
        return 0
