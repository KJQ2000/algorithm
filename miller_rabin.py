"""
Author: Kuan Jun Qiang
"""
import sys
import random
from numpy import log as ln

# this function wrtie content to secretprimes.txt
def write_file_secretprimes(file_path: str, p:int, q:int):
    '''
    Input: 
        file_path: file path of output file
        p: p value
        q: q value
    '''
    f = open(file_path, 'w')
    f.write("# p" + "\n")
    f.write(str(p) + "\n")
    f.write("# q" + "\n")
    f.write(str(q) + "\n")
    f.close()

# this function wrtie content to publickeyinfo.txt
def write_file_publickeyinfo(file_path: str, p:int, q:int):
    '''
    Input: 
        file_path: file path of output file
        p: p value
        q: q value
    '''
    f = open(file_path, 'w')
    f.write("# modulus (n)" + "\n")
    f.write(str(p*q) + "\n")
    f.write("# exponent (e)" + "\n")
    f.write(str(exponent(p,q)) + "\n")
    f.close()


def repeated_squaring(a,b,n):
    """
    Input:
        a: base
        b: exponent
        n: modulus
    Output:
        result: a^b mod n
    """
    b_bin_rep = ""
    result = -1
    while b !=0:
        b_bin_rep =str(b%2)+b_bin_rep
        b = b//2
    lst = [[] for i in range(len(b_bin_rep))]
    for i in range(len(b_bin_rep)):
        if i!=0:
            previous = lst[i-1]
            lst[i].append((previous[0]*previous[0])%n)
        else:
            lst[i].append(a%n)
    for i in range(len(b_bin_rep)):
        if b_bin_rep[len(lst)-1-i]=="1":
            if result == -1:
                result = lst[i][0]
            else:
                result = (result*lst[i][0])
    return result%n

# using euclidean algorithm
def gcd(x,y):
    """
    Input:
        x: integer
        y: integer
    Output:
        gcd of x and y
    """
    while y!=0:
        x, y = y, x%y
    return abs(x)

def exponent(p,q):
    """
    Input:
        p: prime number
        q: prime number
    Output:
        e: exponent
    """
    lambd = ((p-1)*(q-1))//(gcd(p-1,q-1))
    e = random.randint(3,lambd-1)
    while gcd(e,lambd)!=1:
        e = random.randint(3,lambd-1)
    return e


def miller_rabin(n):
    """
    Input:
        n: integer
    Output:
        True if n is prime
    """

    k = ln(n).astype(int)
    
    if n==1:
        return False
    
    #Special Case
    if n ==2 or n ==3:
        return True
    
    #even number is not prime
    if n %2 == 0:
        return False
    
    #factor  n-1 as 2^s * t, where t is odd
    s = 0
    t = n-1

    while t%2 ==0:
        s+=1
        t = t//2
    
    # run random k times
    for i in range(1,k-1):
        # choose a random integer a in the range [2,n-2]
        a = random.randint(2,n-2)

        current = repeated_squaring(a,2**1*t,n)
        previous = repeated_squaring(a,2**(0)*t,n)
        for j in range(2,s):
            if current == 1 and previous != 1 and previous != n-1:
                return False
            previous = current
            current = previous**2 % n
        if repeated_squaring(a,n-1,n) != 1:
            return False
    return True

def generate_key(d):
    """
    Input:
        d: integer
    Output:
        p: prime number
    """
    x = int(2**d)
    p  = -1
    q = -1
    while p == -1 or q == -1:
        if miller_rabin(x-1) == True:
            if p ==-1:
                p = x-1
            else:
                q = x-1
        x = x<<1
    return p,q

if __name__ == "__main__":
    _, d = sys.argv
    p,q = generate_key(int(d))
    write_file_publickeyinfo("./publickeyinfo.txt", p, q)
    write_file_secretprimes("./secretprimes.txt", p, q)