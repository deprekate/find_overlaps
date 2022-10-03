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
#parser.add_argument('-x', '--exact', action='store_true', help='Allow only exact matches')
#parser.add_argument('-r', '--revcomp', action='store_true', help='do reverse complement comparison')
args = parser.parse_args()


files = sorted( os.listdir(args.directory) )

# OPEN ALL THE FILES AND GET ALL THE SEQUENCES
args.outfile.write('sequence')
sequences = dict()
for name in files:
	with open(os.path.join(args.directory, name)) as f:
		args.outfile.write('\t')
		args.outfile.write(name)
		for line in f:
			seq = line.rstrip().split('\t')[args.column - 1]
			if seq:
				if seq not in sequences:
					sequences[seq] = [name]
				else:
					sequences[seq].append(name)
args.outfile.write('\n')


# Go THROUGH THE SEQS OF EACH FILE AND FIND WHETHER THE SEQ IS PRESENT
for seq,names in sequences.items():
	args.outfile.write(seq)
	for name in files:
		args.outfile.write('\t')
		if name in names:
			args.outfile.write('1')
		else:
			args.outfile.write('0')
	args.outfile.write('\n')






