import kerastuner as kt
import gc
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, BatchNormalization
from keras.optimizers import Adam
class MyHyperModel(kt.HyperModel):
    def __init__(self, number_of_categories=2):
        self.number_of_categories = number_of_categories

    def build(self, hp):
        # Hyperparameters
        hp_units = hp.Int('units', min_value=32, max_value=512, step=32)
        hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
        hp_activation = hp.Choice('activation', values=['relu', 'sigmoid'])

        # Define the optimizer
        model = Sequential()
        model.add(Dense(units=hp_units, activation=hp_activation))
        #model.add(LSTM(128, return_sequences=True))
        #model.add(LSTM(32))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(self.number_of_categories, activation='sigmoid'))  # Salida multi-etiqueta

        opt = Adam(learning_rate=hp_learning_rate)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

        gc.collect()

        return model
    
    def build_without_hyperparameters(self):
        model = Sequential()
        model.add(LSTM(128, return_sequences=True))
        model.add(LSTM(32))
        model.add(Dense(64, activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Dense(self.number_of_categories, activation='sigmoid'))  # Salida multi-etiqueta

        opt = Adam(learning_rate=0.001)
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

        return model
    