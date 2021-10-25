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
trans = str.maketrans('ACTG', 'TGAC')
def make_kmers(s, args):
	if args.allow:
		for i, c in enumerate(s):
			for other in bases :
				yield s[0:i]  + other + s[i+1:]
				if args.revcomp:
					yield ''.join([s[0:i], other, s[i+1:]]).translate(trans)[::-1]
	else:
		yield s
		if args.revcomp:
			yield s.translate(trans)[::-1]


usage = '%s [-opt1, [-opt2, ...]] file1 file2' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('file1', type=is_valid_file, help='input file')
parser.add_argument('file2', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
parser.add_argument('-m', '--min', type=int, default=30, help='minimum length of overlap')
parser.add_argument('-e', '--entropy', type=int, default=0, help='size of kmers to show entropy for alignment')
parser.add_argument('-a', '--allow', action='store_true', help='allow 1 mismatch')
parser.add_argument('-s', '--skip', action='store_true', help='skip output if they are the same file')
parser.add_argument('-r', '--revcomp', action='store_true', help='do revers complement comparison')
args = parser.parse_args()

# SKIP OUTPUT IF FILE1 AND FILE2 ARE THE SAME FILE
if args.skip and args.file1 == args.file2:
	exit()

# GO THROUGH FIRST FILE AND FIND ALL POSSIBLE KMERS ON ENDS
lefts = dict()
rights = dict()
length = dict()
head = seq = ''
with open(args.file1) as fp:
	for line in chain(fp, '>'):
		if line.startswith('>'):
			length[head] = len(seq)
			for i in range(0, len(seq) - args.min + 1 ):
				lefts.setdefault(seq[  :len(seq)-i ],[]).append(head)
				rights.setdefault(seq[ i:           ],[]).append(head)
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip().upper()

# GO THROUGH OTHER FILE AND FIND ALL POSSIBLE KMERS ON ENDS
head = seq = ''
seenpairs = dict()
with open(args.file2) as fp:
	for line in chain(fp, '>'):
		if line.startswith('>'):
			seen = dict()
			for i in range(0, len(seq) - args.min + 1):
				for left,right in zip(make_kmers(seq[:len(seq)-i], args), make_kmers(seq[i:], args)):
					#bits = encode(seq[:len(seq)-i])
					if left in rights or right in lefts:
						for kmer,end in chain(zip(repeat(left), rights.get(left,[])), zip(repeat(right), lefts.get(right,[]))):
							tup = tuple([end,head])
							if (end not in seen or not any([kmer in item for item in seen[end]])) and (tup not in seenpairs or not any([kmer in item for item in seenpairs[tup]])) and (args.file1 != args.file2 or end != head): 
							#if (end not in seen or kmer not in seen[end]) and (tup not in seenpairs or kmer not in seenpairs[tup]) and (args.file1 != args.file2 or end != head): 
							#if (end not in seen) and (tup not in seenpairs) and (args.file1 != args.file2 or end != head): 
								print(end, head, sep='\t', end='\t')
								print('1', end='\t')
								print(length[end] - len(kmer) + 1, end='\t')
								print(len(kmer), end='\t')
								print(kmer, end='')
								if args.entropy:
									print('\t', end='')
									print(entropy(kmer, args.entropy), end='\t')
								print()
								#seenpairs[ tup[::-1] ] = seenpairs.get( tup[::-1] , '') + kmer # True
								#seen[end] = seen.get(end, '') + kmer #True
								seenpairs.setdefault( tup[::-1], [] ).append( kmer )
								seen.setdefault( end , [] ).append(kmer)
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip().upper()
