import numpy as np
from scipy.optimize import linprog

# def Solve_load_balancing_reciprocal(path_dict, edge_list, traffic_matrix=None, _integer=False, _solver='highs-ds', _options={'disp': True}):

#     num_routers=(1+pow(1+4*len(path_dict), 0.5))/2
#     assert(num_routers.is_integer() and 'length of path_dict should be N*(N-1), N is the number of routers')
    
#     if traffic_matrix==None:
#         traffic_matrix=[[1 for j in range(int(num_routers))] for i in range(int(num_routers))]# default traffic pattern is uniform
#         for i in range(int(num_routers)): 
#             traffic_matrix[i][i]=0

#     # pre-process the path dictionary, ensure reciporcity
#     # Create a new dictionary to store the reorganized keys and values
#     reorganized_dict = {}

#     # Iterate through the keys of the input dictionary
#     for key, value in path_dict.items():
#         u, v = key
#         reorganized_key = (min(u, v), max(u, v))  # the smaller value comes first
#         if reorganized_key not in reorganized_dict.keys():
#             reorganized_dict[reorganized_key] = value
#         # elif not reorganized_dict[reorganized_key] == value:
#         #     raise UserWarning("Warning: the original path dictionary does not ensure path reciporcity")
        

#     data = [] # for eac row, there are three columns: [(s,d), path(list of int), list of edges in the path(list of tuple of int)]
#     for (u, v), paths in reorganized_dict.items():
#         for path in paths:
#             arcs=[(path[i], path[i+1]) for i in range(len(path)-1)]
#             arcs.extend([(path[i+1], path[i]) for i in range(len(path)-1)])
#             new_data = [ (int(u),int(v)), path, arcs]
#             data.append(new_data)

#     num_paths=len(data)

#     normalization=[] 
#     for (u, v) in reorganized_dict.keys():
#         Aij=[0]*num_paths
#         in_the_zoon=False
#         for i in range(num_paths): # the entries that we are looking for should be nested together
#             if data[i][0]==(u,v):
#                 Aij[i]=1
#                 in_the_zoon=True
#             elif in_the_zoon == True:
#                 break
#         normalization.append(Aij)
#     normalization=np.array(normalization)

#     coefficients=[]
#     for (u,v) in edge_list:
#         # one direction
#         B=[0]*num_paths
#         for i in range(num_paths):
#             if (u,v) in data[i][2]:
#                 B[i]=traffic_matrix[u][v]
#         coefficients.append(B)
#         # another direction
#         B=[0]*num_paths
#         for i in range(num_paths):
#             if (v,u) in data[i][2]:
#                 B[i]=traffic_matrix[v][u]
#         coefficients.append(B)
#     coefficients=np.array(coefficients)


#     assert(num_paths == coefficients.shape[1]) # denoted as n
#     num_links = coefficients.shape[0] # denoted as m
#     assert(num_links == 2*len(edge_list))
#     #constraints:
#     """
#     1.
#     variables y1, y2,.., ym that represents the link loads
#     y1 = A11*x1 + A12*x2 + ... + A1n*xn;
#     ...
#     ym = Am1*x1 + Am2*x2 + ... + Amn*xn

#     2.
#     variable Y that is greater or equals to y1, y2,.., ym
#     Y >= y1; ....; Y >= ym

#     3.
#     0<=xij<=1

#     4.
#     SUM_k (xijk) == 1
#     """



#     ## 2. constraints for the variables Y
#     A_combinations = np.zeros((num_links, num_paths))
#     A_y = np.eye(num_links)
#     A_Y = -np.ones((num_links, 1))
#     A = np.hstack((A_combinations, A_y, A_Y))

#     b = np.zeros(num_links)

#     n_variables=A.shape[1]
#     n_constraints=A.shape[0]
#     assert(n_variables==num_paths+num_links+1)
#     assert(n_constraints==num_links)

#     ## 3. 0<xij<=1
#     bounds=[(0, 1) for _ in range(num_paths)]
#     bounds.extend([(0, None) for _ in range(num_links+1)])
#     bounds=np.array(bounds)

#     ## 4. SUM_k (xijk) == 1
#     Aeq= normalization
#     num_s_d=Aeq.shape[0]
#     Aeq_y = np.zeros((num_s_d, num_links))
#     Aeq_Y = np.zeros((num_s_d, 1))
#     Aeq = np.hstack((Aeq, Aeq_y, Aeq_Y))
#     beq = np.ones(num_s_d)
    
#     ## 1. (equality) constraints for the variables y1, y2,.., ym
#     A_combinations = coefficients
#     A_y = -np.eye(num_links)
#     A_Y = np.zeros((num_links, 1))
#     Aeq = np.vstack( (Aeq, np.hstack((A_combinations, A_y, A_Y))) )
#     beq = np.hstack( ( beq, np.zeros(num_links) ) )

#     # Objective function: Minimizing Y
#     c = np.zeros(n_variables)
#     c[-1] = 1

#     # Solve the linear program
#     result = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds, method=_solver, options=_options)

#     # Extract the solution
#     optimal_Y = result.fun
#     optimal_variables = result.x    

#     # linprog_verbose_callback(result)

#     print("=============calculation done===========")

#     all_weighted_paths={}
#     link_loads=[]

#     print("Optimal objective funtion found: %s" % optimal_Y)
#     for i, variable in enumerate(optimal_variables):
#         if i < num_paths:
#             source, dest=data[i][0]
#             if not( (source, dest) in all_weighted_paths.keys() ):
#                 all_weighted_paths[(source, dest)]=[]
#             all_weighted_paths[(source, dest)].append( (data[i][1], variable) )
#         elif i < num_paths+num_links:
#             link_loads.append(variable)
#     return all_weighted_paths, link_loads


def Solve_load_balancing(path_dict, edge_list, traffic_matrix=[], _integer=False, _solver='highs-ds', _options={'disp': True}):

    num_routers=(1+pow(1+4*len(path_dict), 0.5))/2
    assert(num_routers.is_integer() and 'length of path_dict should be N*(N-1), N is the number of routers')
    
    if list(traffic_matrix):
        assert(len(traffic_matrix)==len(traffic_matrix[0])==num_routers and  'traffic matrix shape is wrong, note that this should be a R2R traffic matrix!')
    else:
        traffic_matrix=[[1 for j in range(int(num_routers))] for i in range(int(num_routers))]# default traffic pattern is uniform
        for i in range(int(num_routers)): 
            traffic_matrix[i][i]=0

    data = [] # for eac row, there are three columns: [(s,d), path(list of int), list of edges in the path(list of tuple of int)]
    for (u, v), paths in path_dict.items():
        for path in paths:
            new_data = [ (int(u),int(v)), path, [(path[i], path[i+1]) for i in range(len(path)-1)] ]
            data.append(new_data)

    num_paths=len(data)

    normalization=[] 
    for (u, v) in path_dict.keys():
        Aij=[0]*num_paths
        in_the_zoon=False
        for i in range(num_paths): # the entries that we are looking for should be nested together
            if data[i][0]==(u,v):
                Aij[i]=1
                in_the_zoon=True
            elif in_the_zoon == True:
                break
        normalization.append(Aij)
    normalization=np.array(normalization)

    coefficients=[]
    for (u,v) in edge_list:
        #TODO: alternatively, enforce bi-directional paths to be on the same link, see difference
        # one direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (u,v) in data[i][2]:
                B[i]=traffic_matrix[data[i][1][0]][data[i][1][-1]]
        coefficients.append(B)
        # another direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (v,u) in data[i][2]:
                B[i]=traffic_matrix[data[i][1][0]][data[i][1][-1]]
        coefficients.append(B)
    coefficients=np.array(coefficients)


    assert(num_paths == coefficients.shape[1]) # denoted as n
    num_links = coefficients.shape[0] # denoted as m
    assert(num_links == 2*len(edge_list))
    #constraints:
    """
    1.
    variables y1, y2,.., ym that represents the link loads
    y1 = A11*x1 + A12*x2 + ... + A1n*xn;
    ...
    ym = Am1*x1 + Am2*x2 + ... + Amn*xn

    2.
    variable Y that is greater or equals to y1, y2,.., ym
    Y >= y1; ....; Y >= ym

    3.
    0<=xij<=1

    4.
    SUM_i (xij) == 1
    """



    ## 2. constraints for the variables Y
    A_combinations = np.zeros((num_links, num_paths))
    A_y = np.eye(num_links)
    A_Y = -np.ones((num_links, 1))
    A = np.hstack((A_combinations, A_y, A_Y))

    b = np.zeros(num_links)

    n_variables=A.shape[1]
    n_constraints=A.shape[0]
    assert(n_variables==num_paths+num_links+1)
    assert(n_constraints==num_links)

    ## 3. 0<=xij<=1
    bounds=[(0, 1) for _ in range(num_paths)]
    bounds.extend([(0, None) for _ in range(num_links+1)])
    bounds=np.array(bounds)

    ## 4. SUM_i (xij) == 1
    Aeq= normalization
    num_s_d=Aeq.shape[0]
    Aeq_y = np.zeros((num_s_d, num_links))
    Aeq_Y = np.zeros((num_s_d, 1))
    Aeq = np.hstack((Aeq, Aeq_y, Aeq_Y))
    beq = np.ones(num_s_d)
    
    ## 1. (equality) constraints for the variables y1, y2,.., ym
    A_combinations = coefficients
    A_y = -np.eye(num_links)
    A_Y = np.zeros((num_links, 1))
    Aeq = np.vstack( (Aeq, np.hstack((A_combinations, A_y, A_Y))) )
    beq = np.hstack( ( beq, np.zeros(num_links) ) )

    # Objective function: Minimizing Y
    c = np.zeros(n_variables)
    c[-1] = 1

    # Solve the linear program
    result = linprog(c, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds, method=_solver, options=_options)

    # Extract the solution
    optimal_Y = result.fun
    optimal_variables = result.x    

    # linprog_verbose_callback(result)

    print("=============calculation done===========")

    all_weighted_paths={}
    link_loads=[]

    print("Optimal objective funtion found: %s" % optimal_Y)
    for i, variable in enumerate(optimal_variables):
        if i < num_paths:
            source, dest=data[i][0]
            if not( (source, dest) in all_weighted_paths.keys() ):
                all_weighted_paths[(source, dest)]=[]
            all_weighted_paths[(source, dest)].append( (data[i][1], variable) )
        elif i < num_paths+num_links:
            link_loads.append(variable)
    return all_weighted_paths, link_loads