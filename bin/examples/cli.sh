~/bp/basepair/bin/basepair --config config.json --action create-sample --name "Sample 5" --datatype chip-seq --genome mm9 --file1 sample_1.fastq.gz --file2 sample_2.fastq.gz

~/bp/basepair/bin/basepair --config config.json --action create-sample --name "Sample 9" --datatype chip-seq --genome mm9 --file1 sample_1.fastq.gz

~/bp/basepair/bin/basepair --config config.json --action create-analysis -w 10 -s 1855

~/bp/basepair/bin/basepair --config config.json --action create-analysis -w 8 -s 9 -c 10

~/bp/basepair/bin/basepair --config config.json --action update-sample -s 1855 --key genome --val mm10

~/bp/basepair/bin/basepair --config config.json --action update-analysis -a 2006 --key name --val "Analysis w/ p 0.05"

~/bp/basepair/bin/basepair --config config.json --action download -s 14 --tags bam --tags dedup

~/bp/basepair/bin/basepair --config config.json --action delete-analysis -a 2006

~/bp/basepair/bin/basepair --config config.json --action delete-sample -s 1855
