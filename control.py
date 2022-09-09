# used for testing runtime of cplex library
import cplex
import time 

try:
    file = input("Enter file path:\n") 
    q = time.time();
    cpx = cplex.Cplex(file)
    cpx.solve()
    print(cpx.solution.get_objective_value())
except Exception as e:
    print(e)
finally:
    print(time.time()-q)