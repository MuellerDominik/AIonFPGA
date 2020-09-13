#!/usr/bin/env python3

'''aionfpga ~ throw analysis
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import numpy as np

import matplotlib.pyplot as plt

import fhnwtoys.training as fh

rows = fh.fetch_all_rows(fh.tab_frames)

nofs = list() # number of frames of each throw

fid = 1
nof = 0
for row in rows:
    if row[2] == fid:
        nof += 1
    else:
        nofs.append(nof)
        # print(nofs)
        nof = 1
        fid += 1
nofs.append(nof)

# print(max(nofs))
# print(len(nofs))
# print(sum(nofs))

x1 = range(1, max(nofs) + 1)
x2 = range(1, max(nofs) + 2)

hist, _ = np.histogram(nofs, bins=max(nofs))
cumsum = np.cumsum(hist) / len(nofs)
cumsum = [0,] + list(cumsum)

# print(list(hist))
# print(cumsum)

fig, ax = plt.subplots(figsize=[8, 4])
ax.bar(x1, hist)

plt.xticks([t+1 for t in range(max(nofs)) if t%9 == 0])

plt.xlabel('Number of Frames $x$')
plt.ylabel('Number of Throws')

plt.savefig('distribution.pdf', transparent=True, bbox_inches='tight')

# --------------------------------------------

fig, ax = plt.subplots(figsize=[8, 4])
ax.step(x2, cumsum)

bottom, top = plt.ylim()
plt.ylim(0, top)

plt.autoscale(False)

ax.hlines(0.8, -5, 22, colors='gray', ls='--', lw=1)
ax.vlines(22, 0, 0.8,colors='gray', ls='--', lw=1)

plt.xticks([t+1 for t in range(max(nofs)) if t%9 == 0 or t == 21])

plt.xlabel('Number of Frames $x$')
plt.ylabel('Probability')

plt.savefig('cumulative_distribution.pdf', transparent=True, bbox_inches='tight')

plt.show()
