#!/usr/bin/env python3

'''aionfpga ~ convolutional neural network (cnn)
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

import matplotlib.pyplot as plt

import fhnwtoys.training as fh

def main():
    seed = fh.seed + 1 # AIonFPGA + 1 = AIonFPGB
    tf.random.set_seed(seed)

    training_dataset = fh.Dataset_Generator(fh.training_frames_name, fh.training_labels_name, fh.dir_training_dataset, 4903, 32)
    validation_dataset = fh.Dataset_Generator(fh.validation_frames_name, fh.validation_labels_name, fh.dir_validation_dataset, 1050, 32)
    test_dataset = fh.Dataset_Generator(fh.test_frames_name, fh.test_labels_name, fh.dir_test_dataset, 1050, 32)

    # Convolutional Neural Network Architecture
    # Convolution layers
    model = models.Sequential()
    model.add(layers.Conv2D(16, (5, 5), padding='same', activation='relu', input_shape=fh.inf_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(32, (3, 3), padding='same', activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), padding='same', activation='relu'))

    # Dense layers
    model.add(layers.Flatten())
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dense(22))

    # Layer summary
    model.summary()

    # Compile the model
    # todo: maybe use a better optimizer / loss function
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    # Create directories to save the model
    fh.recreatedir(fh.dir_checkpoint)

    fh.recreatedir(fh.dir_model)
    fh.recreatedir(fh.dir_frozen_model)

    fh.recreatedir(fh.dir_model_without_opt)
    fh.recreatedir(fh.dir_hdf5)
    fh.recreatedir(fh.dir_weights)

    # Save only the weights after each epoch (even if epoch n+1 is worse than epoch n)
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=str(fh.dir_checkpoint / 'cp-{epoch:04d}.ckpt'),
                                                     save_weights_only=True,
                                                     verbose=1,
                                                     save_freq='epoch')

    # Fit the model
    history = model.fit(x=training_dataset,
                        epochs=10,
                        validation_data=validation_dataset,
                        callbacks=[cp_callback])

    # Saving the entire model and weights in (almost) all possible formats
    model.save(fh.dir_model) # saving the model in the SavedModel format
    model.save(fh.dir_model_without_opt, include_optimizer=False) # saving the model in the SavedModel format (without optimizer)
    model.save(fh.dir_hdf5 / 'model.h5') # saving the model in the hdf5 format
    model.save(fh.dir_hdf5 / 'model_without_opt.h5', include_optimizer=False) # saving the model in the hdf5 format (without optimizer)
    model.save_weights(str(fh.dir_weights / 'cp.ckpt')) # saving the weights
    model.save_weights(str(fh.dir_hdf5 / 'weights.h5')) # saving the weights in the hdf5 format

    # Saving the frozen graph (see https://leimao.github.io/blog/Save-Load-Inference-From-TF2-Frozen-Graph/)
    # Convert the Keras model to a concrete function
    full_model = tf.function(lambda x: model(x))
    full_model = full_model.get_concrete_function(x=tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))

    # Get the frozen concrete function
    frozen_func = convert_variables_to_constants_v2(full_model)
    frozen_func.graph.as_graph_def()

    # Save the frozen graph from the frozen concrete function
    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                      logdir=str(fh.dir_frozen_model),
                      name='frozen_graph.pb',
                      as_text=False)

    # Plot the results
    plt.plot(history.history['accuracy'], label='Training dataset')
    plt.plot(history.history['val_accuracy'], label='Validation dataset')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0.5, 1])
    plt.legend(loc='lower right')
    plt.show()

    # Testing the fitted model by using the test dataset
    test_loss, test_acc = model.evaluate(x=test_dataset, verbose=2)

    print(f'Test accuracy is {test_acc:.3f}')

if __name__ == '__main__':
    main()
