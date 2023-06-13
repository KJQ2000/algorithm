"""
Author: Kuan Jun Qiang
"""
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

class global_end:
    """
    This class is used to represent global end variable
    """
    def __init__(self):
        self.value = -1
    
    def increment(self, integer):
        self.value += int(integer)

class Node:
    """
    This class is used to represent a node in the suffix tree

    Attributes:
        start: start index of edge
        end: end index of edge
        is_leaf: boolean to indicate if node is leaf
        is_root: boolean to indicate if node is root
        suffix_link: suffix link of node
        children: array of children nodes
        suffix_id: array of suffix id
    """
    def __init__(self, start=None, end=None, is_leaf=False, is_root=False, suffix_link=None):
        self.start, self.end, self.is_leaf, self.is_root, self.suffix_link = start, end, is_leaf, is_root, suffix_link
        self.children = [None] * 92
        self.suffix_id = []


    def get_edge(self, index):
        """
        to get the edge at index
        """
        return self.children[index]
    
    def get_start(self):
        """
        to get the start index of edge
        """
        return self.start
    
    def create_edge(self, index, node):
        """
        to add edge at index
        """
        self.children[index] = node
    
    def add_suffix_id(self, suffix):
        """
        to add suffix id
        """
        self.suffix_id.append(suffix)
    
    def get_end(self):
        """
        to get the end index of edge
        """
        if self.is_leaf:
            return self.end.value
        else:
            return self.end

class SuffixTree:
    '''
    Generalized Suffix Tree
    
    Attributes:
        root: root node of suffix tree
        active_node: node representing active node
        active_length: length of active node
    '''
    def __init__(self):
        #Initialize basic variables
        self.root = Node(is_root=True)
        self.root.suffix_link = self.root

        #Traversal variables
        # Reset Traverse variables
        self.active_node = self.root    #start from root
        self.active_length = 0
    
    def traverse(self, txt, end):
        """
        to traverse the suffix tree and return the last discovered node
        """

        def traverse_aux(current_node, current_length):

            # If is leaf or current length is 0, end
            if current_node.is_leaf or current_length == 0:
                return current_node
            
            #Else is internal node, update active node and length
            self.active_node = current_node
            self.active_length = current_length

            # Get active edge
            index = ord(txt[end - current_length])-36
            edge  = current_node.get_edge(index)

            #If no active edge, end
            if edge is None:
                return current_node
            
            #Else get active edge length
            edge_length = edge.get_end() - edge.get_start()

            # If edgelength is longer than current length, end
            if edge_length > current_length:
                return current_node
            
            # Else skip count down
            return traverse_aux(edge, current_length - edge_length)
            
        
        return traverse_aux(self.active_node, self.active_length)
    
    def inorder(self,node):
        """
        to perform inorder traversal of suffix tree and return the suffix id in inorder
        """

        res = []

        def inorder_aux(node):
            #Node is leaf, return suffix id
            if node.is_leaf:
                occurrence = 0
                while occurrence < len(node.suffix_id):
                    res.append(node.suffix_id[occurrence]+1)
                    occurrence += 1
            
            #Node is not leaf, perform inorder traversal
            else:
                for e in node.children:
                    if e is not None:
                        inorder_aux(e)
        
        inorder_aux(node)
        return res
    
    def ukkonen(self, txt):
        """
        to build the suffix tree using Ukkonen's algorithm

        Algorithm:
            1. For each phase, traverse the tree until last discovered node
            2. If no active edge, add new edge
            3. If active edge, split edge
            4. If internal node created in previous extension, create suffix link
            5. If internal node created in previous extension, update suffix link
            6. If internal node created in previous extension, update active node and length
        """

        j = 0 # represent extension
        ge = global_end() # global end variable

        # Phases
        for i in range(len(txt)+1):

            #Update variables
            ge.increment(1) # increment global end(Rule 1)
            prev_inter_node = None # Reset variable representing internal node created in previous extension of same phase

            # Extensions
            while j<i:

                # Reset active length if at root
                if self.active_node == self.root:
                    self.active_length = i-j
                
                # Traversal
                pointer = self.traverse(txt,i)                  # pointer = last discovered node (node after last visited edge)
                                                                # active node and length will be updated until last visited internal node where active_length >0

                # Get active edge
                index = ord(txt[i-self.active_length])-36          # Index corrensponding to first character of active/remaining length
                edge = self.active_node.get_edge(index)         # edge should be at that index in active node's child array

                # Rule 2.1: Add new edge
                if edge is None:
                    new_node = Node(i-self.active_length,ge, is_leaf=True)      # Create new edge with leaf node
                    new_node.add_suffix_id(j)                                              # Save j at leaf node
                    self.active_node.create_edge(index, new_node)                          # Add it under active_node
                
                # Rule 2.2: Split edge
                elif txt[i-1] != txt[edge.get_start() + self.active_length-1]:

                    # internal node as new parent node for branch
                    inter_node = Node(edge.get_start(), edge.get_start() + self.active_length-1, is_leaf = False)   #Create new internal edge and node
                    self.active_node.create_edge(index, inter_node)            # Replace original node at active

                    # Update original edge as new branch
                    edge.start = edge.get_start() + self.active_length-1    # Update start of original node
                    x = ord(txt[edge.start])-36                                # Get it's appropriate index
                    inter_node.create_edge(x,edge)                             # Add original node to internal node

                    # Create New branch with leaf node
                    new_node = Node(i-1, ge, is_leaf = True)        # Create new leaf node
                    y = ord(txt[ge.value-1])-36                        # Get it's appropriate index
                    new_node.add_suffix_id(j)                                  # Save j at leaf node
                    inter_node.create_edge(y,new_node)                         # Add new node to internal node

                    # Resolve suffix links
                    inter_node.suffix_link = self.root                      # Link new internal node to root

                    if prev_inter_node is not None:                         # Update previously created internal node if it exists
                        prev_inter_node.suffix_link = inter_node            # Link previously created internal node to new internal node
                    
                    prev_inter_node = inter_node                            # Update prev_inter_node for next extension
                
                # Rule 2.3: Add payload at leaf
                elif pointer.is_leaf:
                    pointer.add_suffix_id(j)                                   # Save j at leaf node
                # Rule 3: Do nothing
                else:
                    break                                                   # Skip to next phase (Showstopper trick)
 
                # Update variables
                j += 1                                                      # Next extension
                self.active_node = self.active_node.suffix_link             # Move active node across suffix link


            self.active_length += 1  # increment active length
        return self.inorder(self.root)
    

    def build_suffix_array(self, txt):
        """
        Inserts text strings in list texts into the GST
        """
        N = len(txt)

        # Add terminal character to each text
        txt = txt + '$'
        return self.ukkonen(txt)

if __name__ == '__main__':
    _, filename = sys.argv
    string = str(read_file(filename))
    a = SuffixTree()
    ans = a.build_suffix_array(string)
    #clear file and add occurrences to file
    f = open("./output_sa.txt", 'w')
    f.write(str(ans[0]) + "\n")
    f.close()
    for i in range(1,len(ans)):
        write_file("./output_sa.txt",str(ans[i]))


"""
References:
Tutorial week 4:
https://drive.google.com/file/d/1v4l_Fhwpe1AQxo6M9kNIy_0D3rIj3R1l/view?usp=share_link
"""