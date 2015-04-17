#This code processes maf files, runs bedtools functions, and graphs using matplotlib
from numpy import *
import argparse 
import csv 
import pybedtools
import os
import brewer2mpl
import pandas as pd
from ggplot import *

#arguments
parser = argparse.ArgumentParser()
parser.add_argument('file1',help='input maf/bed file')
parser.add_argument('file2',help='input maf/bed file')
parser.add_argument('-i','--intersect',help='intersect two files', action='store_true')
parser.add_argument('-s','--subtract',help='subtract two files from each other', action='store_true')
args = parser.parse_args()

#functions
def maf_edit(file): 
	os.system(''' awk '(NR > 2) {print "chr" $5, $6 -1, $7, $0;}' OFS="\t" ''' + file + ">temp.maf")
	csvfile = open("temp.maf",'r') 
	reader = csv.reader(csvfile, dialect = 'excel-tab')
	makebed = open("'"+file+".bed'", 'w')
	writer = csv.writer(makebed, delimiter='\t')
	for row in reader:
		if 'chrGL' not in row[0]:
			writer.writerow(row)
	bed = open("'"+file+".bed'", 'r')
	return bed

def bedtool_int(file1,file2):
	a = pybedtools.BedTool(file1)
	ints = a.intersect(file2).saveas(args.file1[:-4]+"_"+args.file2[:-4]+"_intersect.bed")
	return ints

def bedtool_sub(file1,file2):
	a = pybedtools.BedTool(file1)
	uniqs= a.subtract(file2).saveas(args.file1[:-4]+"_"+args.file2[:-4]+"_subtract.bed")
	return uniqs
	
def merge(file1):
	output = os.system('cat' + file1 + '''| awk '{print $1, $4} | sort | uniq -c | sed -e 's/^ *//;s/ / /' ''')
	return output

def check(file1):
	suffix = '.maf'
	suffix1 = '.bed'
	if file1.endswith(suffix):
		return maf_edit(file1)
	elif file1.endswith(suffix1):
		return file1
	else:
		return False 

def graph(file1):
	data = pd.read_csv(file1, header = None, sep = ' ')
	data2 = []
	for i in data:
		data2.append({'COUNT':data[0][i], 'NAME':data[2][i]})
	df = Dataframe(data2)
	return ggplot(df,aes(x='NAME',weight='COUNT')) + geom_bar()

#check files
File1 = check(args.file1)
if check(args.file1) == False:
	print 'Argument 1 is not .maf or .bed format'
File2 = check(args.file2)
if check(args.file2) == False:
	print 'Argument 2 is not .maf or .bed format'

#using bedtools	
if File1 and File2 != False:
	if args.intersect: 
		print graph(merge(bedtool_int(File1,File2)))
	if args.subtract:
		unique_1 = merge(bedtool_sub(File1,File2))
		unique_2 = merge(bedtool_sub(File2,File1))
		print graph(unique_1)
		print graph(unique_2)
