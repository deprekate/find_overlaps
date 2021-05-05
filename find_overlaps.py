import os
import sys
import argparse
from argparse import RawTextHelpFormatter
from itertools import chain as add_last

def is_valid_file(x):
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

usage = '%s [-opt1, [-opt2, ...]] file1 file2' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('file1', type=is_valid_file, help='input file')
parser.add_argument('file2', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
parser.add_argument('-m', '--min', type=int, default=30, help='minimum length of overlap')
args = parser.parse_args()


# GO THROUGH FIRST FILE AND FIND ALL POSSIBLE KMERS ON RIGHT
rights = dict()
head = seq = ''
with open(args.file1) as fp:
	for line in add_last(fp, '>'):
		if line.startswith('>'):
			for i in range(len(seq) - args.min + 1):
				rights.setdefault(seq[i:],[]).append(head)
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip()
#for i in range(len(seq) - args.min + 1):
#	rights.setdefault(seq[i:],[]).append(head)

# GO THROUGH OTHER FILE AND FIND ALL POSSIBLE KMERS ON LEFT
head = seq = ''
with open(args.file2) as fp:
	for line in add_last(fp, '>'):
		if line.startswith('>'):
			for i in range(len(seq) - args.min):
				kmer = seq[:len(seq)-i]
				if kmer in rights:
					for right in rights[kmer]:
						print(right, '_', head, sep='', end=',   ')
						print('1', end=',   ')
						print(len(kmer), end=',   ')
						print(kmer)
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip()

