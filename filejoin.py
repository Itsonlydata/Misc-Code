import os
import csv

path = “C:\. . .” ## Update with the folder path on your system
fnames = [“file1.csv",
          “file2.csv",
          “file3.csv",
          “file4.csv"] # Update with file names to join

joinname = “allfiles.csv" # The name of the joined file

delim = “,” # The delimiter to use (could also be “\t” for tab-delimited files)

os.chdir(path)

header = None
join = []
for name in fnames:
    with open(name,'rU') as f:
        reader = csv.reader(f,delimiter=delim)
        if not header:
            header = reader.next()
        else:
            reader.next()
            
        for row in reader:
            join.append(row)

writer = csv.writer(open(joinname,'wb'))
writer.writerow(header)
writer.writerows(join)

'''
Created on Dec 22, 2016

@author: Stefan
'''
