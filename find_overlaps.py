import os
import sys
import argparse
from argparse import RawTextHelpFormatter
from itertools import chain as add_last

def is_valid_file(x):
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

def encode(string):
    result = 1
    for char in string:
        result = (result << 2) | ((ord(char) >> 1) & 3)
    return result

usage = '%s [-opt1, [-opt2, ...]] file1 file2' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('file1', type=is_valid_file, help='input file')
parser.add_argument('file2', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
parser.add_argument('-m', '--min', type=int, default=30, help='minimum length of overlap')
args = parser.parse_args()


# GO THROUGH FIRST FILE AND FIND ALL POSSIBLE KMERS ON RIGHT
rights = dict()
length = dict()
head = seq = ''
with open(args.file2) as fp:
	for line in add_last(fp, '>'):
		if line.startswith('>'):
			length[head] = len(seq)
			for i in range(len(seq) - args.min + 1):
				rights.setdefault(seq[i:],[]).append(head)
				#rights.setdefault(encode(seq[i:]),[]).append(head)
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip()

# GO THROUGH OTHER FILE AND FIND ALL POSSIBLE KMERS ON LEFT
head = seq = ''
with open(args.file1) as fp:
	for line in add_last(fp, '>'):
		if line.startswith('>'):
			seen = dict()
			for i in range(len(seq) - args.min + 1):
				kmer = seq[:len(seq)-i]
				#bits = encode(seq[:len(seq)-i])
				if kmer in rights:
					for right in rights[kmer]:
						if right not in seen:
							print(head, '_', right, sep='', end=',')
							print('1'.rjust(4), end=',')
							print(str(length[right] - len(kmer) + 1).rjust(4), end=',')
							print(str(len(kmer)).rjust(4), end=', ')
							print(kmer)
						seen[right] = True
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip()

