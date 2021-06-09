import os
import sys
import argparse
from argparse import RawTextHelpFormatter
from itertools import chain as add_last
from math import log
import collections
import math

def is_valid_file(x):
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

def encode(string):
    result = 1
    for char in string:
        result = (result << 2) | ((ord(char) >> 1) & 3)
    return result

def entropy(sequence, k=4):
	H = 0
	counts = dict()
	for i in range(0, len(sequence)-k+1):
		seq = sequence[i:i+k]
		counts[seq] = counts.get(seq, 0) + 1
	total = sum(counts.values())
	for count in counts.values():
		H += (count/total) * log(count/total)		
	return -H


bases = ['A','C','T','G']
def make_perms(s, allow):
	if not allow:
		yield s
	else:
		for i, c in enumerate(s):
			for other in bases :
				yield s[0:i]  + other + s[i+1:]

usage = '%s [-opt1, [-opt2, ...]] file1 file2' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('file1', type=is_valid_file, help='input file')
parser.add_argument('file2', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
parser.add_argument('-m', '--min', type=int, default=30, help='minimum length of overlap')
parser.add_argument('-e', '--entropy', type=int, default=0, help='size of kmers to show entropy for alignment')
parser.add_argument('-a', '--allow', action='store_true', help='allow 1 mismatch')
parser.add_argument('-s', '--skip', action='store_true', help='skip output if they are the same file')
args = parser.parse_args()

# SKIP OUTPUT IF FILE1 AND FILE2 ARE THE SAME FILE
if args.skip and args.file1 == args.file2:
	exit()

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
				for kmer in make_perms(seq[:len(seq)-i], args.allow):
					#bits = encode(seq[:len(seq)-i])
					if kmer in rights:
						for right in rights[kmer]:
							if right not in seen:
								print(head, '_', right, sep='', end=',')
								print('1'.rjust(4), end=',')
								print(str(length[right] - len(kmer) + 1).rjust(4), end=',')
								print(str(len(kmer)).rjust(4), end=', ')
								print(kmer, end='')
								if args.entropy:
									print(', ', end='')
									print(entropy(kmer, args.entropy), end='')
								print()
							seen[right] = True
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip()

