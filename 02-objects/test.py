import sys
import scorelib

file_path = sys.argv[1]

pps = scorelib.load(file_path)

for pp in pps:
    pp.format()
    print()