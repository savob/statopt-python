'''
This file is used to load in test data for the development of the program.
Originally to test the output portion of the code (plots/print statements)
before Savo worked to tune the simulation itself so one could trust that 
the output statements and figures reflect the data provided accurately.

It was then used to read in some of the .mat files used to store values for
different system parameters such as distortion since those are easier to prepare 
by hand as desired in either MATLAB or Octave.

Note: the object will have a dict of the objects/variables stored in the MAT file.
The function will usually return these as read in, but if the file name matches
one in this, then it'll return that object directly.
'''

from scipy.io import loadmat

def objectFromMat(filename):
    # Return an object from a .MAT file
    temp = loadmat(filename, appendmat=True, simplify_cells=True)
    temp = dictToObject(temp)

    # Return nested object if the filename matches
    if filename in temp.__dict__:
        temp = temp.__dict__[filename]

    return temp

# Declaring an empty class
class C:
    pass

def dictToObject(d):
     
    # checking whether object d is a
    # instance of class list
    if isinstance(d, list):
        d = [dictToObject(x) for x in d]
 
    # if d is not a instance of dict then
    # directly object is returned
    if not isinstance(d, dict):
        return d
    
    # constructor of the class passed to obj
    obj = C()
  
    for k in d:
        obj.__dict__[k] = dictToObject(d[k])
  
    return obj
 
