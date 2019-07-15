#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get Q values from S11 touchstone format
or any other complex vector format

Based on the paper by F. Caspers
http://arxiv.org/abs/1201.4068

More info also in:
Microwave Measurements, E. Ginzton, McGraw-Hill 1957


Code history:

Xaratustrah 2017
Skye 2019
Xaratustrah 2019
"""

import matplotlib.pyplot as plt
import numpy as np
from smithplot import SmithAxes
from scipy.signal import savgol_filter
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
    file_basename_wo_ext = file_basename.split('.')[0]

    # find resonant frequency
    idx_res = np.argmin(np.abs(cplx))
    f_res = freqs[idx_res]

    # determine the rotation angle from the offset for detuned short location
    idx_max = np.argmin(np.abs(cplx)) + 50
    idx_min = np.argmin(np.abs(cplx)) - 50
    rotation = (np.angle(cplx[idx_min]) + np.angle(cplx[idx_max])) / 2

    # find the detuned short position
    # Ae^(jphi-rot) = Acos(phi-rot) + jAsin(phi-rot)
    # filter using Savgol filter
    add_angle = 0
    if rotation < 0:
        add_angle = np.pi

    real_dsp = np.abs(cplx) * np.cos(np.angle(cplx) - rotation + add_angle)
    real_dsp = savgol_filter(real_dsp, 51, 3)

    imag_dsp = np.abs(cplx) * np.sin(np.angle(cplx) - rotation + add_angle)
    imag_dsp = savgol_filter(imag_dsp, 51, 3)
    cplx_dsp = np.vectorize(complex)(real_dsp, imag_dsp)
    impz_dsp = (1 + cplx_dsp) / (1 - cplx_dsp) * 50

    # find detuned open position
    real_dop = np.abs(cplx_dsp) * np.cos(np.angle(cplx_dsp) - np.pi)
    imag_dop = np.abs(cplx_dsp) * np.sin(np.angle(cplx_dsp) - np.pi)
    cplx_dop = np.vectorize(complex)(real_dop, imag_dop)
    impz_dop = (1 + cplx_dop) / (1 - cplx_dop) * 50

    # Calculating unloaded Q
    # find the index of the point where Re(Z) = |Im(Z)| left of the resonance and call it f5
    offset = 100
    f5 = freqs[np.argmin(np.abs(
        np.abs(np.real(impz_dsp)[idx_res - offset: idx_res]) -
        np.abs(np.imag(impz_dsp)[idx_res - offset: idx_res])
    )
    )
        + idx_res - offset]

    # find the index of the point where Re(Z) = |Im(Z)| right of the resonance and call it f6
    f6 = freqs[np.argmin(np.abs(
        np.abs(np.real(impz_dsp)[idx_res: idx_res + offset]) -
        np.abs(np.imag(impz_dsp)[idx_res: idx_res + offset])
    )
    )
        + idx_res]

    delta_f_u = np.abs(f5 - f6)
    Qu = f_res / delta_f_u
    print('Qu: ', Qu, '∆fu: ', delta_f_u, 'MHz')

    # Calculating the loaded Q
    f1 = freqs[np.argmax(np.imag(cplx_dsp))]
    f2 = freqs[np.argmin(np.imag(cplx_dsp))]
    delta_f_l = np.abs(f1 - f2)
    Ql = f_res / delta_f_l
    print('Ql: ', Ql, '∆fl: ', delta_f_l, 'MHz')

    # Calculate the external Q from the other two Qs
    Qext_calc = 1 / (1 / Ql - 1 / Qu)
    print('Qext_calc: ', Qext_calc)

    # Calculate the coupling factor
    beta_calc = Qu / Qext_calc
    print('beta_calc', beta_calc)

    # Alternative calculation of the external Q using the impedance ~ ±j
    # you need to use the detuned open position for this
    # find the first zero crossing from beginning to half of the vector
    # https://stackoverflow.com/a/3843124/5177935
    #
    f3 = freqs[np.where(np.diff(np.sign(np.imag(impz_dop[:idx_res]))))[0][0]]
    # now on the second half of the array
    f4 = freqs[np.where(np.diff(np.sign(np.imag(impz_dop[idx_res:]))))[
        0][0] + idx_res]
    delta_f_ext = np.abs(f3 - f4)
    Qext_meas = f_res / delta_f_ext
    print('Qext_meas: ', Qext_meas)

    # Calculate the coupling factor
    beta_meas = Qu / Qext_meas
    print('beta_meas', beta_meas)

    # Plot section
    plt.figure()  # figsize=(6, 6))
    ax = plt.subplot(1, 1, 1, projection='smith', grid_minor_enable=True)
    plt.plot(cplx, markevery=10, label='Measurement data',
             datatype=SmithAxes.S_PARAMETER)
    plt.plot(cplx_dsp, markevery=10, label='Detuned short position',
             datatype=SmithAxes.S_PARAMETER)
    plt.plot(cplx_dop, markevery=10, label='Detuned open position',
             datatype=SmithAxes.S_PARAMETER)
    plt.legend(loc="lower right", fontsize=8)
    plt.title(file_basename_wo_ext)
    print('Plotting to file {}.png'.format(filename_wo_ext))
    txt = 'Qu={:0.0f}, Ql={:0.0f}\n∆fu={:0.3f} [MHz]\nf_res={:0.3f} [MHz]\nbeta={:.3f}'.format(
        Qu, Ql, delta_f_u, f_res, beta_calc)
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
    return file_basename_wo_ext, Qu, Ql, delta_f_u, f_res, beta_calc


# ------------------------


if __name__ == '__main__':
    with open('results.txt', 'a') as the_file:
        the_file.write('#file, Qu, Ql, delta_f_u, f_res, beta\n')
        for filename in sys.argv[1:]:
            print('Filename: ', filename)
            ff, cc = read_touchstone(filename)
            the_file.write(','.join(str(s)
                                    for s in get_q_values(ff, cc, filename)) + '\n')
