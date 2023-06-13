'''
Author: Kuan Jun Qiang
'''

import sys

# this function reads a file and return its content
def read_file(file_path: str) -> str:
    '''
    Input: 
        file_path: file path of input file
    Output:
        return the content in the file line by line
    '''
    mystring= ''
    myfile = open(file_path,'r')
    for line in myfile:
        mystring += line.strip()
    myfile.close()
    return mystring


# this function wrtie content to a file
def write_file(file_path: str, content: str):
    '''
    Input: 
        file_path: file path of output file
        content: things that need to write into the file
    '''
    f = open(file_path, 'a+')
    f.write(content + "\n")
    f.close()

def z_algo(str1,pat):
    '''
    Input:
        str1: text which is used to search for pattern
        pat: pattern which is used to search for in text
    Output:
        return z_array which is the z array of the combined string(str1+'$'+pat)
    Time Complexity:
        O(n+m) where n is the length of str1 and m is the length of pat
    Space Complexity:
        O(n+m) where n is the length of str1 and m is the length of pat
    '''
    #combine the string
    string = pat+'$'+str1
    z_array = []
    #insert length of string as the first value of z_array
    z_array.append(len(string))
    i = 1
    r = 0
    l = 0
    zi=0
    for i in range(1,len(string)):
        #calculate k and remaining
        k = i-l
        remaining = r-i+1
        #case 1
        if i>r:
            j = i
            zi = 0
            zi=explicit_compare(string,zi,j)
            z_array.append(zi)
        #case2a Z[k]<remaining
        elif z_array[k]<remaining:
            z_array.append(z_array[k])
            zi = z_array[k]
        #case2b Z[k]>remaining
        elif z_array[k]>remaining:
            z_array.append(remaining)
            zi = remaining
        #case2c Z[k]==remaining
        else:
            zi = z_array[k]
            j = i+1
            zi+=explicit_compare(string,zi,j)
            z_array.append(zi)
        #update l and r
        if i +zi -1> r:
            l = i
            r = i+zi-1
    return z_array

def explicit_compare(compare_string,a,b):
    '''
    Input:
        compare_string: string which is used to compare
        a: index of the first string
        b: index of the second string
    Output:
        return the number of matched characters
    Time Complexity:
        O(n) where n is the length of compare_string
    '''
    matched=0
    # do explicit compare
    while a<len(compare_string) and b<len(compare_string) and compare_string[a]==compare_string[b]:
        a+=1
        b+=1
        matched+=1
    return matched

def detect_transposition_error(str1,pattern):
    '''
    Input:
        str1: text which is used to search for pattern
        pattern: pattern which is used to search for in text
    Output:
        return a list of index where the transposition error occurs and index where pattern matched
    Time Complexity:
        O(n+m) where n is the length of str1 and m is the length of pattern
    Space Complexity:
        O(n+m) where n is the length of str1 and m is the length of pattern
    '''
    answer = []
    #check if the pattern is empty or the length of pattern is greater than the length of str1
    if len(pattern) ==0 or len(str1) ==0 or len(pattern) >len(str1):
        # return empty list
        return answer
    #combine the string
    combined = pattern+"$"+str1
    #get the z array of the combined string
    ori_z_array = z_algo(str1,pattern)
    #reverse the string
    reversed_str1 = str1[::-1]
    #reverse the pattern
    reversed_pattern = pattern[::-1]
    #get the z array of the reversed string and pattern(this is the z array for detecting suffix)
    reversed_z_array = z_algo(reversed_str1,reversed_pattern)
    #reverse the z array back to the original order
    temp = reversed_z_array[0:len(pattern)+1]
    reversed_z_array = reversed_z_array[len(pattern)+1:]
    reversed_z_array = reversed_z_array[::-1]
    reversed_z_array = temp + reversed_z_array
    # skip pattern part and end when less than pattern length
    for i in range(len(pattern)+1,len(ori_z_array)-len(pattern)+1):
        matched_prefix = ori_z_array[i]
        matched_suffix = reversed_z_array[i+len(pattern)-1]
        if matched_prefix+matched_suffix == len(pattern)-2:
            #front compare with pattern's behind and behind comapre with pattern's front
            if combined[i+ori_z_array[i]] == pattern[matched_prefix+1] and combined[i+ori_z_array[i]+1] == pattern[matched_prefix] and i+ori_z_array[i]<len(combined):
                answer.append(str(i - len(pattern)) + " " + str(i+ori_z_array[i] - len(pattern)))
        elif ori_z_array[i] == len(pattern):
            answer.append(str(i - len(pattern)))
    return answer



if __name__ == '__main__':
    _, filename1, filename2 = sys.argv
    text  = str(read_file(filename1))
    pattern = str(read_file(filename2))
    ans = detect_transposition_error(text,pattern)
    #clear file and add occurrences to file
    f = open("./output_q1.txt", 'w')
    f.write(str(len(ans)) + "\n")
    f.close()
    for i in ans:
        write_file("./output_q1.txt",str(i))