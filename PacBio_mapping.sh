#! /bin/bash

# this script will take demultiplexed fastq files and filter and map them to a specified reference sequence using BBMap. It will then take that output sam file, extract fastqs, reverse complement the reverse reads, merge them and convert them to fasta format. It will then pass these merged fasta files to either MAAFT or Translator X (simply hash out whichever one you don't want to use), which will align them and output the aligned fasta file which is ready to use. I would recommend Translator X, as it will not disrupt the reading frame in the alignment. To run, simply define the sample list you want to run the script on, and change the directory of where your demultiplexed fastq files are located and the rest is ready to go. This script requires that BBMap and samtools are added to your path and that MAAFT and Translator X are installed (when you install both, they should automatically be installed in the user/bin, but if not, then you must move them there for this script to access them).  

# Here I am defining an array, which is basically a list of values. The syntax is ARRAY_NAME[index]="value"; so here, I am defining an array called "SAMPLE" (All arrays must be in uppercase), containing entries 0-n, where each index is named a string defined in the quotes

#sample list
SAMPLE[0]="CA04_test"
SAMPLE[1]="1918_test"

cd /Users/user/Documents/PacBio_sequencing/data/BBMap/CA04_PacBio_mapping_script;

# Start a for loop. For each variable in the array SAMPLE, do the following commands. Do this for all of the variables. This series of commands will call upon other programs (BBMap, Translator X, Samtools, MAFFT) to perform the tasks

for var in ${SAMPLE[*]}
do 
	# create a new folder with the name of the variable
	mkdir $var
	
	# do the mapping with BBMap; require minimum quality of Q30, don't allow indels > 5 bases, exclude sequences < 1700 bp and > 1800 bp; read must be 80% identical to reference to map it - this will help exclude extraneous carry-over reads if they are present in PacBio reads as they sometimes are in Illumina runs
	mapPacBio.sh in=$var.fastq out=$var/$var.sam ref=/Users/user/Documents/PacBio_sequencing/data/reference_sequences/HA_1918_like_avian.fa nodisk covstats=$var/$var.covstats.txt maq=30 maxindel=5 strictmaxindel=t minlen=1700 maxlen=1800 minid=0.8
	
	# convert the output sam file to a bam file using samtools
	samtools view -bS $var.sam > $var.bam
	
	# split the sam file into forward, reverse, and unmapped reads as separate sam files
	splitsam.sh $var/$var.sam $var/fastq_extraction/$var.forward.sam $var/fastq_extraction/$var.reverse.sam $var/fastq_extraction/$var.unmapped.sam
	
	# extract fastq files out of the sam files
	reformat.sh in=$var/fastq_extraction/$var.forward.sam 		out=$var/fastq_extraction/$var.forward.fastq
	
	reformat.sh in=$var/fastq_extraction/$var.reverse.sam out=$var/fastq_extraction/$var.reverse.fastq
	
	# take the reverse complement of the reverse reads
	reformat.sh in1=$var/fastq_extraction/$var.reverse.fastq out1=$var/fastq_extraction/$var.reverse_complement.fastq rcomp=t
	
	# combine the fastq files together
	cat $var/fastq_extraction/$var.reverse_complement.fastq $var/fastq_extraction/$var.forward.fastq >> $var/$var.merged.fastq
	
	# make a copy of the fastq file and rename it as a fasta file
	cp $var/$var.merged.fastq $var/$var.merged.fasta
	
	# find and replace strings to convert the merged fastq file to a fasta file
	# sed usage is sed -i 's/original/new/g' - g stands for global, meaning replace all matches in the file; /d means to delete the line with a match
	sed -i '' $'s/\@/\>/g' $var/$var.merged.fasta		# replace @ with <
	sed -i '' $'/\+/d' $var/$var.merged.fasta			# remove lines with a +
	sed -i '' $'/JJ/d' $var/$var.merged.fasta			# remove lines with JJ
	
	# this sends the fasta file to maaft, which will then perform an alignment 
	# "/usr/local/bin/mafft" --auto --inputorder /Users/user/Documents/PacBio_sequencing/data/BBMap/CA04_PacBio_mapping_script/$var/"$var.merged.fasta" > /Users/user/Documents/PacBio_sequencing/data/BBMap/CA04_PacBio_mapping_script/$var/"$var.aligned.fasta"
	
	# alternatively, you can use translator X to align, which I think is better because it keeps everything in the right reading frame. Make a new directory for it and outwrite all files to that directory
	
	mkdir $var/translator_x/
	translatorx_vLocal.pl -i $var/$var.merged.fasta -o $var/translator_x/$var.aligned.out -p F -t T -w 1 -c 1
	
	# the options I'm choosing are as follows (can also access by calling program without putting in the correct options):
	# - p = program, F = MAFFT
	# -t = guess reading frame, T = true
	# -w = use web server...not sure what this menas
	# -c = genetic code, 1 = standard
	
	# Make a copy of the aligned fasta file and take out the extra returns. This makes the output the correct format for input into the enumerate haplotypes script. 
	cp $var/translator_x/$var.aligned.out.nt_ali.fasta $var/$var.aligned.for_haplotypes.txt
	sed -i '' $'/\>/d' $var/$var.aligned.for_haplotypes.txt	# remove lines with a >
	
done

