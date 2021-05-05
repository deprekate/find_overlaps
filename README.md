# find_overlaps

Run on included sample data:
```sh
python3 find_overlaps.py file1.fna file2.fna > outfile
```

To break up `file1` into 500 pieces and run each piece against `file2` with the awk 
script on the sge cluster, run the below command on the head node.
```
$ ./split_and_run.pl -1 file1.fna -2 file2.fna -n 500
```
