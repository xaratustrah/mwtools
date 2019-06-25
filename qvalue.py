#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get Q values from S11 touchstone format
or any other complex vector format

Xaratustrah 2017


Skye 2019
Xaratustrah 2019
"""

import matplotlib.pyplot as plt
import numpy as np
from smithplot import SmithAxes
import sys
import os


def read_touchstone(filename):
    """
    touch stone format:
    freq, real, imaginary
    comma seperated values
    S11 data is centered on the resonance frequency

    Data format:
     HZ   S   RI   R     50.0
    ! Rohde & Schwarz ZVL
    !
    !
    !
    4.021237600000000E8    -6.366180130598420E-1  -7.604446991938126E-1
    ...
    """

    # ignore the first 5 header lines
    sri = np.genfromtxt(filename, skip_header=5)

    freqs = sri[:, 0] / 1e6
    cplx = np.vectorize(complex)(sri[:, 1], sri[:, 2])
    return freqs, cplx


def get_q_values(freqs, cplx, filename):
    file_basename = os.path.basename(filename)
    filename_wo_ext = os.path.splitext(filename)[0]

    # find resonant frequency
    idx_res = np.argmin(np.abs(cplx))
    f_res = freqs[idx_res]

    # determine the rotation angle from the offset for detuned short location
    idx_max = np.argmin(np.abs(cplx)) + 100
    idx_min = np.argmin(np.abs(cplx)) - 100
    rotation = (np.angle(cplx[idx_min]) + np.angle(cplx[idx_max])) / 2

    # find the detuned short position
    # Ae^(jphi-rot) = Acos(phi-rot) + jAsin(phi-rot)

    real_shifted = np.abs(cplx) * np.cos(np.angle(cplx) - rotation)
    imag_shifted = np.abs(cplx) * np.sin(np.angle(cplx) - rotation)
    cplx_shifted = np.vectorize(complex)(real_shifted, imag_shifted)
    # without multiplication with 50 ohm. so it is normalized
    impz_shifted = (1 + cplx_shifted) / (1 - cplx_shifted) * 50

    # find detuned open position
    # real_dop = np.abs(cplx_shifted) * np.cos(np.angle(cplx_shifted) - np.pi)
    # imag_dop = np.abs(cplx_shifted) * np.sin(np.angle(cplx_shifted) - np.pi)
    # cplx_dop = np.vectorize(complex)(real_dop, imag_dop)
    # impz_dop = (1 + cplx_dop) / (1 - cplx_dop) * 50

    # find the index of the point where Re(Z) = |Im(Z)| left of the resonance and call it f5
    f5 = freqs[np.argmin(np.abs(
        np.abs(np.real(impz_shifted)[idx_res - 200: idx_res]) -
        np.abs(np.imag(impz_shifted)[idx_res - 200: idx_res])
    )
    )
        + idx_res - 200]

    # find the index of the point where Re(Z) = |Im(Z)| right of the resonance and call it f6
    f6 = freqs[np.argmin(np.abs(
        np.abs(np.real(impz_shifted)[idx_res: idx_res + 200]) -
        np.abs(np.imag(impz_shifted)[idx_res: idx_res + 200])
    )
    )
        + idx_res]

    # These are the point needed for the unloaded Q
    delta_f_u = np.abs(f5 - f6)
    Qu = f_res / delta_f_u
    print('Qu: ', Qu, '∆fu: ', delta_f_u, 'MHz')

    # These are the point needed for the loaded Q
    f1 = freqs[np.argmax(np.imag(cplx_shifted))]
    f2 = freqs[np.argmin(np.imag(cplx_shifted))]
    delta_f_l = np.abs(f1 - f2)
    Ql = f_res / delta_f_l
    print('Ql: ', Ql, '∆fl: ', delta_f_l, 'MHz')

    # Calculate the external Q from the other two Qs
    Qext = 1 / (1 / Ql - 1 / Qu)
    print('Qext: ', Qext)

    # Calculate the coupling factor
    beta = Qu / Qext
    print('beta', beta)

    # Calculate the external Q using the impedance ~ ±j
    # cnt = 0
    # for z in impz_shifted:
    #     if 0.9 < np.imag(z) < 1.1:
    #         print(z, cnt, freqs[cnt])
    #     cnt += 1
    #
    # cnt = 0
    # for z in impz_shifted:
    #     if -0.9 > np.imag(z) > -1.1:
    #         print(z, cnt, freqs[cnt])
    #     cnt += 1
    # f2 = freqs[np.argmin(
    #     np.abs(np.imag(impz_shifted) - np.ones(len(impz_shifted))))]
    # f3 = freqs[np.argmin(np.abs(np.imag(impz_shifted) -
    #                             (np.ones(len(impz_shifted)) * -1)))]
    # print(f2, f3)
    # Qext = f_res / (np.abs(f2 - f3))
    # print('Qext: ', Qext)

    # Plot section
    plt.figure()  # figsize=(6, 6))
    ax = plt.subplot(1, 1, 1, projection='smith', grid_minor_enable=False)
    plt.plot(cplx, markevery=10, label='Measurement data',
             datatype=SmithAxes.S_PARAMETER)
    plt.plot(cplx_shifted, markevery=10, label='Detuned short position',
             datatype=SmithAxes.S_PARAMETER)
    # plt.plot(cplx_dop, markevery=10, label='Detuned open position',
    #         datatype=SmithAxes.S_PARAMETER)
    plt.legend(loc="lower right", fontsize=8)
    plt.title(file_basename)
    print('Plotting to file {}.png'.format(filename_wo_ext))
    txt = 'Qu={:0.0f}, Ql={:0.0f}\n∆fu={:0.3f} [MHz]\nf_res={:0.3f} [MHz]\nbeta={:.3f}'.format(
        Qu, Ql, delta_f_u, f_res, beta)
    plt.text(0, 0.6, txt, size=9, rotation=0,
             ha="left", va="top",
             bbox=dict(boxstyle="square",
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )

    plt.savefig("{}.png".format(filename_wo_ext),
                format="png",
                dpi=600,
                bbox_inches="tight",)

    plt.clf()

# ------------------------


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        print('Filename: ', filename)
        ff, cc = read_touchstone(filename)
        get_q_values(ff, cc, filename)
