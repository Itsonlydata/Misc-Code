'''
This program finds empty folders in a specified directory and deletes them.

This program will not delete empty nested folders.

This program does not exhaustively search directory trees.

It has been very lightly tested.

Use at your own risk.

'''

import os

loc = "C:/Users/Stefan/Desktop/EFDTEst"
folders = os.listdir(loc)

for f in folders:
    loc_mod = loc+"/"+f
    if os.path.isdir(loc_mod) and os.listdir(loc_mod) == []:
        os.rmdir(loc_mod)

'''
*** MIT LICENSE INFORMATION ***
Copyright 2017 Stefan Slater

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
***
'''
