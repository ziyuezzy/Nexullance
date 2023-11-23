import gurobipy as gp
from gurobipy import GRB

NUM_threads=1

options = {
    "WLSACCESSID": "6f6ff6a8-32e2-447d-b681-592b24fc09d1",
    "WLSSECRET": "333995b6-ce3f-4053-b4bf-7dcdb2b167df",
    "LICENSEID": 2411299,
}

def Solve_load_balancing(nx_graph, R2R_TM=[], _solver=0, _verbose=0):
    #LP solver options:
    '''
    0: Automatic (solver chooses the method)
    1: Primal simplex
    2: Dual simplex
    3: Network simplex
    4: Barrier
    5: Concurrent (uses multiple methods)
    '''    

    s_d_pairs = [(s, d) for s in nx_graph.nodes() 
                        for d in nx_graph.nodes() if s != d]
    edge_list = list(nx_graph.edges())

    num_routers= nx_graph.number_of_nodes()
    if list(R2R_TM):
        assert(len(R2R_TM)==len(R2R_TM[0])==num_routers and  'traffic matrix shape is wrong, note that this should be a R2R traffic matrix!')
    else:
        R2R_TM=[[1 for j in range(int(num_routers))] for i in range(int(num_routers))]# default traffic pattern is uniform
        for i in range(int(num_routers)): 
            R2R_TM[i][i]=0

    with gp.Env(params=options) as env, gp.Model(env=env) as model:
        # Define variables
        link_share_var = {} # dict of dict, {link (i->j): {(s, d): share value}}. # 2*E*V^2 variables
        link_load_var = {} # 2*E variables, 
        link_load_expression = {} # 2*E constraints
        # flow_conservation = [] # V^3 linear constraints
        Max_load = model.addVar(vtype=GRB.CONTINUOUS, name='Max_load') # 2*E constraints
        for (i, j) in edge_list:
            link_load_var[(i, j)]=model.addVar(
                vtype=GRB.CONTINUOUS, name=f'link_load_({i},{j})')
            model.addConstr(link_load_var[(i, j)]<=Max_load)
            link_load_expression[(i, j)]=gp.LinExpr()
            link_load_expression[(i, j)]-=link_load_var[(i, j)]

            link_load_var[(j, i)]=model.addVar(
                vtype=GRB.CONTINUOUS, name=f'link_load_({j},{i})')
            model.addConstr(link_load_var[(j, i)]<=Max_load)
            link_load_expression[(j, i)]=gp.LinExpr()
            link_load_expression[(j, i)]-=link_load_var[(j, i)]

            link_share_var[(i, j)]={}
            link_share_var[(j, i)]={}
            for (s, d) in s_d_pairs:
                if s==d:
                    continue
                else:
                    link_share_var[(i, j)][(s, d)]=model.addVar(
                        vtype=GRB.CONTINUOUS, name=f'link_share^({s},{d})_({i},{j})')
                    link_share_var[(i, j)][(s, d)].setAttr(GRB.Attr.LB, 0.0)  # Lower bound
                    link_share_var[(i, j)][(s, d)].setAttr(GRB.Attr.UB, 1.0)  # Upper bound

                    link_share_var[(j, i)][(s, d)]=model.addVar(
                        vtype=GRB.CONTINUOUS, name=f'link_share^({s},{d})_({j},{i})')
                    link_share_var[(j, i)][(s, d)].setAttr(GRB.Attr.LB, 0.0)  # Lower bound
                    link_share_var[(j, i)][(s, d)].setAttr(GRB.Attr.UB, 1.0)  # Upper bound
                    
        for (s, d) in s_d_pairs: # flow conservation (V^3 linear constraints)
            for i in nx_graph.nodes():
                conservation=gp.LinExpr()
                for j in list(nx_graph.neighbors(i)):
                    assert(((i, j) in edge_list) or ((j, i) in edge_list))
                    conservation+=link_share_var[(i, j)][(s, d)]
                    conservation-=link_share_var[(j, i)][(s, d)]
                    link_load_expression[(i, j)]+=link_share_var[(i, j)][(s, d)]*R2R_TM[s][d]
                if i == s:
                    conservation-=1
                if i == d:
                    conservation+=1

                model.addConstr(conservation==0)
                # flow_conservation.append(conservation)

        for linexp in link_load_expression.values():
            model.addConstr(linexp==0)

        # print(f'number of variables = {len(path_prob)+len(link_load_var)}, number of constraints = {len(link_load_constr)+len(normalization_constr)}')
        # Set objective
        model.setObjective(Max_load, GRB.MINIMIZE)
        # Enable verbose output
        model.setParam(GRB.Param.OutputFlag, _verbose)  # 1: Enables output, 0: Disables output (default)
        # model.setParam(GRB.Param.OptimalityTol, 1e-9)
        # model.setParam(GRB.Param.IntFeasTol, 1e-9)
        # model.setParam(GRB.Param.FeasibilityTol, 1e-9)
        # model.setParam(GRB.Param.IterationLimit, 2)
        env.setParam('Threads', NUM_threads)    #Limit the number of cores used according to the license
        model.setParam(GRB.Param.Method, _solver)  
        model.setParam(GRB.Param.Crossover, 0)  
        # Optimize the model
        model.optimize()

        traffic_shared = {} #{(s, d): {link (i->j): shared value}}
        result_link_loads={}
        if model.status == GRB.OPTIMAL:
            print("Optimal solution found")
            if _verbose:
                print("LP stats:")
                model.printStats() # only produce data if verbose
            
            for (s, d) in s_d_pairs:
                traffic_shared[(s, d)]={}
                for (i, j) in edge_list:
                    traffic_shared[(s, d)][(i, j)]=link_share_var[(i, j)][(s, d)].x
                    traffic_shared[(s, d)][(j, i)]=link_share_var[(j, i)][(s, d)].x


            for (u, v), load in link_load_var.items():
                result_link_loads[(u,v)]=load.x

            Max_load_result=Max_load.x
            print(f'Max link load is: {Max_load.x}')

            return traffic_shared, result_link_loads, Max_load_result
        
        else:
            print("LP failed")
            model.setParam(GRB.Param.OutputFlag, 1)
            model.printStats()