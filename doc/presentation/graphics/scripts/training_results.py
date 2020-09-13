#!/usr/bin/env python3

'''aionfpga ~ training results
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import matplotlib.pyplot as plt

x = range(1,11)

loss = [0.4974, 0.0775, 0.0523, 0.0438, 0.0401, 0.0351, 0.0326, 0.0355, 0.0295, 0.0325]
val_loss = [0.1564, 0.0365, 0.0324, 0.0671, 0.0121, 0.0115, 0.0374, 0.0979, 0.0148, 0.0168]

accuracy = [0.8248, 0.9758, 0.9846, 0.9880, 0.9896, 0.9913, 0.9919, 0.9917, 0.9931, 0.9930]
val_accuracy = [0.9511, 0.9885, 0.9892, 0.9821, 0.9960, 0.9969, 0.9914, 0.9752, 0.9959, 0.9958]

def main():
    plt.figure(figsize=[6, 3], tight_layout=True)
    plt.plot(x, accuracy, color=(0, 0.4470, 0.7410), label='Training dataset')
    plt.plot(x, val_accuracy, color=(0.8500, 0.3250, 0.0980), label='Validation dataset')
    plt.axhline(y=1.0, c='grey', linestyle='--', lw=1.0)
    plt.xlabel('Epoch')
    plt.xticks(x)
    plt.ylabel('Classification Accuracy')
    plt.legend(loc='lower right')
    plt.savefig('training_results.pdf', transparent=True)
    plt.show()

if __name__ == '__main__':
    main()
