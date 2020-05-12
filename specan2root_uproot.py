#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
read specan files and convert them to ROOT
using uproot
2020 Xaratustrah

"""

import sys
import os
from iqtools import tools

import types
import uproot
import uproot_methods.classes.TH1


class MyTH1(uproot_methods.classes.TH1.Methods, list):
    def __init__(self, low, high, values, title=""):
        self._fXaxis = types.SimpleNamespace()
        self._fXaxis._fNbins = len(values)
        self._fXaxis._fXmin = low
        self._fXaxis._fXmax = high
        for x in values:
            self.append(float(x))
        self._fTitle = title
        self._classname = "TH1F"


def process(filename):
    gROOT.Reset()
    filename_base = os.path.basename(filename)
    filename_wo_ext = os.path.splitext(filename)[0]
    ff, pp, units = tools.read_trace_xml(filename)
    h1f = MyTH1(ff[0], ff[-1], pp, title=filename_base)
    file = uproot.recreate(filename_wo_ext + '.root',
                           compression=uproot.ZLIB(4))
    file["h1f"] = h1f


def main():
    for file in sys.argv[1:]:
        process(file)


# ------------------------


if __name__ == '__main__':
    main()
