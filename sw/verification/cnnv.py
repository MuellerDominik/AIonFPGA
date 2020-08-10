#!/usr/bin/env python3

'''aionfpga ~ convolutional neural network verification (cnnv)
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import numpy as np

from tensorflow.keras import models

import fhnwtoys.training as fh

def main(verification=fh.Verification.TRAINING, config=fh.DatasetConfig.ALL):
    # Test labels
    test_labels = np.load(fh.dir_test_dataset / f'{fh.test_labels_name}.npy')

    if verification == fh.Verification.TRAINING:
        model = models.load_model(fh.dir_model) # load from tf-model

        model.summary()

        # load test dataset
        if config == fh.DatasetConfig.ALL:
            test_dataset = fh.Dataset_Generator(fh.test_frames_name, fh.test_labels_name, fh.dir_test_dataset, 1050, 32)
        elif config == fh.DatasetConfig.FULLY_VISIBLE_ONLY:
            test_dataset = fh.Dataset_Generator(fh.test_frames_name, fh.test_labels_name, fh.dir_test_dataset, 394, 32)
        else: # fh.DatasetConfig.PARTIALLY_VISIBLE_ONLY
            raise ValueError('This configuration has no use case!')

        # predict only a single image
        # test_frames, test_labels = test_dataset[0] # first batch
        # test_dataset = test_frames[0][np.newaxis, ...] # first frame
        # test_labels = test_labels[0][np.newaxis, ...] # first label

        predictions = model.predict(x=test_dataset)
    else: # fh.Verification.INFERENCE
        if config == fh.DatasetConfig.ALL:
            predictions = np.load(fh.dir_verification / f'{fh.inference_predictions_name}.npy')
        elif config == fh.DatasetConfig.FULLY_VISIBLE_ONLY:
            predictions = np.load(fh.dir_verification / f'{fh.inference_fvo_predictions_name}.npy')
        else: # fh.DatasetConfig.PARTIALLY_VISIBLE_ONLY
            raise ValueError('This configuration has no use case!')

    # Top K accuracy (overall)
    num_objects = fh.num_objects
    num_frames = len(test_labels)

    top_k = fh.top_k(predictions, test_labels, num_objects)
    print(f'Top K (overall): {top_k}')

    # Top K accuracies with K = 1..5 (per object)
    top_k_objects = np.zeros((num_objects, num_objects), dtype=np.float64)
    for idx in range(num_objects):
        indices = np.asarray(test_labels == idx).nonzero()[0]
        predictions_object = predictions[indices, ...]
        labels_object = test_labels[indices, ...]

        top_k_objects[idx] = fh.top_k(predictions_object, labels_object, num_objects)

    objects = fh.objects

    mmax = 0
    for obj in objects:
        if len(obj) > mmax:
            mmax = len(obj)

    for idx, obj in enumerate(top_k_objects):
        print(f'{objects[idx]}:{" "*(mmax - len(objects[idx]))} Top1: {obj[0]:.3f} / Top2: {obj[1]:.3f} / Top3: {obj[2]:.3f} / Top4: {obj[3]:.3f} / Top5: {obj[4]:.3f}')

if __name__ == '__main__':
    # Settings
    verification = fh.verification
    dataset_config = fh.dataset_config

    main(verification, dataset_config)
