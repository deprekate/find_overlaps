#!/usr/bin/perl -w
use strict;
use POSIX;

# split a fasta file into a specified number of sub files and run a program on them

# version 2014.11.24



my $usage=<<EOF;

$0 <options>

-1 file to split
-2 file to run against
-n number to break into
-d destination directory (default = ".")

-p program name ()

-N job name (default is splitjob) 

-rev reverse the order of files that are submitted to the BLAST queue. (i.e. so you can run twice and start from the end backwards!)

Other things will be used as blast options. Unless -p && -db, will split and stop

EOF

my ($file, $other, $dest, $no, $program, $jobname, $rev);


while (@ARGV) {
	my $test=shift(@ARGV);
	if ($test eq "-1") {$file=shift @ARGV}
	elsif ($test eq "-2") {$other=shift @ARGV}
	elsif ($test eq "-d") {$dest=shift @ARGV}
	elsif($test eq "-n") {$no=shift @ARGV}
	elsif($test eq "-p") {$program=shift @ARGV}
	elsif($test eq "-N") {$jobname=shift @ARGV}
	elsif($test eq "-rev") {$rev=1}
}

die $usage unless ($file && $other && $no);

$jobname="splitjob" unless ($jobname);
if ($dest) {unless (-e $dest) {mkdir $dest, 0755}}
else {$dest="."}
$dest =~ s/\/$//;

# read the file and see how many > we have
if ($file =~ /gz$/) {open(IN, "gunzip -c $file |") || die "Can't open a pipe to $file"}
else {open(IN, $file)|| die "Can't open $file"}

my $counttags;
while (<IN>) {$counttags++ if (/^>/)}
close IN;
my $required=ceil($counttags/$no); # ceil rounds up so we should get less files than if we use int or real rounding.
#print STDERR "There are $counttags sequences in $file and we are going to write $required per file\n";


my $filecount=1;
my @sourcefiles;
if ($file =~ /gz$/) {open(IN, "gunzip -c $file |") || die "Can't open a pipe to $file"}
else {open(IN, $file)|| die "Can't open $file"}
$file =~ s/^.*\///;
open (OUT, ">$dest/$file.$filecount") || die "Can't open $dest/$file.$filecount";
push @sourcefiles, "$file.$filecount";

my $sofar;
while (my $line=<IN>) {
	if ($line =~ /^>/) {$sofar++}
	if (($line =~ /^>/) && !($sofar % $required) && (($counttags - $sofar) > 20)) {
		# the last conditional is to make sure that we don't have a few sequences in a file at the end
		close OUT;
		$filecount++;
		open (OUT, ">$dest/$file.$filecount") || die "Can't open $dest/$file.$filecount";
		push @sourcefiles, "$file.$filecount";
	}
	print OUT $line;
}

@sourcefiles=reverse @sourcefiles if ($rev);


my $name="splt$file";
$name=substr($name, 0, 10);

my $pwd=`pwd`; chomp($pwd);


my $submitted=0;
foreach my $sf (@sourcefiles) {
	$submitted++;
	my $command = "awk -f script.sh $pwd/$dest/$sf $other";
	
	open(OUT, ">$dest/$name.$submitted.sh") || die "Can't open $dest/$name.$submitted.sh";
	print OUT "#!/bin/bash\n$command\n";
	close OUT;
	system("chmod a+x $dest/$name.$submitted.sh");
}
my $sgetaskidfile="$name.submitall";
my $c=0;
while (-e "$sgetaskidfile.$c.sh") {$c++}

open(STI, ">$sgetaskidfile.$c.sh") || die "can't write to $sgetaskidfile.$c.sh";
print STI "#!/bin/bash\n$dest/$name.\$SGE_TASK_ID.sh\n";
close STI;
`chmod +x $sgetaskidfile.$c.sh`;
mkdir "sge_output", 0755 unless (-e "sge_output");
my $output = join("", `qsub -q default -S /bin/bash -cwd -e sge_output -o sge_output -t 1-$submitted:1 ./$sgetaskidfile.$c.sh`);
# output will be something like this:
# Your job-array 275368.1-92:1 ("bl6666666..submitall.0.sh") has been submitted
my $jobid="";
if ($output =~ /Your job-array (\d+)/) {
	$jobid=$1;
}

print STDERR $output, $submitted, " jobs submitted as array task\nJob ID: $jobid\n";


