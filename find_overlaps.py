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

def print_match(end, head, kmer, side, d, args):
	args.outfile.print(end)
	args.outfile.print('\t')
	args.outfile.print(head)
	args.outfile.print('\t')
	args.outfile.print(side)
	args.outfile.print('\t')
	args.outfile.print(d)
	args.outfile.print('\t')
	args.outfile.print(length[end] - len(kmer) + 1)
	args.outfile.print('\t')
	args.outfile.print(len(kmer))
	args.outfile.print('\t')
	args.outfile.print(kmer)
	if args.entropy:
		args.outfile.print('\t')
		args.outfile.print(entropy(kmer, args.entropy))
	args.outfile.print('\n')

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


trans = str.maketrans('ACTG', 'TGAC')
def make_kmers(seq, args):
	seqs = [ (seq,'+1'), (seq.translate(trans)[::-1],'-1') ] if args.revcomp else [(seq,'+1')]
	for s,d in seqs:
		for i in range(0, len(s) - args.len + 1):
			s1 = s[:len(s)-i]
			s2 = s[i:]
			if args.mismatch:
				for j, c in enumerate(s1):
					for other in 'ACTG':
						yield s1[0:j]  + other + s1[j+1:] , s2[0:j]  + other + s2[j+1:] , d
			else:
				yield s1,s2,d


usage = '%s [-opt1, [-opt2, ...]] file1 file2' % __file__
parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter, usage=usage)
parser.add_argument('file1', type=is_valid_file, help='input file')
parser.add_argument('file2', type=is_valid_file, help='input file')
parser.add_argument('-o', '--outfile', action="store", default=sys.stdout, type=argparse.FileType('w'), help='where to write output [stdout]')
parser.add_argument('-l', '--len', type=int, default=30, help='minimum length of overlap')
parser.add_argument('-e', '--entropy', type=int, default=0, help='size of kmers to show entropy for alignment')
parser.add_argument('-m', '--mismatch', action='store_true', help='allow 1 mismatch')
parser.add_argument('-a', '--all', action='store_true', help='Include all matches at both ends')
parser.add_argument('-s', '--skip', action='store_true', help='skip output if they are the same file')
parser.add_argument('-r', '--revcomp', action='store_true', help='do reverse complement comparison')
args = parser.parse_args()
def _print(self, item):
	if isinstance(item, str):
		self.write(item)
	else:
		self.write(str(item))
args.outfile.print = _print.__get__(args.outfile)



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
			for i in range(0, len(seq) - args.len + 1 ):
				lefts.setdefault(  seq[   : len(seq)-i ],[]).append(head)
				rights.setdefault( seq[ i :            ],[]).append(head)
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
			for left,right,d in make_kmers(seq, args):
				if left in rights or right in lefts:
					for kmer,end,side in chain(zip(repeat(left), rights.get(left,[]), repeat('R')), zip(repeat(right), lefts.get(right,[]), repeat('L'))):
						tup = tuple([end,head])
						if ( 
							( end not in seen      or (args.all and not any([kmer in kmers for kmers in seen[end]]))      ) and
							( tup not in seenpairs or (args.all and not any([kmer in kmers for kmers in seenpairs[tup]])) ) and
							( args.file1 != args.file2 or end != head)
							): 
								print_match(end, head, kmer, side, d, args)
								seenpairs.setdefault( tup[::-1], [] ).append( kmer )
								seen.setdefault( end , [] ).append(kmer)
			head = line[1:].rstrip().split(' ')[0]
			seq = ''
		else:
			seq += line.rstrip().upper()








