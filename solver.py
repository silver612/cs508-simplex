from math import inf
import numpy as np
from sympy import *


def to_tableau(c, A, b): # convert to tableau form 
    xb = [cons + [x] for cons, x in zip(A, b)]
    return xb + [c]

def change_to_basic(tableau): # write tableau in terms of basic varibles
    
    temp, pivot_columns = Matrix(tableau[:-1]).rref() # getting reduced row echelon form
    tableau[:-1] = temp.tolist()
    columns = np.array(tableau).T
    
    # checking if bfs is obtained
    if not(len(pivot_columns) == len(tableau)-1 and len(columns)-1 not in pivot_columns):
        raise Exception("Basic feasible solution does not exist")

    # writing z in terms of basic variables
    for pivot_column in pivot_columns:
        column = columns[pivot_column]
        row_index = np.where(column == 1)
        tableau[-1] = (np.array(tableau[-1]) - column[-1]*np.array(tableau[row_index[0][0]])).tolist()

    return tableau

def can_opt(tableau): # check if z can be optimised further
    z = tableau[-1]
    for x in z[:-1]:
        if x > 0:
            return True 
    return False

def get_pivot(tableau, v): # get pivot variable and its limiting constraint
    z = tableau[-1]
    column = next(i for i, x in enumerate(z[:-1]) if x > 0)
    limits = []
    if v[column].ub != 1e20: #1e20 is equivalent to inf
        limits.append(v[column].ub)
    for eq in tableau[:-1]:
        ei = eq[column]
        limits.append(inf if ei <= 0 else eq[-1] / ei)

    if (all([r == inf for r in limits])):
        raise Exception("Unbounded solution")

    row = limits.index(min(limits))
    return row, column

def pivot_step(tableau, pivot_position): # change basic variables and the tableau based on the pivot
    new_tableau = [[] for _ in tableau]
    
    i, j = pivot_position
    pivot_value = tableau[i][j]
    new_tableau[i] = np.array(tableau[i]) / pivot_value
    
    for eq_i, _ in enumerate(tableau):
        if eq_i != i:
            new_tableau[eq_i] = np.array(tableau[eq_i]) - np.array(new_tableau[i]) * tableau[eq_i][j]
    

    final_tableau = []
    for row in new_tableau:
        final_tableau.append(row.tolist())
    
    return final_tableau

def is_basic(column): # check if column is for a basic variable
    return sum(column) == 1 and len([c for c in column if c == 0]) == len(column) - 1

def get_solution(tableau): # get solution from tableau
    columns = np.array(tableau).T
    solutions = []
    for column in columns[:-1]:
        solution = 0
        if is_basic(column):
            one_index = column.tolist().index(1)
            solution = columns[-1][one_index]
        solutions.append(solution)
        
    return solutions

def simplex(c, A, b, v): # simplex method, descriptions of function mentioned above
    
    tableau = to_tableau(c, A, b)
    tableau = change_to_basic(tableau)

    while can_opt(tableau):
        pivot_pos = get_pivot(tableau, v)
        tableau = pivot_step(tableau, pivot_pos)
        
    solutions =  get_solution(tableau)
    return solutions, sum(np.multiply(c[:-1], solutions)) - c[-1]
