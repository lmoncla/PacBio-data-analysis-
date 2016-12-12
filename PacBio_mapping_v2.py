#!/usr/bin/env python

import sys, subprocess, glob, os, shutil
from subprocess import call


commands_list = []

for i in range(1, len(sys.argv)):
	command = sys.argv[i].lower()
	commands_list.append(command)
	
if "-h" in commands_list:
	with open("PacBio_mapping_README.txt", "r") as infile:
		print infile.read()

try: 
	reference_sequence = sys.argv[1]
except IndexError:
	print "you must specify a reference sequence in fasta format. For help running this program and usage instructions, type 'PacBio_mapping_v2.py -h'"
	
sample_list = []

for file in glob.glob("*.fastq"):		# glob will find instances of all files ending in .fastq as shell would
	sample_list.append(file)


def perform_bbmap_mapping(sample_list):
	
	for sample in sample_list:
		call("mkdir {sample}.analyses".format(sample=sample), shell=True)
		call("mapPacBio.sh in={sample} out={sample}.analyses/{sample}.sam ref={reference_sequence} nodisk covstats={sample}.analyses/{sample}.covstats.txt qhist={sample}.analyses/{sample}.qualityhist.txt aqhist={sample}.analyses/{sample}.avqualhist.txt lhist={sample}.analyses/{sample}.lengthhist.txt qin=33 maq=30 maxindel=5 strictmaxindel=t minlen=1700 maxlen=1800 minid=0.8".format(sample=sample, reference_sequence=reference_sequence), shell=True)
		call("mkdir {sample}.analyses/mapping_quality_metrics".format(sample=sample), shell=True)
		call("mv {sample}.analyses/*.txt {sample}.analyses/mapping_quality_metrics".format(sample=sample), shell=True)
	

def convert_sam_to_fasta(sample_list):		
	for sample in sample_list:	
		call("mkdir {sample}.analyses/file_conversions".format(sample=sample), shell=True)
		call("cd {sample}.analyses/file_conversions".format(sample=sample), shell=True)
		
		# convert the output sam file to a bam file using samtools
		call("samtools view -bS {sample}.analyses/{sample}.sam > {sample}.analyses/file_conversions/{sample}.bam".format(sample=sample), shell=True)
	
		# split the sam file into forward, reverse, and unmapped reads as separate sam files
		call("splitsam.sh {sample}.analyses/{sample}.sam {sample}.analyses/file_conversions/{sample}.forward.sam {sample}.analyses/file_conversions/{sample}.reverse.sam {sample}.analyses/file_conversions/{sample}.unmapped.sam".format(sample=sample), shell=True)
	
		# extract fastq files out of the sam files
		call("reformat.sh in={sample}.analyses/file_conversions/{sample}.forward.sam out={sample}.analyses/file_conversions/{sample}.forward.fastq qin=33".format(sample=sample), shell=True)	
		call("reformat.sh in={sample}.analyses/file_conversions/{sample}.reverse.sam out={sample}.analyses/file_conversions/{sample}.reverse.fastq qin=33".format(sample=sample), shell=True)
	
		# take the reverse complement of the reverse reads
		call("reformat.sh qin=33 in1={sample}.analyses/file_conversions/{sample}.reverse.fastq out1={sample}.analyses/file_conversions/{sample}.reverse_complement.fastq rcomp=t".format(sample=sample), shell=True)
	
		# combine the fastq files together
		call("cat {sample}.analyses/file_conversions/{sample}.reverse_complement.fastq {sample}.analyses/file_conversions/{sample}.forward.fastq >> {sample}.analyses/file_conversions/{sample}.merged.fastq".format(sample=sample), shell=True)
	
		# make a copy of the fastq file and rename it as a fasta file
		call("cp {sample}.analyses/file_conversions/{sample}.merged.fastq {sample}.analyses/{sample}.fasta".format(sample=sample), shell=True)
	
		# find and replace strings to convert the merged fastq file to a fasta file
		# sed usage is sed -i 's/original/new/g' - g stands for global, meaning replace all matches in the file; /d means to delete the line with a match
		call("sed -i '' $'s/\@/\>/g' {sample}.analyses/{sample}.fasta".format(sample=sample), shell=True)		# replace @ with <
		call("sed -i '' $'/\+/d' {sample}.analyses/{sample}.fasta".format(sample=sample), shell=True)			# remove lines with a +
		call("sed -i '' $'/JJ/d' {sample}.analyses/{sample}.fasta".format(sample=sample), shell=True)			# remove lines with JJ


def perform_alignment(sample_list):
	for sample in sample_list:
		
		# this sends the fasta file to maaft, which will then perform an alignment 
		if "-mafft" in commands_list:
			#call("mkdir {sample}.analyses/mafft/".format(sample=sample), shell=True)	
			call("/usr/local/bin/mafft --auto --inputorder {sample}.analyses/{sample}.fasta > {sample}.analyses/{sample}.mafft.aligned.fasta".format(sample=sample), shell=True)
	
		# alternatively, you can use translator X to align, which I think is better because it keeps everything in the right reading frame. Make a new directory for it and outwrite all files to that directory
		if "-tx" in commands_list:
			call("mkdir {sample}.analyses/translator_x/".format(sample=sample), shell=True)	
			call("translatorx_vLocal.pl -i {sample}.analyses/{sample}.fasta -o {sample}.analyses/translator_x/{sample}.aligned.out -p F -t T -w 1 -c 1".format(sample=sample), shell=True)	
	
		# the options I'm choosing are as follows (can also access by calling program without putting in the correct options):
		# - p = program, F = MAFFT
		# -t = guess reading frame, T = true
		# -w = use web server...not sure what this menas
		# -c = genetic code, 1 = standard
	
		# Make a copy of the aligned fasta file and take out the extra returns. This makes the output the correct format for input into the enumerate haplotypes script. 
		call("cp {sample}.analyses/translator_x/{sample}.aligned.out.nt_ali.fasta {sample}.analyses/{sample}.aligned.for_haplotypes.txt".format(sample=sample), shell=True)	
		call("sed -i '' $'/\>/d' {sample}.analyses/{sample}.aligned.for_haplotypes.txt".format(sample=sample), shell=True)		# remove lines with a >



# combine all of the quality metrics files together and format them to be easily read into R
def quality_metrics():
	call("grep -r --include='*.avqualhist.txt' . * >> average_quality_histogram.txt".format(), shell=True)
	call("grep -r --include='*.covstats.txt' . * >> coverage_stats.txt".format(), shell=True)
	call("grep -r --include='*.qualityhist.txt' . * >> quality_histogram.txt".format(), shell=True)	
	call("grep -r --include='*.lengthhist.txt' . * >> length_histogram.txt".format(), shell=True)
	
	quality_files_list = ["average_quality_histogram.txt","coverage_stats.txt","quality_histogram.txt","length_histogram.txt"]
	
	for file in quality_files_list:
		call("sed -i '' $'/\#/d' {file}".format(file=file), shell=True)
		call("sed -i '' $'s/\:/\t/g' {file}".format(file=file), shell=True)
		call("sed -i '' $'s/\.fastq.*\.txt//g' {file}".format(file=file), shell=True)


def call_SNPs(sample_list):
	
	if "-varscan" in commands_list:
		for sample in sample_list:
			call("mkdir {sample}.analyses/file_conversions".format(sample=sample), shell=True)
			call("cd {sample}.analyses/file_conversions".format(sample=sample), shell=True)	
			call("samtools view -bS {sample}.analyses/{sample}.sam > {sample}.analyses/file_conversions/{sample}.bam".format(sample=sample), shell=True)
			call("samtools sort {sample}.analyses/file_conversions/{sample}.bam > {sample}.analyses/file_conversions/{sample}.sorted.bam".format(sample=sample), shell=True)
			call("samtools mpileup -d 1000000 {sample}.analyses/file_conversions/{sample}.sorted.bam > {sample}.analyses/file_conversions/{sample}.pileup -f {reference_sequence}".format(sample=sample, reference_sequence=reference_sequence), shell=True)
			call("java -jar VarScan.v2.3.9.jar pileup2snp {sample}.analyses/file_conversions/{sample}.pileup --min-coverage 100 --min-avg-qual 30 --min-var-freq 0.01 --strand-filter 0 --output-vcf 1 > {sample}.analyses/{sample}.snps.txt".format(sample=sample), shell=True)
		
		call("grep -r --include='*.snps.txt' . * >> snps.txt".format(), shell=True)
		call("sed -i '' $'/Position/d' snps.txt".format(), shell=True)
		call("sed -i '' $'s/\:/\t/g' snps.txt".format(), shell=True)
		call("sed -i '' $'s/\.fastq.*\.txt//g' snps.txt".format(), shell=True)
	
	if "-lofreq" in commands_list:
		for sample in sample_list:
			call("mkdir {sample}.analyses/file_conversions".format(sample=sample), shell=True)
			call("cd {sample}.analyses/file_conversions".format(sample=sample), shell=True)	
			call("samtools view -bS {sample}.analyses/{sample}.sam > {sample}.analyses/file_conversions/{sample}.bam".format(sample=sample), shell=True)
			call("samtools sort {sample}.analyses/file_conversions/{sample}.bam > {sample}.analyses/file_conversions/{sample}.sorted.bam".format(sample=sample), shell=True)
			call("lofreq call --no-default-filter -f {reference_sequence} -o {sample}.analyses/{sample}.lofreq.vcf {sample}.analyses/file_conversions/{sample}.sorted.bam".format(sample=sample, reference_sequence = reference_sequence), shell=True)
			call("lofreq filter --no-defaults --cov-min 100 --snvqual-thresh 30 --af-min 0.01 -i {sample}.analyses/{sample}.lofreq.vcf -o {sample}.analyses/{sample}.lofreq.filtered.vcf".format(sample=sample), shell=True)
		
		call("grep -r --include='*.lofreq.filtered.vcf' . * >> lofreq.snps.txt".format(), shell=True)
		call("sed -i '' $'/#/d' lofreq.snps.txt".format(), shell=True)
		call("sed -i '' $'s/\;/\t/g' lofreq.snps.txt".format(), shell=True)
		call("sed -i '' $'s/\:/\t/g' lofreq.snps.txt".format(), shell=True)
		call("sed -i '' $'s/\t*\=/\t/g' lofreq.snps.txt".format(), shell=True)
		call("sed -i '' $'s/\.fastq.*\.vcf//g' lofreq.snps.txt".format(), shell=True)
# run it

if "-m" in commands_list:
	perform_bbmap_mapping(sample_list)
	quality_metrics()

if "-a" in commands_list:
	convert_sam_to_fasta(sample_list)
	perform_alignment(sample_list)
	
if "-s" in commands_list:
	call_SNPs(sample_list)
	
if "-q" in commands_list:
	quality_metrics()
	



## current usage notes: ###
## PacBio_mapping_v2.py <reference sequence> <arguments>
## arguments list:
## -m = perform mapping to a reference sequence
## -a = perform alignment
## -s = call SNPs
## -tx = choose translator x as your preferred aligner ; must choose either tx or m if choose to do alignment
## -mafft = choose to use mafft as your preferred aligner

