#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser()
#parser.add_argument("ref_sequence", help="please provide a reference sequence")
#args = parser.parse_args()
#print args.ref_sequence

parser.add_argument("square", help="display a square of a given number", type=int)
args=parser.parse_args()

if args.square:
	print args.square**2
	
else:
	print "ok"