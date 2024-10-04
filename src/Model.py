import kerastuner as kt
import gc
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization, LeakyReLU
from keras.optimizers import Adam
class MyHyperModel(kt.HyperModel):
    def __init__(self, number_of_categories=2, max_sequence_length=100):
        self.number_of_categories = number_of_categories
        self.max_sequence_length = max_sequence_length

    def build(self, hp):
        # Hyperparameters
        hp_units = hp.Int('units', min_value=64, max_value=1024, step=64)
        hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
        hp_activation = hp.Choice('activation', values=['relu', 'sigmoid'])
        hp_dropout = hp.Float('dropout', min_value=0.1, max_value=0.5, step=0.1)

        # Define the optimizer
        model = Sequential()
        model.add(Dense(units=hp_units, activation=hp_activation))
        model.add(BatchNormalization())
        model.add(Dropout(hp_dropout))
    
        model.add(Dense(128))
        model.add(LeakyReLU(alpha=0.1))
        model.add(Dense(64))
        model.add(LeakyReLU(alpha=0.1))
    
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
    