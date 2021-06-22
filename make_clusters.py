import os
import sys
import argparse
from argparse import RawTextHelpFormatter
from itertools import chain as chain
from math import log
import collections
import math

def is_valid_file(x):
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x


usage = '%s [-opt1, [-opt2, ...]] file1 file2' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('infile', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
args = parser.parse_args()



clusters = list()
where = dict()
with open(args.infile) as fp:
	for line in fp:
		read1,read2 = line.split('\t')[:2]
		if read1 not in where and read2 not in where:
			l = [read1, read2]
			clusters.append(l)
			where[read1] = l
			where[read2] = l
		elif read1 in where:
			where[read1].append(read2)
		elif read2 in where:
			where[read2].append(read1)
		

for cluster in clusters:
	print(len(cluster) - 1, cluster)
