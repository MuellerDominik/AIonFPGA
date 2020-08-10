#!/usr/bin/env python3

'''aionfpga ~ dataset generator
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import cv2

import math
import numpy as np

import fhnwtoys.training as fh

def save_batches(frames_name, labels_name, dst, frame_names, batch_size):

    num_frames = len(frame_names)
    num_batches = math.ceil(num_frames / batch_size)

    labels = np.empty((num_frames,), dtype=np.uint8)
    for idx in range(num_batches):
        start = idx * batch_size
        end = start + batch_size
        frame_names_slice = frame_names[start:end]

        frames = np.empty((len(frame_names_slice),) + fh.inf_shape, dtype=np.uint8)
        for i, frame in enumerate(frame_names_slice):
            obj_san = frame.split('_')[3]
            label = fh.objects_san.index(obj_san)
            frames[i] = cv2.imread(str(fh.dir_frames_augmented / f'{frame}.png'))
            labels[idx * batch_size + i] = label

        np.save(dst / f'{frames_name}_batch_{idx}_of_{num_batches}.npy', frames)

    np.save(dst / f'{labels_name}.npy', labels)

'''training dataset (~70%): used to fit the model
validation dataset (~15%): unbiased evaluation of the model fit on the training dataset while tuning model hyperparameters
test dataset (~15%): unbiased evaluation of the final model fit on the training dataset
calibration dataset (45 x 22 = 990 images): small unlabeled dataset for calibration (during the quantization) taken from the validation dataset [5..45 frames per class (110..990)]
'''

def main(config=fh.DatasetConfig.ALL, brightness=False, flipping=False):
    # Setup
    rng = fh.RNG(fh.seed)

    multiplier = 1 # Dataset multiplier

    # Brightness augmentation
    brightnesses = [85, 100, 115, 130, 145, 160]
    if brightness:
        multiplier *= len(brightnesses) + 1 # +1: also include original frame

    # Horizontal and vertical flip augmentation
    if flipping:
        multiplier *= 2 + 1 # +1: also include original frame

    # Fetch all rows from the database
    all_rows = fh.fetch_all_rows(fh.tab_frames)

    # determine the desired frames by listing the key 'frame'
    frames_dict = {}
    for row in all_rows:
        if row[3] == 1: # calculate brightness of the first frame of each throw
            img = cv2.imread(str(fh.dir_frames / f'{row[4]}'))
            brightness = float(np.sum(img) / (1280 * 1024 * 3))
            rounded_brightness = round(brightness)
        # dict with the key 'frame' (value holds all the information about a single 'frame')
        frames_dict[row[4]] = {
            'id': row[0],
            'timestamp': row[1],
            'throwid': row[2],
            'frameid': row[3],
            'object': row[5],
            'framegood': row[6],
            'partial': row[7],
            'brightness': rounded_brightness, # brightness of the first frame of the throw
        }

    frames_list = []
    for idx, obj in enumerate(fh.objects):
        if config == fh.DatasetConfig.ALL:
            frames = [f[0] for f in fh.fetch_rows(fh.tab_frames, 'object', obj, 'frame')]
        elif config == fh.DatasetConfig.FULLY_VISIBLE_ONLY:
            frames = [f[0] for f in fh.fetch_rows(fh.tab_frames, 'object', obj, 'frame') if frames_dict[f[0]]['partial'] == 0]
        else: # fh.DatasetConfig.PARTIALLY_VISIBLE_ONLY
            raise ValueError('This configuration has no use case!')
        frames_list.append(frames)

    min_frames = min([len(frames) for frames in frames_list])

    # shuffle frames in place and only use the same (min_frames) amount for each object
    for idx, frames in enumerate(frames_list):
        rng.shuffle(frames)
        frames_list[idx] = frames[0:min_frames]

    # the total size of the dataset after augmentation
    total_amount = min_frames * fh.num_objects * multiplier

    validation_amount = math.floor(0.15 * total_amount / fh.num_objects) * fh.num_objects # ~15%
    test_amount = validation_amount # ~15%, same as 'validation_amount'
    training_amount = total_amount - validation_amount - test_amount # ~70%

    calibration_amount = (1000 // fh.batch_size_calibration) * fh.num_objects # 5..45 frames per class (110..990)

    fh.recreatedir(fh.dir_frames_augmented)

    frames_list_augmented = [] # names (without .png extension)
    for frames in frames_list:
        for frame in frames:
            print(f'Augmenting frame {frame}')
            name = frame.split('.')[0] # remove .png extension
            names = [name]

            img = cv2.imread(str(fh.dir_frames / frame))
            img_resized = cv2.resize(img, fh.inf_dsize, interpolation=fh.Interpolation.NEAREST)

            imgs = [img_resized]

            if brightness:
                img_int16 = img_resized.astype(np.int16)
                for brightness in brightnesses:
                    offset = brightness - frames_dict[frame]['brightness']

                    img_offsetted = img_int16 + offset
                    img_clipped = np.clip(img_offsetted, 0, 255)
                    img_uint8 = img_clipped.astype(np.uint8)

                    imgs.append(img_uint8)
                    names.append(f'{name}_{brightness}')

            if flipping:
                imgs_flipped = []
                names_flipped = []
                for name, img in zip(names, imgs):
                    flipped_v = cv2.flip(img, 0)
                    imgs_flipped.append(flipped_v)
                    names_flipped.append(f'{name}_v')
                    flipped_h = cv2.flip(img, 1)
                    imgs_flipped.append(flipped_h)
                    names_flipped.append(f'{name}_h')

                imgs.extend(imgs_flipped)
                names.extend(names_flipped)

            for name, img in zip(names, imgs):
                cv2.imwrite(str(fh.dir_frames_augmented / f'{name}.png'), img)

            frames_list_augmented.extend(names)

    rng.shuffle(frames_list_augmented) # shuffle 'frames_list_augmented' in place

    training_dataset = frames_list_augmented[0:training_amount]
    validation_dataset = frames_list_augmented[training_amount:training_amount + validation_amount]
    test_dataset = frames_list_augmented[training_amount + validation_amount:]
    calibration_dataset = validation_dataset[-calibration_amount:]

    print('Saving training dataset')
    fh.recreatedir(fh.dir_training_dataset)
    save_batches(fh.training_frames_name, fh.training_labels_name, fh.dir_training_dataset, training_dataset, fh.batch_size)
    print('Saving validation dataset')
    fh.recreatedir(fh.dir_validation_dataset)
    save_batches(fh.validation_frames_name, fh.validation_labels_name, fh.dir_validation_dataset, validation_dataset, fh.batch_size)
    print('Saving test dataset')
    fh.recreatedir(fh.dir_test_dataset)
    save_batches(fh.test_frames_name, fh.test_labels_name, fh.dir_test_dataset, test_dataset, fh.batch_size)
    print('Saving calibration dataset')
    fh.recreatedir(fh.dir_calibration_dataset)
    save_batches(fh.calibration_frames_name, fh.calibration_labels_name, fh.dir_calibration_dataset, calibration_dataset, fh.batch_size_calibration)

if __name__ == '__main__':
    # Settings
    dataset_config = fh.dataset_config
    brightness = True # Brightness augmentation
    flipping = True # Horizontal and vertical flip augmentation

    main(dataset_config, brightness, flipping)
