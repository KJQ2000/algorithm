'''
Author: Kuan Jun Qiang
'''
import sys

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
    f = open(file_path, 'w+')
    for i in content:
        f.write(str(i) + "\n")
    f.close()

def z_algo(string):
    '''
    Input:
        string: combined string of pattern and text in the form of pattern+'$'+text
    Output:
        return z_array which is the z array of the combined string(str1+'$'+pat)
    Time Complexity:
        O(n+m) where n is the length of str1 and m is the length of pat
    Space Complexity:
        O(n+m) where n is the length of str1 and m is the length of pat
    '''
    z_array = []
    z_array.append(len(string))
    r = 0
    l = 0
    zi=0
    for i in range(1,len(string)):
        k = i-l
        remaining = r-i+1
        zi = 0
        #case 1
        if i>r:
            j = i
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
    while a<len(compare_string) and b<len(compare_string) and compare_string[a]==compare_string[b]:
        a+=1
        b+=1
        matched+=1
    return matched

def Boyer_Moore(text,pattern):
    '''
    Input:
        text: text which is used to search for pattern
        pattern: pattern which is used to search for in text
    Output:
        return the list of occurence of pattern in text
    Time Complexity:
        O(n+m) where n is the length of text and m is the length of pattern
    Space Complexity:
        O(n+m) where n is the length of text and m is the length of pattern
    '''
    # initialize variables
    m = len(pattern)
    n = len(text)
    occurence = []
    pattern_unique = list(set(pattern))

    # if length of pattern or text equal to 0 or length of pattern is greater than length of text, return empty list
    if m==0 or n==0 or m>n:
        return occurence

    #if pattern and text have the same length, do explicit compare
    if m==n:
        for i in range(len(text)):
            if text[i]!=pattern[i]:
                return occurence
        return [0]
    
    #method 1 - fill up the table from right to left
    # make sure wildcard "." in the last row of pattern_unique list
    if "." in pattern:
        pattern_unique = list(set(pattern))
        pattern_unique.remove(".")
        pattern_unique.append(".")
    else:
        pattern_unique = list(set(pattern))
    # initialize bad character table with -1
    bad_character_table = [[-1]*m for i in range(len(pattern_unique))]
    for i in range(m):
        counter = 0
        target = pattern[m-i-1]
        # check the row of the target character
        for j in range(len(pattern_unique)):
            if target == pattern_unique[j]:
                break
        # fill up the table
        bad_character_table[j][m-i-1] = m-i-1
        # fill up the table from right to left
        while m-i + counter < m and bad_character_table[j][m-i+counter]==-1:
            bad_character_table[j][m-i+counter] = m-i-1
            counter +=1

    #do z-algorithm on the pattern and find reversed z-array(z^-1)
    reversed_pattern = pattern[::-1]
    z_array= z_algo(reversed_pattern)
    z_array.reverse()
    match_prefix_z_array = z_algo(pattern)

    # Good Suffix table
    good_suffix_table = [0 for i in range(int(m)+1)]
    # j = len(m)-z_array^-1[i]
    for i in range(m-1):
        j = m - z_array[i]
        good_suffix_table[j] = i
    
    #Match Prefix table
    match_prefix_table = [0 for i in range(int(m))]
    for i in range(1,m+1):
        # z_array[i](start from last char) + i(position) == m
        if match_prefix_z_array[m-i] + m-i == m:
            match_prefix_table[m-i] = match_prefix_z_array[m-i]
        else:
            if m-i == m-1:
                match_prefix_table[m-i] = 0
            else:
                match_prefix_table[m-i] = match_prefix_table[m-i+1]
    
    # Search
    # initialise variable
    i = 0
    j = m-1
    bc_mismatched_offset = 0
    gs_mismatched_offset = 0
    mp_mismatched_offset = 0
    counter = 0
    while i+j<n:
        # do explicit search
        # counter +=1 if matched pattern or matched index of text is wildcard
        while (text[i+j-counter]==pattern[j-counter] or pattern[j-counter] == ".") and counter != m:
            counter+=1
        # if matched all pattern
        if j-counter==-1:
            # append the index of occurence
            # start from index 1
            occurence.append(i+1)
            counter = 0
            # skip length of matched longest prefix
            if match_prefix_table[1]>0:
                i += m - match_prefix_table[1]
            else:
                i+=m-1
        else:
            # if not matched all pattern
            # find the mismatched index of text
            mismatched_text_char = text[i+j-counter]
            # find the row of mismatched index of text in pattern_unique
            for miss in range(len(pattern_unique)):
                if pattern_unique[miss] == mismatched_text_char:
                    break
                else:
                    # if mismatched char not in pattern unique, set miss to the length of pattern unique
                    miss = m
            # if miss found in pattern unique and no wildcard exist in pattern
            if miss <m and pattern_unique[-1] != ".":
                bc_mismatched_offset = j-counter - int(bad_character_table[miss][j-counter])
            # if miss found in pattern unique and wildcard exist in pattern
            elif miss<m and pattern_unique[-1] == "." and bad_character_table[-1][j-counter]!=-1:
                bc_mismatched_offset = min(j-counter - int(bad_character_table[miss][j-counter]),j-counter - int(bad_character_table[-1][j-counter]))
            else:
                # if miss not found in pattern unique and wildcard exist in pattern
                if pattern_unique[-1] == "." and bad_character_table[-1][j-counter]!=-1:
                    bc_mismatched_offset = j-counter - int(bad_character_table[-1][j-counter])
                else:
                    # if miss not found in pattern and wildcard not exist in pattern
                    bc_mismatched_offset = 0
            # if good suffix exist
            if good_suffix_table[j-counter+1] != 0:
                # find good suffix offset(how many positions to shift)
                gs_mismatched_offset = m-int(good_suffix_table[j-counter+1])-1
                # set match prefix offset to 0
                mp_mismatched_offset = 0
            else:
                # if good suffix not exist
                # set good suffix offset to 0
                gs_mismatched_offset = 0
                if j-counter<m-1:
                    # if match prefix offset equal to len(pattern)
                    if match_prefix_table[j-counter+1]+1 == m:
                        mp_mismatched_offset = 0
                    else:
                        # find match prefix offset(how many positions to shift)
                        mp_mismatched_offset = match_prefix_table[j-counter+1]+1
                else:
                    mp_mismatched_offset =0
            # if bad characher rule shift the most
            if max(bc_mismatched_offset,gs_mismatched_offset, mp_mismatched_offset,1) == bc_mismatched_offset:
                i+=bc_mismatched_offset
                counter = 0
            # if match prefix rule shift the most
            elif max(bc_mismatched_offset,gs_mismatched_offset, mp_mismatched_offset,1) == mp_mismatched_offset:
                i+=mp_mismatched_offset
                counter = 0
            # if good suffix rule shift the most
            elif max(bc_mismatched_offset,gs_mismatched_offset, mp_mismatched_offset,1) == gs_mismatched_offset:
                i+=gs_mismatched_offset
            else:
                i+=1
                counter=0

    return occurence

if __name__ == '__main__':
    _, filename1, filename2 = sys.argv
    text  = str(read_file(filename1))
    pattern = str(read_file(filename2))
    ans = Boyer_Moore(text,pattern)
    if len(ans)>0:
        write_file("./output_q2.txt",ans)
    else:
        f = open("./output_q2.txt", 'w+')
        f.write("\n")
        f.close()