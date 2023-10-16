import gurobipy as gp
from gurobipy import GRB

options = {
    "WLSACCESSID": "6f6ff6a8-32e2-447d-b681-592b24fc09d1",
    "WLSSECRET": "333995b6-ce3f-4053-b4bf-7dcdb2b167df",
    "LICENSEID": 2411299,
}

def Solve_load_balancing(path_dict, edge_list, traffic_matrix=[], maximum_prob=1.0, _solver=0, _verbose=0, _integer=0):
    #LP solver options:
    '''
    0: Automatic (solver chooses the method)
    1: Primal simplex
    2: Dual simplex
    3: Network simplex
    4: Barrier
    5: Concurrent (uses multiple methods)
    '''

    num_routers=(1+pow(1+4*len(path_dict), 0.5))/2
    assert(num_routers.is_integer() and 'length of path_dict should be N*(N-1), N is the number of routers')
    
    if list(traffic_matrix):
        assert(len(traffic_matrix)==len(traffic_matrix[0])==num_routers and  'traffic matrix shape is wrong, note that this should be a R2R traffic matrix!')
    else:
        traffic_matrix=[[1 for j in range(int(num_routers))] for i in range(int(num_routers))]# default traffic pattern is uniform
        for i in range(int(num_routers)): 
            traffic_matrix[i][i]=0

    with gp.Env(params=options) as env, gp.Model(env=env) as model:
        # Define variables
        path_prob = {}
        link_load_var = {}
        link_load_constr = {}
        Max_load = model.addVar(vtype=GRB.CONTINUOUS, name='Max_load')
        for (u,v) in edge_list:
            link_load_var[(u, v)]=model.addVar(vtype=GRB.CONTINUOUS, name=f'link_load_({u},{v})')
            link_load_constr[(u, v)]= gp.LinExpr()
            link_load_var[(v, u)]=model.addVar(vtype=GRB.CONTINUOUS, name=f'link_load_({v},{u})')
            link_load_constr[(v, u)]= gp.LinExpr()

        normalization_constr={}

        unique_path_id=0
        for (s, d), paths in path_dict.items():
            if len(paths)>1: 
                normalization_constr[(s, d)]=gp.LinExpr()

            for path in paths:      
                if len(paths)>1:  
                    if _integer:
                        path_prob[unique_path_id]=model.addVar(vtype=GRB.BINARY, name=f'path_prob_({s}, {d})_{unique_path_id}')
                    else:
                        path_prob[unique_path_id]=model.addVar(vtype=GRB.CONTINUOUS, name=f'path_prob_({s}, {d})_{unique_path_id}')

                    path_prob[unique_path_id].setAttr(GRB.Attr.LB, 0)  # Lower bound
                    path_prob[unique_path_id].setAttr(GRB.Attr.UB, maximum_prob)  # Upper bound
                else:
                    path_prob[unique_path_id]=1.0

                if len(paths)>1: 
                    normalization_constr[(s, d)]+=path_prob[unique_path_id]
                for i in range(len(path) - 1):
                    vertex1, vertex2 = path[i], path[i + 1]
                    link_load_constr[(vertex1, vertex2)]+=path_prob[unique_path_id]*traffic_matrix[s][d]
                unique_path_id+=1

        for (u, v), linexp in link_load_constr.items():
            model.addConstr(linexp==link_load_var[(u, v)])
            model.addConstr(Max_load>=link_load_var[(u, v)])
        for linexp in normalization_constr.values():
            model.addConstr(linexp==1.0)

        print(f'number of variables = {len(path_prob)+len(link_load_var)}, number of constraints = {len(link_load_constr)+len(normalization_constr)}')
        # Set objective
        model.setObjective(Max_load, GRB.MINIMIZE)
        # Enable verbose output
        model.setParam(GRB.Param.OutputFlag, _verbose)  # 1: Enables output, 0: Disables output (default)
        # model.setParam(GRB.Param.OptimalityTol, 1e-9)
        # model.setParam(GRB.Param.IntFeasTol, 1e-9)
        # model.setParam(GRB.Param.FeasibilityTol, 1e-9)
        # model.setParam(GRB.Param.IterationLimit, 2)
        env.setParam('Threads', 6)    #Limit the number of cores used according to the license
        model.setParam(GRB.Param.Method, _solver)  
        # Optimize the model
        model.optimize()
        
        all_weighted_paths={}
        result_link_loads={}
        # if model.status == GRB.OPTIMAL:
        print("Optimal solution found")
        unique_path_id=0
        for (s,d), paths in path_dict.items():
            all_weighted_paths[(s, d)]=[]
            for path in paths:
                if len(paths)>1:
                    all_weighted_paths[(s, d)].append( (path, path_prob[unique_path_id].x) )
                else:
                    all_weighted_paths[(s, d)].append( (path, 1.0) )
                unique_path_id+=1
        for (u, v), load in link_load_var.items():
            result_link_loads[(u,v)]=load.x
        print(f'Max link load is: {Max_load.x}')

    return all_weighted_paths, result_link_loads
    
