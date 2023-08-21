import cvxpy as cp
import pickle
import pandas as pd
import numpy as np


def LP_load_balancing(path_dict, edge_list, topo, config):

    #input a non-weighted path dict, output a weighted path dict
    dict = {'source':[ ],
            'dest':[ ],
            'path':[ ],
            'edges': [] }

    df = pd.DataFrame(dict)
    for (u, v), paths in path_dict.items():
        for path in paths:
            new_data = {
                'source': int(u),
                'dest': int(v),
                'path': [path],
                'edges': [[(path[i], path[i+1]) for i in range(len(path)-1)]]
            }
            new_row = pd.DataFrame(new_data)
            df = pd.concat([df, new_row], ignore_index=True)  # Reset index using ignore_index=True

    num_paths=len(df.index)
    x=cp.Variable(num_paths)

    A=[]
    for (u, v) in path_dict.keys():
        Aij=[0]*num_paths
        in_the_zoon=False
        for i in range(num_paths):
            if df.iloc[i]['source']==u and df.iloc[i]['dest']==v:
                Aij[i]=1
                in_the_zoon=True
            elif in_the_zoon == True:
                break
        A.append(Aij)

    A=np.array(A)
    # A=A.transpose()
    constraints=[ A @ x == 1, x>=0, x<=1] 

    # Define objective function
    list_of_link_loads=[]
    for (u,v) in edge_list:
        #TODO: alternatively, enforce bi-directional paths to be on the same link, see difference
        # one direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (u,v) in df.iloc[i]['edges']:
                B[i]=1
        list_of_link_loads.append(B@x)
        # another direction
        B=[0]*num_paths
        for i in range(num_paths):
            if (v,u) in df.iloc[i]['edges']:
                B[i]=1
        list_of_link_loads.append(B@x)

    list_of_link_loads=cp.hstack(list_of_link_loads)
    objective = cp.Minimize(cp.max(list_of_link_loads))

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCIPY)

    all_weighted_paths={}

    if problem.status not in ["infeasible", "unbounded"]:
        # Otherwise, problem.value is inf or -inf, respectively.
        print("Optimal objective funtion found: %s" % problem.value)
        for i, variable in enumerate(problem.variables()[0]):
            source=df.iloc[i]['source']
            dest=df.iloc[i]['dest']
            if not( (source, dest) in all_weighted_paths.keys() ):
                all_weighted_paths[(source, dest)]=[]
            
            all_weighted_paths[(source, dest)].append( (df.iloc[i]['path'], variable.value) )
        pickle.dump(all_weighted_paths, open(f'../pickled_data/graphs_and_paths/LP_weighted_{config}_{topo}_paths.pickle', 'wb'))
    else:
        print(problem.status)

