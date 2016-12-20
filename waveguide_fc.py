#!/usr/bin/env python
"""
Calculates cut off frequency of a waveguie

Dec 2014 Xaratustrah

"""

import sys

import scipy as sp
import scipy.special as sps
import scipy.constants as spc
from decimal import *


class Cutoff:
    CC = 299792458

    def __init__(self, type, dimension):
        self.dimension = dimension
        self.type = str(type)
        if self.type.lower() == 'r':
            self.frequency = self.get_frequency_circular()

        elif self.type.lower() == 'w':
            self.frequency = self.get_frequency_rectangular()

        else:
            print('Type not recognised.')

    def __str__(self):
        strng = "Cutoff frequency is: {} Hz.\n".format(
            self.frequency) + "Cutoff wavelength in freespace is: {} m.".format(
            self.get_wavelength(self.frequency))

        return strng

    def get_frequency_rectangular(self):
        return Cutoff.CC / 2 / self.dimension

    def get_frequency_circular(self):
        return (sps.jnyn_zeros(1, 1)[1] * spc.c / 2 / sp.pi / self.dimension)[0]

    def get_wavelength(self, freq):
        return Cutoff.CC / freq


if __name__ == "__main__":
    if (len(sys.argv) == 3):
        print(Cutoff(sys.argv[1], float(sys.argv[2])))
    else:
        print('Please provide radius (r) or width (w) in meters!')
