from tensorflow import keras as keras
from tensorflow.keras.datasets import reuters as reuters
from tensorflow.keras import models as models
from tensorflow.keras import layers as layers
from tensorflow.keras.utils import to_categorical
import matplotlib.pylab as plt
import numpy as np
(train_data, train_labels), (test_data, test_labels) = reuters.load_data(num_words=10000)
word_index = reuters.get_word_index()
reverse_word_index = dict([(value, key) for key, value in word_index.items()])
decoded_newswire = ' '.join([reverse_word_index.get(i - 3, '?') for i in train_data[0]])
print(decoded_newswire)
def vectorize_sequences(sequences , dimensions=10000):
    results = np.zeros((len(sequences), dimensions))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1
    return results
x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)
one_hot_train_labels = to_categorical(train_labels)
one_hot_test_labels = to_categorical(test_labels)
#y_train = np.asarray(train_labels).astype('float32')
#y_test = np.asarray(test_labels).astype('float32')
model = models.Sequential()
model.add(layers.Dense(64, activation='relu', input_shape=(10000,)))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(46, activation='sigmoid'))
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['acc'])
x_val = x_train[:1000]
partial_x_train =  x_train[1000:2200]
y_val = one_hot_train_labels[:1000]
partial_y_train =  one_hot_test_labels[1000:2200]
history = model.fit(partial_x_train, partial_y_train, epochs=9, batch_size=512, validation_data=(x_val, y_val))
history_dict = history.history
loss_values = history_dict['loss']
val_loss_values = history_dict['val_loss']
acc_values = history_dict['acc']
val_acc_values = history_dict['val_acc']
epochs = range(1, len(history_dict['acc']) +1)
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.plot(epochs, loss_values, 'bo', label='News Training loss')
ax1.plot(epochs, val_loss_values, 'b', label='News Validation loss')
ax1.set_title('News Training and Validation loss')
ax1.set_xlabel('Epochs')
ax1.set_ylabel('Loss')
ax1.legend()
ax2.plot(epochs, acc_values, 'bo', label='News Training Acc')
ax2.plot(epochs, val_acc_values, 'b', label='News Validation Acc')
ax2.set_title('News Training and Validation Accuracy')
ax2.set_xlabel('Epochs')
ax2.set_ylabel('Acc')
ax2.legend()