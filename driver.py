from math import inf
import cplex
import solver
import time 
class var:
    def __init__(self):
        self.name = "" # variable name
        self.index = -1 # variable index
        self.index_1 = -1 # if free variable, need to break into 2 variables. This is index of other variable
        self.lb = 0 # lower bound
        self.ub = inf # upper bound
        self.ub1 = inf # may need to change ub, this is a backup storage

try:
    file = input("Enter file path:\n") 
    #q = time.time(); # used to check runtime
    cpx = cplex.Cplex(file) # read lp file
except:
    print("Cplex error")
else:
    num_v = cpx.variables.get_num() # get variables and initialise var objects
    v = []
    
    for i in range(num_v):
        v.append(var())
        v[i].index = i 
        v[i].name = cpx.variables.get_names(i)
        v[i].lb = cpx.variables.get_lower_bounds(i)
        v[i].ub = cpx.variables.get_upper_bounds(i)  
        v[i].ub1 = v[i].ub 
    
    num_c = cpx.linear_constraints.get_num() # get constraints
    A = []
    b = []
    new_var = 0
    for i in range(num_c):
        ind, val = cpx.linear_constraints.get_rows(i).unpack()
        row = [val[ind.index(i)] if i in ind else 0 for i in range(num_v)]
        for j in range(new_var):
            row.append(0)
        rhs = cpx.linear_constraints.get_rhs(i)
        sign = cpx.linear_constraints.get_senses(i)
        if sign=='G':       # changing signs to <=
            row = [-r for r in row]
            rhs = -rhs 
            sign = 'L'
        if sign=='L':       # adding slack variables
            y = var()
            y.index = num_v + new_var
            v.append(y)
            new_var = new_var + 1
            row.append(1)
        A.append(row)
        b.append(rhs)
    
    c = cpx.objective.get_linear() # get objective function
    for j in range(new_var):
        c.append(0)
    c.append(0) 
    c_con = cpx.objective.get_offset() # constant part of objective function
    maximize = (cpx.objective.get_sense() == -1) # == 1 for minimize
    
    for row in A:      # adding remaining column parts for slack variables
        for j in range(new_var+num_v-len(row)):
            row.append(0)
    
    split_var = 0
    for i in range(num_v): # making lower bounds of all variables = 0 and taking care of free variables
        if v[i].lb == -inf:
            y = var()
            y.index = num_v + new_var + split_var 
            y.ub = -v[i].lb 
            v.append(y)
            split_var = split_var + 1 
            v[i].lb = 0
            v[i].index_1 = y.index 
            for row in A:
                row.append(-row[i])
        else:
            for j in range(num_c):
                b[j] = b[j] - v[i].lb * A[j][i]
            v[i].ub = v[i].ub - v[i].lb
            v[i].lb = 0
    
    for i, row in enumerate(A): # setting upper bound of slack variables
        try:
            pos = row.index(1, num_v+1, num_v+new_var)
            v[pos].ub = b[i] - sum([v[ri].ub for ri,r in enumerate(row) if r > 0])
        except:
            pos = -1

    try:  # call solver function
        # different parameters sent to ensure simplex has to always maximize
        if maximize: 
            x, val = solver.simplex(c, A, b, v)
            print("Variables: ")
            for i, xi in enumerate(x[0:num_v]): # get values of user defined variables from simplex variables
                if v[i].index_1 != -1:
                    print(cpx.variables.get_names(i)+": "+str(xi - val[v[i].index_1])) 
                elif v[i].ub != v[i].ub1:
                    print(cpx.variables.get_names(i)+": "+str(xi + v[i].ub1-v[i].ub))
                else: 
                    print(cpx.variables.get_names(i)+": "+str(xi))
            print("Objective function value:")
            print(val + c_con)
        else:
            x, val = solver.simplex([-c1 for c1 in c], A, b, v)
            print("Variables: ")
            for i, xi in enumerate(x[0:num_v]): # get values of user defined variables from simplex variables
                if v[i].index_1 != -1:
                    print(cpx.variables.get_names(i)+": "+str(xi + val[v[i].index_1])) 
                elif v[i].ub != v[i].ub1:
                    print(cpx.variables.get_names(i)+": "+str(xi + v[i].ub1-v[i].ub))
                else: 
                    print(cpx.variables.get_names(i)+": "+str(xi))
            print("Objective function value:")
            print(-val + c_con)
        
    except Exception as e: # print exception raised by simplex solver code
        print(e)
    #finally:
        #print(time.time()-q) #used to check runtime

    
    