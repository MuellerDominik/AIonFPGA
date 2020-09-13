#!/usr/bin/env python3

'''aionfpga ~ weighting function
Copyright (C) 2020 Dominik Müller and Nico Canzani
'''

import numpy as np
import matplotlib.pyplot as plt

end = 44

# adapted from https://stackoverflow.com/questions/33737736/matplotlib-axis-arrow-tip
def arrowed_spines(fig, ax):

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    xmax += 1
    ymax += 0.1

    # spines
    ax.spines['left'].set_position('zero')
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # removing the axis ticks
    ax.grid(False)

    # get width and height of axes object to compute matching arrowhead length and width
    dps = fig.dpi_scale_trans.inverted()
    bbox = ax.get_window_extent().transformed(dps)
    width, height = bbox.width, bbox.height

    # manual arrowhead width and length
    hw = 1./30.*(ymax-ymin)
    hl = 1./30.*(xmax-xmin)
    lw = 1. # axis line width
    ohg = 0.3 # arrow overhang

    # compute matching arrowhead length and width
    yhw = hw/(ymax-ymin)*(xmax-xmin)* height/width
    yhl = hl/(xmax-xmin)*(ymax-ymin)* width/height

    # draw x and y axis
    ax.arrow(xmin, 0, xmax-xmin, 0., fc='k', ec='k', lw = lw,
             head_width=hw, head_length=hl, overhang = ohg,
             length_includes_head= True, clip_on = False)

    ax.arrow(0, ymin, 0., ymax-ymin, fc='k', ec='k', lw = lw,
             head_width=yhw, head_length=yhl, overhang = ohg,
             length_includes_head= True, clip_on = False)

def y(k, N=end):
    return np.sin(k/(N + 1) * np.pi)**2

t1 = np.linspace(-0.5, end + 1.5, 1001)
y1 = y(t1)

t2 = np.linspace(1, min(22,end), min(22,end))
y2 = y(t2)

rc = {"xtick.direction" : "inout", "ytick.direction" : "inout", "xtick.major.size" : 6, "ytick.major.size" : 6}
with plt.rc_context(rc):
    fig, ax = plt.subplots(figsize=[8, 4])
    ax.grid(b=True, which='major', color='#666666', linestyle='-')
    ax.grid(b=True, which='minor', color='#bbbbbb', linestyle='-')
    ax.set_xticks(list(range(1,end+3,2)))
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.plot(t1, y1, color='gray', linestyle='--')
    ax.scatter(t2, y2, zorder=3, color=(0, 0.4470, 0.7410))

    for i in range(1, min(22,end) + 1):
        ax.vlines(i, 0, y2[i-1], color='gray', lw=1, linestyles='dotted')

    plt.xlabel('$k$')
    plt.ylabel('Weighting Factor $w_k$')

    arrowed_spines(fig, ax)

    plt.savefig('weighting_function.pdf', transparent=True, bbox_inches='tight')
    plt.show()
