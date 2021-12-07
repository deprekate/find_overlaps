import os
import sys
import argparse
from argparse import RawTextHelpFormatter
from itertools import chain as chain
from itertools import repeat
from math import log
import collections
import math


def is_valid_file(x):
    if not os.path.isdir(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

usage = '%s [-opt1, [-opt2, ...]] directory' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('directory', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
parser.add_argument('-c', '--column', type=int, default=1, help='The column to look for the sequence in')
parser.add_argument('-x', '--exact', action='store_true', help='Allow only exact matches')
#parser.add_argument('-r', '--revcomp', action='store_true', help='do reverse complement comparison')
args = parser.parse_args()


files = sorted( os.listdir(args.directory) )

# OPEN ALL THE FILES AND GET ALL THE SEQUENCES
args.outfile.write('sequence')
sequences = dict()
for name in files:
	args.outfile.write('\t')
	args.outfile.write(name)
	with open(os.path.join(args.directory, name)) as f:
		for line in f:
			seq = line.rstrip().split('\t')[args.column - 1]
			if seq:
				sequences[seq] = True
args.outfile.write('\n')

# Go THROUGH EACH FILE AND FIND WHETHER THE SEQ IS PRESENT
for seq in sequences.keys():
	args.outfile.write(seq)
	for name in files:
		with open(os.path.join(args.directory, name)) as f:
			seen = '0'
			for line in f:
				rseq = line.rstrip().split('\t')[args.column - 1]
				if seq and (not args.exact and seq in rseq) or seq == rseq:
					seen = '1'
		args.outfile.write('\t')
		args.outfile.write(seen)
	args.outfile.write('\n')






