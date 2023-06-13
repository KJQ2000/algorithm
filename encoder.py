class GlobalEnd:
    def __init__(self):
        self.value = -1
    
    def increment(self):
        self.value +=1

class Node:
    def __init__(self, start=None, end=None, suffix_link=None, is_root=False, is_leaf= False):
        self.start = start
        self.end = end
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.children = [None] * 128
        self.suffix_link = suffix_link
        self.suffix_id = []
    
    def get_edge(self, index):
        return self.children[index]
    
    def add_edge(self, index, node):
        self.children[index] = node
    
    def add_suffix(self, extension):
        self.suffix_id.append(extension)
    
    def get_start(self):
        return self.start
    
    def get_end(self):
        if self.is_leaf:
            return self.end.value
        else:
            return self.end
    
    def get_length(self):
        return self.get_end() - self.get_start() + 1

class SuffixTree:
    def __init__(self):
        self.root = Node(is_root=True)
        self.root.suffix_link = self.root
        self.active_node = self.root
        self.active_length = 0
    
    def traverse(self, txt, end):
        def traverse_aux(current_node, current_length):
            if current_node.is_leaf or current_length == 0:
                return current_node
            self.active_node = current_node
            self.active_length = current_length
            index = ord(txt[end - current_length])
            edge  = current_node.get_edge(index)
            if edge is None:
                return current_node
            edge_length = edge.get_end() - edge.get_start()
            if edge_length > current_length:
                return current_node
            return traverse_aux(edge, current_length - edge_length)
            
        
        return traverse_aux(self.active_node, self.active_length)
    
    def inorder(self,node):
        res = []
        def inorder_aux(node):
            if node.is_leaf:
                for occurrence in node.suffix_id:
                    res.append(occurrence)
            else:
                for e in node.children:
                    if e is not None:
                        inorder_aux(e)
        inorder_aux(node)
        return res
    
    def ukkonen(self, txt):
        i = 0
        j = 0
        global_end = GlobalEnd()
        while i <= len(txt):
            global_end.increment()
            prev_inter_node = None
            while j<i:
                if self.active_node == self.root:
                    self.active_length = i-j
                pointer = self.traverse(txt,i)
                index = ord(txt[i-self.active_length])
                edge = self.active_node.get_edge(index)

                if edge is None:
                    new_node = Node(i-self.active_length,global_end, is_leaf=True)
                    new_node.add_suffix(j)
                    self.active_node.add_edge(index, new_node)

                elif txt[i-1] != txt[edge.get_start() + self.active_length-1]:

                    inter_node = Node(edge.get_start(), edge.get_start() + self.active_length-1, is_leaf = False)
                    self.active_node.add_edge(index, inter_node)
                    edge.start = edge.get_start() + self.active_length-1
                    x = ord(txt[edge.start])
                    inter_node.add_edge(x,edge)
                    new_node = Node(i-1, global_end, is_leaf = True)
                    y = ord(txt[global_end.value-1])
                    new_node.add_suffix(j)
                    inter_node.add_edge(y,new_node)
                    inter_node.suffix_link = self.root

                    if prev_inter_node is not None:
                        prev_inter_node.suffix_link = inter_node
                    
                    prev_inter_node = inter_node
                elif pointer.is_leaf:
                    pointer.add_suffix(j)
                else:
                    break
                j += 1
                self.active_node = self.active_node.suffix_link
            i += 1
            self.active_length += 1
        return self.inorder(self.root)

    def preprocess(self, txt):
        N = len(txt)
        # Add terminal character to each text
        txt = txt + '$'
        return self.ukkonen(txt)
######################################### SUFFIX ARRAY GENERATOR END HERE #########################################
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

# this class pack answer into binary file
class BinaryPacker:
    
    def __init__(self):
        self.mybitstring = ""
        self.file = open("bwtencoded.bin", "wb")
    
    def append(self, bitstring):
        self.mybitstring = self.mybitstring + bitstring
        #check if need to pack to file or not for every append
        self.packtofile()
    
    def packtofile(self):
        # I declare buffer size as 8
        # make sure self.mybitstring not exceed buffer size
        # else write to bin file
        while len(self.mybitstring) >=8:
            mybitstring_towrite = self.mybitstring[:8]
            self.mybitstring = self.mybitstring[8:]
            mynumber = int(mybitstring_towrite,2)
            mybyte = mynumber.to_bytes(1, byteorder='big')

            self.file.write(mybyte)
    
    def __str__(self) -> str:
        return self.mybitstring
    
    def close(self):
        # close file
        # make sure last byte is 8 bits
        while len(self.mybitstring)>1 and len(self.mybitstring)<8:
            self.mybitstring = self.mybitstring + "0"
            self.packtofile()
        self.file.close()

# this class is for huffman encoding
class huffman:
    def __init__(self):
        # Declare basic variables
        self.heap = []  # use to store heap
        self.size = 0   # size of the heap
        #36 to 127
        self.encoding_table = [[]for i in range(92)]    # use to return encoding table
        self.ascii = [] # store unique character
    
    def parent(self, pos):
        """
        Input:
        pos: position of the node
        Output:
        return the parent position of the node
        """
        return pos//2
    
    def left_child(self, pos):
        """
        Input:
        pos: position of the node
        Output:
        return the left child position of the node
        """
        return 2*pos + 1
    
    def right_child(self, pos):
        """
        Input:
        pos: position of the node
        Output:
        return the right child position of the node
        """
        return 2*pos + 2
    
    def is_leaf(self, pos):
        """
        Input:
        pos: position of the node
        Output:
        return True if the node is leaf, else return False
        """
        if pos >= (len(self.heap)//2) and pos <= len(self.heap):
            return True
        return False
    
    def insert(self, array):
        """
        This function insert the array into the heap

        Input:
        array: array of tuple (character, frequency)
        """
        for i in array:
            self.heap.append(i)
            self.size += 1
    
    def swap(self, pos1, pos2):
        """
        This function swap the position of two nodes

        Input:
        pos1: position of the first node
        pos2: position of the second node
        """
        self.heap[pos1], self.heap[pos2] = self.heap[pos2], self.heap[pos1]
    

    def min_heapify(self,pos):
        """
        This function heapify the heap, make sure it is a min heap

        Input:
        pos: position of the node
        """
        # if is not leaf
        if self.is_leaf(pos) == False:
            # if probability of parent is greater than left child
            # if self.heap[pos][1]>=self.heap[self.left_child(pos)][1]:
                # if no right child
                if self.right_child(pos)>=self.size and self.heap[pos][1]>=self.heap[self.left_child(pos)][1]:
                    # check probability
                    # if probability of parent is greater than left child
                    if self.heap[pos][1]>self.heap[self.left_child(pos)][1]:
                        self.swap(pos,self.left_child(pos))
                        self.min_heapify(self.left_child(pos))
                    # if probability is equal
                    # check len(char)
                    elif self.heap[pos][1] == self.heap[self.left_child(pos)][1] and len(self.heap[pos][0])>len(self.heap[self.left_child(pos)][0]):
                        self.swap(pos,self.left_child(pos))
                        self.min_heapify(self.left_child(pos))
                    # if probability is equal
                    # check char
                    elif self.heap[pos][1] == self.heap[self.left_child(pos)][1] and self.heap[pos][0]>self.heap[self.left_child(pos)][0]:
                        self.swap(pos,self.left_child(pos))
                        self.min_heapify(self.left_child(pos))
                #check if the parent is greater than the children
                elif self.right_child(pos)<self.size:
                    min = None
                    # freq of left child is greater than right child
                    if self.heap[self.left_child(pos)][1] > self.heap[self.right_child(pos)][1]:
                        min = self.right_child(pos)
                    # same freq
                    elif self.heap[self.left_child(pos)][1] == self.heap[self.right_child(pos)][1]:
                        if len(self.heap[self.left_child(pos)][0]) >len(self.heap[self.right_child(pos)][0]):
                                min = self.right_child(pos)
                        elif len(self.heap[self.left_child(pos)][0]) == len(self.heap[self.right_child(pos)][0]):
                            # lexico order
                            if self.heap[self.left_child(pos)][0] > self.heap[self.right_child(pos)][0]:
                                min = self.right_child(pos)
                            else:
                                min = self.left_child(pos)
                        else:
                            min = self.left_child(pos)
                    else:
                        min = self.left_child(pos)
                    # compare with parent
                    if self.heap[pos][1] > self.heap[min][1]:
                        self.swap(pos,min)
                        self.min_heapify(min)
                    # same freq
                    elif self.heap[pos][1] == self.heap[min][1]:
                        if len(self.heap[pos][0]) >len(self.heap[min][0]):
                            self.swap(pos,min)
                            self.min_heapify(min)
                        elif len(self.heap[pos][0]) == len(self.heap[min][0]):
                            # lexico order
                            if self.heap[pos][0] > self.heap[min][0]:
                                self.swap(pos,min)
                                self.min_heapify(min)


    def min_heap(self):
        """
        This function build the min heap
        """
        # start from self.size//2 because all the following nodes are leaves
        for pos in range(self.size//2, -1, -1):
            self.min_heapify(pos)
        if self.size<=3:
            self.min_heapify(0)
    
    def serve(self):
        """
        This function serve the root of the heap
        """
        self.heap[0],self.heap[-1] = self.heap[-1],self.heap[0]
        self.size -=1
        return self.heap.pop()
    
    def build_encoding_table(self):
        """
        This function build the encoding table
        """
        self.min_heap()
        while self.size>1:
            first_serve = self.serve()
            first = first_serve[0]
            for i in first:
                # put 0 into encoding_table[first serve]
                self.encoding_table[ord(i)-36].append(0)
                if str(ord(i)-36) not in self.ascii:
                    self.ascii.append(str(ord(i)-36))
            # rearrange the heap
            self.min_heapify(0)
            second_serve = self.serve()
            second = second_serve[0]
            for i in second:
                # put 1 into encoding_table[second serve]
                self.encoding_table[ord(i)-36].append(1)
                if str(ord(i)-36) not in self.ascii:
                    self.ascii.append(str(ord(i)-36))
            # rearrange the heap
            self.min_heapify(0)
            # insert the new node(combining first serve and second serve) into the heap
            if first_serve[1]<second_serve[1]:
                self.insert([[first_serve[0]+second_serve[0],first_serve[1]+second_serve[1]]])
            elif first_serve[1] == second_serve[1]:
                if len(first_serve[0])<len(second_serve[0]):
                    self.insert([[first_serve[0]+second_serve[0],first_serve[1]+second_serve[1]]])
                elif len(first_serve[0]) == len(second_serve[0]):
                    if first_serve[0]<second_serve[0]:
                        self.insert([[first_serve[0]+second_serve[0],first_serve[1]+second_serve[1]]])
                    else:
                        self.insert([[second_serve[0]+first_serve[0],first_serve[1]+second_serve[1]]])
                else:
                    self.insert([[second_serve[0]+first_serve[0],first_serve[1]+second_serve[1]]])
            else:
                self.insert([[second_serve[0]+first_serve[0],first_serve[1]+second_serve[1]]])
            self.min_heap()
        for i in self.ascii:
            # Since I use append in the previous loop, I need to reverse the order of the encoding_table
            self.encoding_table[int(i)] = self.encoding_table[int(i)][::-1]
        return self.encoding_table

    
    def __str__(self):
        return self.encoding_table

class Encoder:
    def __init__(self, txt=None):
        """
        This function initialize the Encoder class

        Input:
            txt: the text to be encoded
        """
        #Initialize basic variables
        self.txt = txt

    def binary_of(self,num):
        """
        Converts a string of txt to binary
        """
        binary_rep = ""
        while num !=0:
            binary_rep = str(num%2) + binary_rep
            num = num//2
        return binary_rep
    
    def generate_bwt_string(self,txt):
        """
        Generates the BWT string from the suffix array
        """
        T = SuffixTree()
        suffix_array = T.preprocess(txt)
        bwt = ""
        txts = txt+"$"
        for i in suffix_array:
            bwt += txts[i-1]
        return bwt

    #Elias code
    def elias_code(self,txt):
        """
        This function encode the txt using Elias code

        Input:
            txt: the text(or number) to be encoded
        Output:
            elias_rep: elias omega code of txt(or number)
        """

        # find the binary
        binary_rep = self.binary_of(txt)

        elias_rep = ""
        elias_rep+=binary_rep

        n = len(binary_rep)

        if n == 1:
            return elias_rep
        
        while n>1:
            n = len(binary_rep)
            var = ""
            n=n-1
            binary_rep = self.binary_of(n)
            var  = '0'+binary_rep[1:]
            elias_rep = var + elias_rep
        return elias_rep
    
    def run_length(self,txt):
        """
        Run length encoding
        
        Input:
            txt: the text to be encoded
        Output:
            run_length_lst: the run length encoding of txt
        """
        run_length_lst = []
        i = 0
        while i < len(txt):
            count = 1
            while i+1 < len(txt) and txt[i] == txt[i+1]:
                count+=1
                i+=1
            run_length_lst.append([txt[i],count])
            i+=1
        return run_length_lst
    
    def encoder(self,txt):
        """
        This is the main function to encode txt as describe in the assignment

        Input:
            txt: the text to be encoded
        """
        global_binary = BinaryPacker()
        lst = []
        txt = txt + '$' # add the terminal character
        distinct = set(txt)
        T = SuffixTree()
        H = huffman()

        # find suffix array of txt
        suffix_array = T.preprocess(txt)

        """"""""""""""""""""""""""""""""""" HEADER PART """""""""""""""""""""""""""""""""""
        #since len(bwt_string) = len(suffix_array), we only need to encode len(suffix_array)
        global_binary.append(self.elias_code(len(suffix_array)))

        #encode the unique characters
        global_binary.append(self.elias_code(len(distinct))) #+1 for the terminal character
        
        #build frequency table
        freq_table = [[None] for i in range(92)]
        ascii = []
        for i in txt:
            if freq_table[ord(i)-36] == [None]:
                freq_table[ord(i)-36] = 1
                ascii.append(i)
            else:
                freq_table[ord(i)-36] +=1
        for i in ascii:
            lst.append([i,freq_table[ord(i)-36]])
        
        # insert into the heap
        H.insert(lst)
        H.min_heap()
        encoding_table = H.build_encoding_table()
        # sort the ascii and make sure terminal character is at the end
        ascii.sort()
        ascii.pop(0)
        ascii.append("$")
        for i in ascii:
            # add in the binary representation of unqiue character in ascii
            # make sure the binary representation is 7 bits
            unique = self.binary_of(ord(i))
            while len(unique) <7:
                unique = "0"+unique
            global_binary.append(unique)
            # add in the binary representation of the length of the huffman code
            global_binary.append(self.elias_code(len(encoding_table[ord(i)-36])))
            huffman_code = ""
            # add in the huffman code
            for j in range(len(encoding_table[ord(i)-36])):
                huffman_code += str(encoding_table[ord(i)-36][j])
            global_binary.append(huffman_code)
        """"""""""""""""""""""""""""""""""" DATA PART """""""""""""""""""""""""""""""""""
        # find the run length list of the bwt string
        run_length_lst = self.run_length(self.generate_bwt_string(txt))
        # encode the run length list
        for i in run_length_lst:
            huffman_code = ""
            for j in range(len(encoding_table[ord(i[0])-36])):
                huffman_code += str(encoding_table[ord(i[0])-36][j])
            global_binary.append(huffman_code)
            global_binary.append(self.elias_code(i[1]))
        global_binary.close()

if __name__ == '__main__':
    filename = sys.argv[1]
    string = str(read_file(filename))
    T = Encoder()
    ans = T.encoder(string)

"""
References:
Tutorial week 4:
https://drive.google.com/file/d/1v4l_Fhwpe1AQxo6M9kNIy_0D3rIj3R1l/view?usp=share_link
"""