"""
Author: Kuan Jun Qiang
"""
import sys
import numpy as np

def read_file(file_path: str) -> str:
    '''
    Input: 
        file_path: file path of input file
    Output:
        return the content in the file line by line
    '''

    mystring= []
    constraintsLHSMatrix = []
    constraintsRHSVector = []

    myfile = open(file_path,'r')
    for line in myfile:
        # take out the useful information
        if line.strip()[0]!="#":
            mystring.append(str(line.strip()))
    # take out the number of decimal variables, number of constraints, objective function, constraints LHS matrix, constraints RHS vector
    numDecimalvariables = int(mystring[0])
    numConstraints = int(mystring[1])
    objective = mystring[2].split(", ")
    objective = list(map(int, objective))
    for i in range(3,3+numConstraints):
        constraintsLHSMatrix.append(mystring[i].split(", "))
    for i in range(len(constraintsLHSMatrix)):
        constraintsLHSMatrix[i] = list(map(int, constraintsLHSMatrix[i]))
    for i in range(len(mystring)-numConstraints,len(mystring)):
        constraintsRHSVector.append(mystring[i])
    constraintsRHSVector = list(map(int, constraintsRHSVector))
    
    myfile.close()
    return numDecimalvariables,numConstraints,objective,constraintsLHSMatrix,constraintsRHSVector

# this function wrtie content to a file
def write_file(file_path: str, optimal_decison: list, z_value:float):
    '''
    Input: 
        file_path: file path of output file
        optimal_decision: optimal decision list generated by calculation function
        z_value: optimal objective value generated by calculation function
    '''
    f = open(file_path, 'w')
    f.write("# optimalDecision" + "\n")
    for i in range(len(optimal_decison)):
        if i != len(optimal_decison)-1:
            f.write(str(optimal_decison[i])+", ")
        else:
            f.write(str(optimal_decison[i])+"\n")
    f.write("# optimalObjective" + "\n")
    f.write(str(z_value))
    f.close()

def build_inter_matrix(ndecimal: int, nconstraints:int,index:list):
    """
    Input:
        ndecimal: number of decimal variables
        nconstraints: number of constraints
        index: index of active constraints
    Output:
        inter_matrix: intermediate matrix(empty matrix with a useful trick)
    """
    inter_matrix = [[0]*(ndecimal+nconstraints+2) for i in range(nconstraints)]
    for i in range(len(index)):
        # fill up 1 when row and column index having the same cj
        inter_matrix[i][index[i]] = 1
    return inter_matrix

def build_matrix(ndecimal: int, nconstraints:int, objective:list, LHS:list, RHS:list):
    """
    Input:
        ndecimal: number of decimal variables
        nconstraints: number of constraints
        objective: objective list
        LHS: constraints LHS matrix
        RHS: constraints RHS vector
    Output:
        matrix: matrix for simplex method (matrix for first step only)
    """

    matrix = [[0]*(ndecimal+nconstraints+2) for i in range(nconstraints)]   # matrix for simplex method
    zj = [0]*(ndecimal+nconstraints+1)          # zj list
    cj = objective+ [0]*(nconstraints)          # cj list
    cj_zj = cj.copy()
    cj_active = cj[ndecimal:]                   # cj list for active constraints
    index = [-1]*nconstraints                   # index of active constraints
    # fill up index list
    for i in range(nconstraints):
        index[i] = i+ndecimal
    # fill up 1 when row and column index having the same cj
    for i in range(ndecimal, ndecimal+nconstraints):
        matrix[i-ndecimal][i] = 1
    # fill up LHS
    for i in range(len(LHS)):
        matrix[i][0:ndecimal] = LHS[i]
    # find maximum cj_zj
    maximum = max( (v, i) for i, v in enumerate(cj_zj) )[1]
    # fill up RHS
    for i in range(len(RHS)):
        matrix[i][ndecimal+nconstraints] = RHS[i]
        if matrix[i][maximum] == 0:
            matrix[i][ndecimal+nconstraints+1] = np.inf
        else:
            matrix[i][ndecimal+nconstraints+1] = matrix[i][ndecimal+nconstraints]/matrix[i][maximum]
    cj = objective+ [0]*(nconstraints)
    return matrix, cj, cj_zj, cj_active,zj,index

def find_q(t,j,k):
    """
    Input:
        t: target
        j: old version of the target
        k: intersection
    """
    # q = ?
    # j-?*k = t
    q = (j-t)/k
    return q

def calculation(matrix:list, cj:list, cj_zj:list, cj_active:list, zj:list,index:list):
    """
    Input:
        matrix: matrix generated from build_matrix function
        cj: cj list generated from build_matrix function
        cj_zj: cj-zj list generated from build_matrix function
        cj_active: cj list for active constraints generated from build_matrix function
        zj: zj list generated from build_matrix function
        index: index of active constraints generated from build_matrix function
    """
    # find maximum cj_zj
    maximum_x = max( (v, i) for i, v in enumerate(cj_zj) )[1]
    # find minimum theta
    minimum = matrix[0][-1]
    min_y = -1
    for i in range(1,len(matrix)):
        if matrix[i][-1]<minimum and matrix[i][-1]>=0:
            minimum = matrix[i][-1]
            min_y = i
    if min_y == -1:
        min_y=0
    # update index list
    index[min_y] = maximum_x
    # update intersection
    intersection = matrix[min_y][maximum_x]
    # update cj_active list
    cj_active[min_y] = cj[maximum_x]
    cont = True
    # find number of decimal variables
    ndecimal = len(cj_zj)-len(cj_active)
    # find number of constraints
    nConstraints = len(cj_active)
    while cont:
        # build intermediate matrix
        inter_matrix = build_inter_matrix(ndecimal,len(cj_active),index)
        
        # S/crossection value (intersection) = T
        for i in range(ndecimal+nConstraints+1):
            if i not in index:
                inter_matrix[min_y][i] = matrix[min_y][i]/intersection
        ## col_contain_one = maximum_x
        ## find ?
        for i in range(nConstraints):
            # if not the row of minimum theta, find ?
            if i != min_y:
                j = matrix[i][maximum_x]
                t = inter_matrix[i][maximum_x]
                k = inter_matrix[min_y][maximum_x]
                q = find_q(t,j,k)
                # fill up the row
                for col in range(ndecimal+nConstraints+1):
                    if col not in index:
                        j = matrix[i][col]
                        k = inter_matrix[min_y][col]
                        inter_matrix[i][col] = j-(q*k)
        # update zj list
        for i in range(len(zj)):
            sum = 0
            for j in range(nConstraints):
                sum+=cj_active[j]*(inter_matrix[j][i])
            zj[i] = sum
        # update cj_zj list
        for i in range(len(cj_zj)):
            cj_zj[i] = cj[i]-zj[i]
        # update maximum cj_zj
        maximum_x = max( (v, i) for i, v in enumerate(cj_zj) )[1]
        # if maximum cj_zj <= 0, stop
        if cj_zj[maximum_x] <=0:
            cont = False
            break
        # update theta column
        for i in range(nConstraints):
            if inter_matrix[i][maximum_x] == 0:
                inter_matrix[i][-1] = np.inf
            else:
                inter_matrix[i][-1] = inter_matrix[i][-2]/inter_matrix[i][maximum_x]
        # find minimum theta
        minimum = inter_matrix[0][-1]
        min_y = -1
        for i in range(1,len(inter_matrix)):
            if inter_matrix[i][-1]<minimum and inter_matrix[i][-1]>=0:
                minimum = inter_matrix[i][-1]
                min_y = i
        if min_y == -1:
            min_y=0
        index[min_y] = maximum_x
        intersection = inter_matrix[min_y][maximum_x]
        cj_active[min_y] = cj[maximum_x]
        matrix = inter_matrix
    
    # find optimal decision
    optimal_decision = []
    for i in range(ndecimal):
        for j in range(len(index)):
            if index[j] == i:
                optimal_decision.append(inter_matrix[j][-2])           
    return optimal_decision,zj[-1]

if __name__ == "__main__":
    _, filename= sys.argv
    numDecimalvariables,numConstraints,objective,constraintsLHSMatrix,constraintsRHSVector = read_file(filename)
    matrix, cj, cj_zj, cj_active,zj,index = build_matrix(numDecimalvariables, numConstraints,objective,constraintsLHSMatrix,constraintsRHSVector)
    optimal_decision, z_value = calculation(matrix, cj, cj_zj, cj_active,zj,index)
    write_file("lpsolution.txt",optimal_decision,z_value)