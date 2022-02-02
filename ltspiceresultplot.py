#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Result plotter for LTSpice
On the waveform windown press
Control Panel --> Wave forms --> Data export tool
then you can choose which waveform

for .tran it will be just a set of numbers, that you can read using numpy.genfromtxt.
This code is not for the this data.

time	V(n001)
0.000000000000000e+00	1.000000e+00
9.827253125149416e-03	1.000000e+00
...


This code is written for the output of the .tran analysis  when you use the FFT view,
OR if you use the .ac analysis and you export the frequency pliot. If you export you
will see:

Freq.	V(n001)
0.00000000000000e+00	-2.74728468664485e-06,0.00000000000000e+00
1.00000000000000e+02	8.15613523074404e-07,-5.20373025231768e-07
...


2022 Xaratustrah

"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt


def process(filename):
    filename_base = os.path.basename(filename)
    filename_wo_ext = os.path.splitext(filename)[0]

    dd = []
    with open(filename) as f:
        f.readline()
        for line in f.readlines():
            line = line.replace('\n', '')
            line = line.replace('\t', ',')
            line = line.split(',')
            dd.append([float(line[0]), float(line[1]), float(line[2])])

    dda = np.array(dd)

    plt.plot(dda[:, 0], dda[:, 1], 'r')
    plt.xscale('log')
    plt.grid()
    plt.ylabel('Magnitude')
    plt.xlabel('Freq.')
    plt.savefig(filename_wo_ext + '_mag.png')

    plt.clf()

    plt.plot(dda[:, 0], dda[:, 2])
    plt.xscale('log')
    plt.grid()
    plt.ylabel('Phase')
    plt.xlabel('Freq.')
    plt.savefig(filename_wo_ext + '_phase.png')

    return dda


def main():
    for file in sys.argv[1:]:
        process(file)


# ------------------------


if __name__ == '__main__':
    main()
