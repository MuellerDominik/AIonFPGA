#!/usr/bin/env python3

'''aionfpga ~ statistics
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import matplotlib.pyplot as plt

import fhnwtoys.training as fh

# objects_plot = [
#     'Nerf Dart', 'Football', 'Table Tennis', 'Shuttlecock', 'Sporf', 'Arrow',
#     'Featherball', 'Floorball', 'Spiky Ball', 'Tesafilm', 'Sponge',
#     'Red Duplo', 'Green Duplo', 'Duplo Figure', 'Foam Die', 'Infant Shoe',
#     'Bunny', 'Glove', 'Hemp Cord', 'Paper Ball', 'Beer Cap', 'Water Bottle'
# ]

objects_plot = fh.objects_ui

def main():
    noo = fh.num_objects

    frames = [0]*noo
    frames_partial = [0]*noo

    rows = fh.fetch_all_rows(fh.tab_frames)
    for row in rows:
        if row[6] == 1: # valid
            if row[7] == 0: # not partial
                frames[fh.objects.index(row[5])] += 1
            else:
                frames_partial[fh.objects.index(row[5])] += 1

    frames_valid = sum(frames) + sum(frames_partial)
    frames_invalid = len(rows) - frames_valid

    print(f'frames_valid {frames_valid}')
    print(f'frames_invalid {frames_invalid}')

    for idx, o in enumerate(fh.objects):
        if frames[idx] < 500:
            print(f'{o}: {frames[idx]} (+{frames_partial[idx]} partial => {frames[idx] + frames_partial[idx]} total)')

    plt.figure(figsize=[12, 6], tight_layout=True)
    p1 = plt.bar(objects_plot, frames, color=(0, 0.4470, 0.7410))
    p2 = plt.bar(objects_plot, frames_partial, bottom=frames, color=(0.8500, 0.3250, 0.0980))
    plt.legend((p1[0], p2[0]), ('Object fully visible', 'Object partially visible'))
    plt.xticks(rotation=30, ha='right') # formerly 45

    plt.axhline(y=485, c='black', linestyle='--', lw=1.0)
    plt.yticks([0, 200, 400, 485, 600, 800, 1000])

    plt.savefig('statistics.pdf', transparent=True)
    plt.show()

if __name__ == '__main__':
    main()
