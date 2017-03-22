'''
This code accepts a .csv file as input and returns a number of .csv files
based on user-defined parameters. Useful for taking files that are too large
for use in traditional graphical spreadsheet programs such as Excel and 
making them manageable. To recombine files, try using csvjoin, posted at
stefanslater.com/code.
'''

import csv
import os

def writechunk(d,it):
    '''
    Takes the current string of data and the current file iteration point, and
    writes it out as a .csv.
    '''
    fname_nocsv = fname.split(".")[0] # removing the .csv extension
    writer = csv.writer(open(fname_nocsv+"_"+str(it)+".csv",'wb'))
    writer.writerow(header)
    writer.writerows(d)
    return 

fname = " " # name of the file to be split
fdir = " " # the full path of the file to be split
csvlen = 200000 # the length of the resultant file(s), in rows
os.chdir(fdir)

with open(fname,'rU') as f:
    reader = csv.reader(f)
    header = reader.next()
    i = 1
    chunk = []
    
    for n,r in enumerate(reader):
        if n % csvlen == 0 and n != 0:
            writechunk(chunk,i)
            i += 1
            chunk = []
        chunk.append(r)   
    writechunk(chunk,i)



'''
Created on Mar 21, 2017

@author: stefanslater
'''
