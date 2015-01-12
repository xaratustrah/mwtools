#!/usr/bin/env python
# Convert MWS multi parameteric plots to columns
#
# by github.com/jepio 2014
#

import sys, re

pattern = re.compile("(\d+\.?\d*)")
file = open(sys.argv[1])
out = re.finditer(pattern, file.read())
results = (m.group(1) for m in out)
results = [r for r in results if r not in ("1", "2")]
n = int(len(results) / 3)
for i in range(n):
    print(" ".join(results[i:i + 3]))
