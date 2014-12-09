#!/usr/bin/env python
"""
Calculates cut off frequency of a waveguie

Dec 2014 Xaratustrah

"""

import sys

import scipy as sp
import scipy.special as sps
import scipy.constants as spc


class Cutoff:
    def __init__(self, radius):
        self.radius = radius

    def __call__(self):
        return (sps.jnyn_zeros(1, 1)[1] * spc.c / 2 / sp.pi / self.radius)[0]

    def __str__(self):
        return "Cutoff frequency is: {} Hz.".format(self.__call__())


if __name__ == "__main__":
    if (len(sys.argv) == 2):
        print(Cutoff(float(sys.argv[1])))
    else:
        print('Please provide a radius in meters!')
