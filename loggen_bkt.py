'''
Loggen_bkt is a simulated student log generator that can simulate student data
according to pre-specified BKT parameters. n_otp is the transaction length
that you would like to generate - the number of opportunities to practice
a skill that a random student has.

Loggen supports, or will support, a number of extra parameters.

PROF:
For the simulation of students who are more or less proficient, for the
purposes of fitting a model to a heterogeneous student pool, use the prof
input. Prof is a direct modification of the code's calculated p_corr value.
A positive prof value increases the likelihood that a given student will be
correct, a negative prof value decreases that likelihood. Prof should be
between -1 (no student will ever be correct) and 1 (every student will always
be correct).

DATATYPE (pending):
Loggen can be configured to output simulated correctness and incorrectness
(default) or calculated p(ln) values, or both.
'''

def loggen_bkt(n_otp,lzero,g,s,t,prof=0,datatype=None):
    import random
    
    def ln_update(ln,correct):
        mns = ln*(1-s)
        ms = ln*s 
        nmg = (1-ln)*g
        nc = 1-correct
        nmng = (1-ln)*(1-g)
        
        ca = float(mns)/float((mns+nmg))
        ica = float(ms)/float((ms+nmng))
        new = ((correct*ca) + (nc*ica))
        
        return new + ((1-new)*t)
            
    r = []
    ln = lzero
    for x in xrange(0,n_otp+1):
        p_corr = (ln * (1-s)) + ((1-ln)*g)
        c = random.randint(0,1000)/float(1000)
        if p_corr+prof > c:
            ln = ln_update(ln,1)
            r.append(ln)
        else:
            ln = ln_update(ln,0)
            r.append(ln)
    return r


'''
Created on Jan 28, 2017

@author: Stefan
'''
