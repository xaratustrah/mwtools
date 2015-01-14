#!/usr/bin/env python
"""Convert MWS multi parameteric plots to columns

by github.com/jepio 2014"""

from __future__ import print_function, division
import sys, re
from itertools import islice

number_pattern = re.compile("(\d+\.?\d*([eE][+-]\d+)?)")

def parse(run_data):
    data = re.finditer(number_pattern, run_data)
    run_number = next(data).group(1)
    # Once the run number has been removed, every second entry is an R/Q
    # value.
    numbers = (match.group(1) for match in data)
    r_over_q = islice(numbers, 1, None, 2)
    return (run_number, " ".join(r_over_q,))

file_ = open(sys.argv[1])
data = file_.read()
runs = data.split("Mode Number")

for run in runs[1:]:
    run_number, r_over_q = parse(run)
    print(run_number, r_over_q)
