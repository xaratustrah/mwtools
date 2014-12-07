#!/usr/bin/python
# coding: utf-8

"""Bandwidth measurement application.

usage:
bandwidth <filename> <type>

type: s11, s21\
"""
from __future__ import print_function
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import cmath
import sys


def trace_process(data, s11=True, plot=True):
    """Calculate the bandwidth from VNA trace data."""
    # Columns of data are: freq (Hz), mag (dB), phase (deg)
    if s11:
        peak_freq = np.argmin(data[:, 1])
    else:
        peak_freq = np.argmax(data[:, 1])

    phase_at_peak = data[peak_freq, 2]
    # subtract phase from all measurements and convert to radians
    data[:, 2] = (data[:, 2] - phase_at_peak)*np.pi*0.00555555555
    # convert dB S11 to lin S11
    data[:, 1] = 10 ** (data[:, 1] / 20)
    # convert to complex and then to imaginary
    imaginary_part = data[:, 1]*np.sin(data[:, 2])
    # find max and min imaginary
    freq_imag_min = data[np.argmin(imaginary_part), 0]
    freq_imag_max = data[np.argmax(imaginary_part), 0]

    # printing extras
    format_string = "Frequency of imaginary {} {:d}"
    flag = "minimum" if s11 else "maximum"
    # Data output
    print("Frequency at {}: {:d} Hz".format(flag, int(data[peak_freq, 0])))
    #print(format_string.format("maximum", int(freq_imag_max)))
    #print(format_string.format("minimum", int(freq_imag_min)))
    bandwidth = abs(freq_imag_max - freq_imag_min)
    print("Bandwidth {:.6f} kHz".format(bandwidth * 1e-3))
    q = data[peak_freq, 0] / bandwidth
    print("Q {:.0f}".format(q))
    if plot is False:
        return
    # Plots
    plt.figure(0, figsize=(8, 5))
    plt.plot(data[:, 0], imaginary_part)
    plt.title("Imaginary vs. frequency")
    plt.savefig("imag.png")
    plt.clf()
    plt.polar(data[:, 2], data[:, 1])  # first phase, then r
    plt.scatter(data[peak_freq, 2], data[peak_freq, 1], c='r', marker='o')
    plt.title("S11 in polar", va="bottom")
    plt.savefig("polar.png")
    plt.clf()
    plt.plot(data[:, 0], data[:, 1])
    plt.title("S11 curve in linear scale")
    plt.savefig("curve.png")
    plt.close("all")


def main():
    if len(sys.argv) not in [2, 3]:
        print(__doc__)
        sys.exit(1)
    filename = sys.argv[1]
    s11_flag = None
    try:
        if sys.argv[2] == "s11":
            s11_flag = True
        elif sys.argv[2] == "s21":
            s11_flag = False
    except:
        print("Assuming S11")
        s11_flag = True

    data = np.loadtxt(filename, skiprows=5)  # it's 5,not 3, due to ^M
    trace_process(data, s11_flag, False)


if __name__ == "__main__":
    main()
