#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
read specan files and convert them to ROOT

2020 Xaratustrah

"""

import sys
import os
from iqtools import tools
from ROOT import TH1F, TFile
from ROOT import gROOT


def process(filename):
    gROOT.Reset()
    filename_base = os.path.basename(filename)
    filename_wo_ext = os.path.splitext(filename)[0]
    ff, pp, units = tools.read_trace_xml(filename)
    h1f = TH1F('h1f', filename_base, len(ff), ff[0], ff[-1])
    for i in range(len(pp)):
        h1f.SetBinContent(i, pp[i])
    myfile = TFile(filename_wo_ext + '.root', 'RECREATE')
    h1f.Write()
    myfile.Close()


def main():
    for file in sys.argv[1:]:
        process(file)


# ------------------------


if __name__ == '__main__':
    main()
