import cvxpy as cp
import pickle
import pandas as pd
import numpy as np



def Generate_load_balancing_problem(path_dict, edge_list, traffic_matrix=None, _integer=False):

    num_routers=(1+pow(1+4*len(path_dict), 0.5))/2
    assert(num_routers.is_integer() and 'length of path_dict should be N*(N-1), N is the number of routers')
    
    if traffic_matrix==None:
        traffic_matrix=[[1 for j in range(int(num_routers))] for i in range(int(num_routers))]# default traffic pattern is uniform
        for i in range(int(num_routers)): 
            traffic_matrix[i][i]=0

    data = [] # for eac row, there are three columns: [(s,d), path(list of int), list of edges in the path(list of tuple of int)]
    for (u, v), paths in path_dict.items():
        for path in paths:
            new_data = [ (int(u),int(v)), path, [(path[i], path[i+1]) for i in range(len(path)-1)] ]
            data.append(new_data)

    num_paths=len(data)
    x=cp.Variable(num_paths, integer=_integer)

    A=[] # matrix for constraints, there shoule be N*(N-1) number of constraints, N is the number of routers
    for (u, v) in path_dict.keys():
        Aij=[0]*num_paths
        in_the_zoon=False
        for i in range(num_paths): # the entries that we are looking for should be nested together
            if data[i][0]==(u,v):
                Aij[i]=1
                in_the_zoon=True
            elif in_the_zoon == True:
                break
        A.append(Aij)

    A=np.array(A)
    # A=A.transpose()
    constraints=[ A @ x == 1, x>=0, x<=1] 

    # Define objective function -- the maximum of all link's load
    # this is dependent on the traffic pattern

    list_of_link_loads=[]
    for (u,v) in edge_list:
        #TODO: alternatively, enforce bi-directional paths to be on the same link, see difference
        # one direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (u,v) in data[i][2]:
                B[i]=traffic_matrix[u][v]
        list_of_link_loads.append(B@x)
        # another direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (v,u) in data[i][2]:
                B[i]=traffic_matrix[v][u]
        list_of_link_loads.append(B@x)

    list_of_link_loads=cp.hstack(list_of_link_loads)
    objective = cp.Minimize(cp.max(list_of_link_loads))

    problem = cp.Problem(objective, constraints)

    return data, problem




def Solve_load_balancing(path_dict, edge_list, traffic_matrix=None, _integer=False, _solver=None, _verbose= True):

    num_routers=(1+pow(1+4*len(path_dict), 0.5))/2
    assert(num_routers.is_integer() and 'length of path_dict should be N*(N-1), N is the number of routers')
    
    if traffic_matrix==None:
        traffic_matrix=[[1 for j in range(int(num_routers))] for i in range(int(num_routers))]# default traffic pattern is uniform
        for i in range(int(num_routers)): 
            traffic_matrix[i][i]=0

    data = [] # for eac row, there are three columns: [(s,d), path(list of int), list of edges in the path(list of tuple of int)]
    for (u, v), paths in path_dict.items():
        for path in paths:
            new_data = [ (int(u),int(v)), path, [(path[i], path[i+1]) for i in range(len(path)-1)] ]
            data.append(new_data)

    num_paths=len(data)
    x=cp.Variable(num_paths, integer=_integer)

    A=[] # matrix for constraints, there shoule be N*(N-1) number of constraints, N is the number of routers
    for (u, v) in path_dict.keys():
        Aij=[0]*num_paths
        in_the_zoon=False
        for i in range(num_paths): # the entries that we are looking for should be nested together
            if data[i][0]==(u,v):
                Aij[i]=1
                in_the_zoon=True
            elif in_the_zoon == True:
                break
        A.append(Aij)

    A=np.array(A)
    # A=A.transpose()
    constraints=[ A @ x == 1, x>=0, x<=1] 

    # Define objective function -- the maximum of all link's load
    # this is dependent on the traffic pattern

    list_of_link_loads=[]
    for (u,v) in edge_list:
        #TODO: alternatively, enforce bi-directional paths to be on the same link, see difference
        # one direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (u,v) in data[i][2]:
                B[i]=traffic_matrix[u][v]
        list_of_link_loads.append(B@x)
        # another direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (v,u) in data[i][2]:
                B[i]=traffic_matrix[v][u]
        list_of_link_loads.append(B@x)

    list_of_link_loads=cp.hstack(list_of_link_loads)
    objective = cp.Minimize(cp.max(list_of_link_loads))

    problem = cp.Problem(objective, constraints)

    if _solver:
        problem.solve(solver=_solver, verbose=_verbose)
    else:
        problem.solve(verbose=_verbose)

    all_weighted_paths={}

    if problem.status not in ["infeasible", "unbounded"]:
        # Otherwise, problem.value is inf or -inf, respectively.
        print("Optimal objective funtion found: %s" % problem.value)
        for i, variable in enumerate(problem.variables()[0]):
            source, dest=data[i][0]
            if not( (source, dest) in all_weighted_paths.keys() ):
                all_weighted_paths[(source, dest)]=[]
            
            all_weighted_paths[(source, dest)].append( (data[i][1], variable.value) )
        print("problem solved with cp.", problem.solver_stats.solver_name)
    else:
        print(problem.status)

    return all_weighted_paths