##########################################################################################
WELCOME TO THE FRIEDRICH LAB PACBIO PIPELINE
##########################################################################################

This script is a wrapper for a series of programs that will perform basic quality control and mapping on PacBio sequence data. This should be used for circular consensus sequences generated on a PacBio instrument. 

REQUIREMENTS:

This pipeline calls upon several freely available software packages. These should all be downloaded and installed on the TCF Coltrane server. However, if they are not, then you will need to download them and place them in the usr/bin directory so that everyone who accesses the server may access them. Alternatively, you may download them and put them anywhere on your individual partition of the server and then add them to your path. 

BBMap
Samtools
MAFFT
Translator X
Varscane

BASIC USAGE: PacBio_mapping_v2.py <reference sequence> <arguments>

<reference sequence> is mandatory
<arguments> are all optional; however if you do not specify any of them, then the script will not do anything. 

arguments list:
-m = perform mapping to a reference sequence

This will perform reference-based mapping using bbmap's mapPacBio.sh script. I have hard coded in that for a read to map it must have an average quality score of at least Q30, and the mapping will only allow indels that are at most 5 base pairs long. I have found that this results in nice assemblies. I have also specified to output quality metrics that describe the reads. By default, this script will concatenate all of the quality metrics for each sample into 1 file that can be easily read into and plotted with R. 

-a = perform alignment

This specifies all of the necessary file format manipulations that are required to tranform the mapped assembly file (sam file) into a fasta alignment file in which all reads are aligned to each other. If you choose the -a option, you must specify whether you want to use translator x or mafft to do your alignments. It will then format the output fasta file to the correct format for input into the detect haplotypes script. 

-tx = choose translator x as your preferred aligner 

-mafft = choose to use mafft as your preferred aligner

-s = call SNPs

This will specify that you would like to output SNP calls. This will use Varscan. 

-q = this will concatenate all of the quality scores together into 1 file. This will automatically be done if -m is specified.  

-h = print this document


To RUN: 
Once all of the dependent programs are installed, simply navigate into the directory containing your fastq files. Run the script with whichever arguments you choose in that directory. 

EXAMPLE: PacBio_mapping_v2.py CA04.fa -m -a -tx -s 
This will loop through all the fastq files in the current directory and perform mapping, alignment with translator X, and call SNPs. 