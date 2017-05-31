#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calculate waveguide modes

2017
Xaratustra

"""

from scipy.constants import pi, epsilon_0, mu_0, c
import numpy as np
import sys


def eng_notation(value, unit=''):
    ref = {15: 'P', 12: 'T', 9: 'G', 6: 'M', 3: 'k', 0: '', -3: 'm', -6: 'u', -9: 'n', -12: 'p', -15: 'f', }
    num = max([key for key in ref.keys() if value > 10 ** key])
    return '{}{}{}'.format(int(value / 10 ** num * 100) / 100, ref[num], unit)


class WaveGuide:
    def __init__(self, a, b):
        """

        Parameters
        ----------
        a long side x axis corresponding to m
        b short side y axis corresponding to n
        """
        self.a = a
        self.b = b
        self.mu_r = 1
        self.epsilon_r = 1

    def get_fc(self, nmodes):
        #
        fc = []
        np.seterr(all='ignore')
        for m in range(nmodes):
            for n in range(nmodes):
                kmn = np.sqrt((m * np.pi / self.a) ** 2 + (n * np.pi / self.b) ** 2)
                # print(kmn)
                fmn = kmn / 2 / np.pi / np.sqrt(mu_0 * self.mu_r * epsilon_0 * self.epsilon_r)
                if fmn == 0:
                    continue
                lmn = 2 * np.pi / kmn
                row = ['{}{}'.format(m, n), eng_notation(fmn, unit='Hz'), eng_notation(lmn, unit='m'), fmn]
                fc.append(row)
        return fc


# -----------------
if __name__ == "__main__":
    if (len(sys.argv) == 4):
        wg = WaveGuide(float(sys.argv[1]), float(sys.argv[2]))
        results = wg.get_fc(int(sys.argv[3]))
        results.sort(key=lambda row: row[3])  # sort list of list third column
        print('\n'.join(map(str, results)))

    else:
        print(
            'Please provide long side (a) along x axis, short side (b) along y axis in meters and number of desired modes.')
