import kerastuner as kt
import gc
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, BatchNormalization
from keras.optimizers import Adam
class MyHyperModel(kt.HyperModel):
    def __init__(self, number_of_categories=2, vocab_size=1, embedding_dim=1, max_sequence_length=100):
        self.number_of_categories = number_of_categories
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.max_sequence_length = max_sequence_length

    def build(self, hp):
        # Hyperparameters
        hp_units = hp.Int('units', min_value=32, max_value=512, step=32)
        hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
        hp_activation = hp.Choice('activation', values=['relu', 'sigmoid'])

        # Define the optimizer
        model = Sequential()
        model.add(Embedding(input_dim=self.vocab_size, output_dim=self.embedding_dim, input_length=self.max_sequence_length))
        model.add(Dense(units=hp_units, activation=hp_activation))
        model.add(LSTM(128, return_sequences=True))
        model.add(LSTM(32))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(self.number_of_categories, activation='sigmoid'))  # Salida multi-etiqueta

        opt = Adam(learning_rate=hp_learning_rate)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

        gc.collect()

        return model
    
    def build_without_hyperparameters(self):
        model = Sequential()
        model.add(Embedding(input_dim=self.vocab_size, output_dim=self.embedding_dim, input_length=self.max_sequence_length))
        model.add(LSTM(128, return_sequences=True))
        model.add(LSTM(32))
        model.add(Dense(64, activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(self.number_of_categories, activation='sigmoid'))  # Salida multi-etiqueta

        opt = Adam(learning_rate=0.001)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

        return model
    