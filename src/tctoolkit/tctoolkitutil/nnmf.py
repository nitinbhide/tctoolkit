'''
Non Negative Matrix Factorization : From Programming Collective Intelligence By Toby Segaran.
'''

import math
import itertools
from numpy import *

def difcost(a,b):
    dif = linalg.norm(a-b, 'fro')  
    #dif=0
    #for i in range(shape(a)[0]):
    #  for j in range(shape(a)[1]):
    #    # Euclidean Distance
    #    #dif+=pow(a[i,j]-b[i,j],2)
    #    val = a[i,j]-b[i,j]
    #    dif+=(val*val)
    return dif

def sanitize(mat, matname):
    for idx, val in ndenumerate(mat):
        #use numpy.isnan as python 2.5 doesn't have isnan defined in math module
        if( isnan(val)):            
            mat[idx] = 0
      
def factorize(v,pc=10,iter=50):
    ic=shape(v)[0]
    fc=shape(v)[1]
  
    # Initialize the weight and feature matrices with random values
    w=matrix([[random.random() for j in range(pc)] for i in range(ic)])
    h=matrix([[random.random() for i in range(fc)] for i in range(pc)])
  
    # Perform operation a maximum of iter times
    cost = 0
    for i in range(iter):
        wh=w*h
        # Calculate the current difference
        cost=difcost(v,wh)
        
        if i%10==0: print cost
        
        # Terminate if the matrix has been fully factorized
        if cost==0: break
        
        # Update feature matrix
        hn=(transpose(w)*v)
        hd=(transpose(w)*w*h)
        
        h=matrix(array(h)*array(hn)/array(hd))
        sanitize(h, 'h')
        
        # Update weights matrix
        wn=(v*transpose(h))
        wd=(w*h*transpose(h))
        
        w=matrix(array(w)*array(wn)/array(wd))
        sanitize(w, 'w')
    print "final cost : %f" % cost
    
    return w,h
