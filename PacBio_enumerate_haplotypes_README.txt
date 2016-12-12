Louise Moncla
June 9, 2016

This script is one that I wrote for the purpose of enumerating the number and percentage of haplotypes present in PacBio data. This README file is intended to explain exactly what this script does, what the input data should be, and how to interpret the output files. 

Input file:
The input file for this script is a fasta file of aligned PacBio reads (which can be attained by running PacBio_mapping.sh). 

Output files:
This script will output 2 files in text file format. 

1. The first is the output file which contains 3 columns:
COLUMN 1: the number of times that particular haplotype was detected

COLUMN 2: that haplotype's frequency in the population. This frequency is calculated based only on those haplotypes that are present at a frequency higher than the defined threshold. So if you define your frequency threshold as 1%, this program will only count those haplotypes that are present at a frequency > 1%, and use their frequency within that pool as the reported frequency. 

COLUMN 3: the actual sequence of the haplotype

Below these 3 columns is a block of text that shows each polymorphic site and the identities of each nucleotide at those polymorphic sites. The layout is as follows:

site: X, the polymorhpic site in the alignment
identities: A, T, C, G, etc... This means that haplotype 1 had an A at site X, haplotype 2 had a T at site X, haplotype 3 had a C at site X, etc...


2. The 2nd output file is the output_stats.txt file. This file contains a little bit of summary information about the haplotypes and reads used for the analysis. It will report the following information. 

sample name: this is just the name of the input file used 

total number of input sequences: this is the total number of aligned sequences used for the analysis

total number of haplotypes detected: the number of unique sequences, or haplotypes detected in the original alignment

total number of haplotypes detected above threshold of X (Y): X is the threshold you have defined, and Y is that number converted to the number of sequences. So in an alignment of 1000 reads and a threshold of 1%, haplotypes would be required to be present in at least 10 sequences to be counted. X would = 1 and Y would = 10. The number after the : is the number of haplotypes that were present above your threshold. 

number of sequences considered for haplotypes above threshold: this is the actual number of sequences that are used to calculate the frequency of each haplotype

How this script works: