'''
Author: Kuan Jun Qiang
'''
import sys

# this function wrtie content to a file
def write_file(file_path: str, content: str):
    '''
    Input: 
        file_path: file path of output file
        content: things that need to write into the file
    '''
    f = open(file_path, 'w')
    f.write(content + "\n")
    f.close()


class Huffman_node:
    """
    This class is used to create a node for huffman tree

    Attributes:
        parent: parent node
        left: left child node
        right: right child node
        data: data of the node
    """
    def __init__(self,data=None):
        self.parent = None
        self.left = None
        self.right = None
        self.data = data

class Huffman_decode(Huffman_node):
    """
    This class is used to create a huffman tree for decoding
    """
    def __init__(self):
        self.root = Huffman_node()  #self.root is the root of the huffman tree
    
    def insert(self,data, binary):
        """
        to insert a node into the huffman tree
        """
        current = self.root
        i = 0
        while i <len(binary):
            if binary[i] == '0':
                if current.left == None:
                    current.left = Huffman_node()
                    current.left.parent = current
                    current = current.left
                else:
                    current = current.left
            else:
                if current.right == None:
                    current.right = Huffman_node()
                    current.right.parent = current
                    current = current.right
                else:
                    current = current.right
            i +=1
        if i == len(binary):
            current.data = data
    
    def search(self,binary):
        """
        to search a node in the huffman tree
        """
        current = self.root
        i = 0
        while i < len(binary):
            if binary[i] == '0':
                if current.left == None:
                    return None
                else:
                    current = current.left
            else:
                if current.right == None:
                    return None
                else:
                    current = current.right
            i +=1
        if i == len(binary):
            if current.data == None:
                return None
            else:
                return current.data
            
class Decoder:
    def __init__(self,filename):
        self.fileName = filename
        self.bin_rep = ""
        self.answer = ""
        self.discovered = -1
        self.i = 0
        self.length_fileContent = 0
        self.bwt_string = ""
        self.frequency_rank = [[0]for i in range(92)]
    
    def unpack_bin_file(self):
        """
        to unpack the binary file
        """
        with open(self.fileName, mode = 'rb') as file:
            fileContent = file.read()
            self.length_fileContent = len(fileContent)

            byte_rep = fileContent[self.i]
            temp_binrep = ""
            while byte_rep!=0:
                temp_binrep = str(byte_rep%2) + temp_binrep
                byte_rep = byte_rep//2
            while len(temp_binrep)<8:
                temp_binrep = '0' + temp_binrep
            self.bin_rep += temp_binrep
            self.i +=1
            return self.bin_rep

    
    def elias_decode(self):
        self.discovered = -1
        char_needed = ""
        length_to_discover = 0
        #if first char is 0, it denotes length
        if self.bin_rep[0] == '0':
            self.discovered +=1
            length_to_discover = 1
        else:
            self.bin_rep = self.bin_rep[1:]
            return 1
        while length_to_discover!=0:
            #make sure self.bin_rep has enough bits
            self.update_bin_rep()
            # if it denotes length
            if self.bin_rep[self.discovered +1] == '0':
                char_needed = self.bin_rep[self.discovered+1:self.discovered+1+length_to_discover+1]
                # print(char_needed[0])
                char_needed = '1'+char_needed[1:]
                self.discovered += length_to_discover +1
                length_to_discover = int(char_needed,2)
            else:
                #if it denotes value
                char_needed = self.bin_rep[self.discovered+1:self.discovered+length_to_discover+2]
                self.discovered +=length_to_discover +1
                self.bin_rep = self.bin_rep[self.discovered+1:]
                self.discovered = -1
                self.update_bin_rep()
                return int(char_needed,2)
    
    def huffman_decode(self,array):
        """
        This function insert data into huffman tree
        """
        array.sort(key= lambda x: (x[1],x[0]))
        H_decode = Huffman_decode()
        for i in array:
            H_decode.insert([i[0],i[1]])
        

        
    def update_bin_rep(self):
         """
         to update the bin_rep
         """
         if (int(self.i)*8 - (int(self.i)*8-self.discovered))<8 and self.i<self.length_fileContent:
            self.unpack_bin_file()
    
    def bwt_decode(self,bwt_string):
        """
        to decode the bwt string
        """
        ans = ""
        order_array = [0 for i in range(len(bwt_string))]
        for i in range(len(bwt_string)):
            # to count the frequency of each character
            self.frequency_rank[ord(bwt_string[i])-36][0] = int(self.frequency_rank[ord(bwt_string[i])-36][0])+1
            # to record the order of each character
            order_array[i] = int(self.frequency_rank[ord(bwt_string[i])-36][0])
        # to count the frequency rank of each character
        self.frequency_rank[0].append(1)
        # to count the frequency rank of each character
        for i in range(0,len(self.frequency_rank)-1):
            # if the frequency of the character is not 0, add the previous frequency rank to the current frequency rank
            if self.frequency_rank[i][0]!=0:
                # to count the frequency rank of each character
                self.frequency_rank[i+1].append(self.frequency_rank[i][0]+self.frequency_rank[i][1])
            else:
                # to count the frequency rank of each character
                self.frequency_rank[i+1].append(self.frequency_rank[i][1])
        
        ans+=bwt_string[0]
        order = 0
        target = bwt_string[0]
        # rank[x] + order[x] - 1
        for i in range(len(bwt_string)-1):
            switch =  self.frequency_rank[ord(target)-36][1] + order_array[order]-2
            target = bwt_string[switch]
            order = switch
            ans+=target
        ans = ans[:-1]
        ans = ans[::-1]
        return ans

    def decode(self):
        self.unpack_bin_file()

        # decode the length of bwt string
        length_of_bwt = self.elias_decode() #7
        
        # decode the length of huffman tree
        nUniqChars = self.elias_decode() #4

        lst = [[]for i in range(nUniqChars)]
        for i in range(nUniqChars):
            self.discovered = -1
            self.update_bin_rep()

            lst[i].append(chr(int(str(self.bin_rep[self.discovered+1:self.discovered+7+1]),2)))
            self.discovered +=7
            self.bin_rep = self.bin_rep[self.discovered+1:]
            self.update_bin_rep()

            self.discovered = -1
            code_length = self.elias_decode()
            self.update_bin_rep()
            huffman_code = self.bin_rep[:code_length]
            
            self.discovered = -1
            self.discovered +=int(code_length)
            self.bin_rep = self.bin_rep[self.discovered+1:]
            self.update_bin_rep()
            lst[i].append(str(huffman_code))
        lst.sort(key= lambda x: (x[1],x[0]))
        H_decode = Huffman_decode()
        for k in lst:
            H_decode.insert(k[0],k[1])
        pointer = 1
        while length_of_bwt > len(self.bwt_string):
            if H_decode.search(self.bin_rep[0:pointer]) == None:
                pointer +=1
            else:
                temp = H_decode.search(self.bin_rep[0:pointer])
                self.bin_rep = self.bin_rep[pointer:]
                run_length =  self.elias_decode()
                for i in range(run_length):
                    self.bwt_string += temp
                pointer = 1
        print("bwt string = "+ self.bwt_string)
        return self.bwt_decode(self.bwt_string)
        
if __name__ == '__main__':
    filename = sys.argv[1]
    D = Decoder(filename)
    ans = D.decode()
    write_file("recovered.txt",ans)

"""
References:
Tutorial week 4:
https://drive.google.com/file/d/1v4l_Fhwpe1AQxo6M9kNIy_0D3rIj3R1l/view?usp=share_link
"""