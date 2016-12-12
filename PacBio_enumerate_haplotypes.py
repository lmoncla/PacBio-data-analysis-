#!/usr/bin/env python

sequence_dict = {}		# define a new, empty dictionary 
number_of_haplotypes = 0 		# this will count the total number of haplotypes, aka, distinct sequences
lines = 0 		# this will count the number of lines read in, aka, the number of sequences
threshold_haplotypes = 0 		# define a variable called threshold_haplotypes which will count the # of haplotypes present more than 1 time
threshold_reads = 0			# define a variable threshold_reads which will count the total number of sequences in the subset of those that are present >= 1 time
haplotype_list = []

# read in an aligned fasta file and set it to the variable InFileName
InFile1 = "test"
InFileName = InFile1 + ".txt"

OutFileName = InFile1 + "_output.txt"
OutFileName2 = InFile1 + "_output_stats.txt"

# define the percentage the haplotype must be present in the population to consider it real. That value will be converted to a float and used as the haplotype threshold
threshold = raw_input("Enter the haplotype detection threshold you wish to use as percent (enter 1 for 1%): ")
threshold = float(threshold)/100

# open the input file and read it; that read text file is now the variable InFile
NewFile = open("NewFile.txt", 'w')

# this will go through and take out all of the lines containing the > defining the fasta file and output a new file that will be read in
with open(InFileName) as InFile:
	for line in InFile:
		if ">" not in line:
			NewFile.write(line)
NewFile.close()


with open("NewFile.txt") as InFile:
	
	for line in InFile:
		line = str(line)	# convert the line to a string
		line = line.lower()		# make all characters lowercase
		lines = lines + 1		# add 1 to the lines counter
		#print line
		
		if line in sequence_dict.keys():	# if that sequence is already a key in the dictionary
			sequence_dict[line] += 1		# add 1 to the value for that key
			
		else:	# if that sequence is not a key in the dictionary
			haplotype_count = 1		# set haplotype_count = 1
			sequence_dict[line] = haplotype_count	# add a new key:value combo of the line and haplotype count
			number_of_haplotypes = number_of_haplotypes + 1
	
	#print sequence_dict
	#print number_of_haplotypes
	#print lines
	#print max(sequence_dict.values())
	
		
	for key, value in sequence_dict.iteritems(): # iterate through the keys and look at their values
		if value >= threshold * lines:
			threshold_haplotypes = threshold_haplotypes + 1
			threshold_reads = threshold_reads + value
	
	print threshold_haplotypes
	threshold_reads = float(threshold_reads) # convert the variable threshold_reads to a float
	print threshold_reads
	
	with open(OutFileName,"w") as OutFile: # create an empty output file just to clear it in case one already exists
		OutFile.write("")
	
	for key, value in sequence_dict.iteritems():
		if value >= threshold * lines:	
			# output every haplotype present at the threshold value into a text file		
			with open(OutFileName,"a") as OutFile:	# open the output file
				OutFile.write("%s \t" % value)	# append first the key value and then the sequence
				OutFile.write("%s \t" % str(float((value/threshold_reads)*100))) # include here the fraction frequency of that haplotype
				OutFile.write("%s" % key)
			OutFile.close()
			
			# now try to get this to also store the polymorphic sites
			haplotype_string = list(str(key))		# convert the key (haplotype sequence) into a list of strings (a,t,c,g)
			haplotype_list.append(haplotype_string)		# write this list to the "haplotype_list" list
			#print haplotype_list
			#print len(haplotype_string)
			

count = 0
while count < len(haplotype_string):		# loop through all nucleotide sites
	list2 = [item[count] for item in haplotype_list]		# define another list, which will be the index of each list in haplotype_list
	
	def all_same(iterator):		# define a function to test whether all items in the list are the same
		return len(set(iterator)) <= 1
	
	if all_same(list2) == True:		# if the base at the site is the same in all haplotpyes, return true and increase count by 1
		count += 1
		
	else:
		list2 = "\t".join(list2)
		with open(OutFileName,"a") as OutFile:	# open the output file
			OutFile.write("site: %s \n" % str(count + 1))	#report the polymorphic site (add 1 because site 0 is the first site and I want to report it as site 1)
			OutFile.write("identites: \t %s \n" % list2)		#report the nucleotides that are present at those polymorphic sites
		OutFile.close
		count += 1

with open(OutFileName2,"w") as OutFile:
	OutFile.write("")
with open(OutFileName2,"w") as OutFile:
	OutFile.write("sample name: %s \n" % InFile1)
	OutFile.write("total number of input sequences: %s \n" % lines)
	OutFile.write("total number of haplotypes detected: %s \n" % number_of_haplotypes)
	OutFile.write("total number of haplotypes detected above threshold of %s: %s \n" % (str(threshold*lines), threshold_haplotypes))
	OutFile.write("number of sequences considered for haplotypes above threshold: %s" %	threshold_reads)
OutFile.close




# I now need to find a way to remove regions of the alignment that are at least 90% gaps; I also need to filter out haplotypes that only differ based on gaps at the ends of sequences
# option 1: could alter my original if statement to say if they are all the same or the same except for differing by a gap character
# I also could really use a way to convert these nucleotide numbers to better ones, because they are not necessarily right - I suppose I could do this by just including a reference sequence in the alignment step - that way you would always be able to see that
