import gurobipy as gp
from gurobipy import GRB
import networkx as nx

Graph = nx.graph.Graph

NUM_threads=1

gp_options = {
    "WLSACCESSID": "6f6ff6a8-32e2-447d-b681-592b24fc09d1",
    "WLSSECRET": "333995b6-ce3f-4053-b4bf-7dcdb2b167df",
    "LICENSEID": 2411299,
}

class Nexullance_MP:
    def __init__(self, _nx_graph: Graph, path_dict: dict, _M_R: list, _Cap_remote: float, _solver:int=0, _verbose:bool=False):
        # assume uniform C^{remote}
        #LP solver options:
        '''    
        0: Automatic (solver chooses the method)
        1: Primal simplex
        2: Dual simplex
        3: Network simplex
        4: Barrier
        5: Concurrent (uses multiple methods)
        '''    
        self.nx_graph: Graph = _nx_graph
        self.M_R: list = _M_R
        self.solver: int = _solver
        self.verbose: bool = _verbose
        self.Cap_remote: float = _Cap_remote
        self.path_dict: dict = path_dict


    def init_model(self):
        num_routers=(1+pow(1+4*len(self.path_dict), 0.5))/2
        assert(num_routers==self.nx_graph.number_of_nodes() and 'length of path_dict should be N*(N-1), N is the number of routers')
        assert(len(self.M_R)==len(self.M_R[0])==num_routers and \
                'traffic matrix shape is wrong, note that this should be a M_R traffic matrix!')
        self.edge_list = list(self.nx_graph.edges())
        
        _env = gp.Env(params=gp_options)
        _env.setParam('Threads', NUM_threads)
        self.model = gp.Model(env=_env)
        self.model.setParam(GRB.Param.OutputFlag, self.verbose)
        self.model.setParam(GRB.Param.Method, self.solver)
        self.model.setParam(GRB.Param.Crossover, 0)  

        # add variables and constraints
        self.path_prob = {}
        link_load_var = {}
        link_load_constr = {}
        self.Max_load = self.model.addVar(vtype=GRB.CONTINUOUS, name='self.Max_load')
        for (u,v) in self.edge_list:
            link_load_var[(u, v)]=self.model.addVar(vtype=GRB.CONTINUOUS, name=f'link_load_({u},{v})')
            link_load_constr[(u, v)]= gp.LinExpr()
            link_load_var[(v, u)]=self.model.addVar(vtype=GRB.CONTINUOUS, name=f'link_load_({v},{u})')
            link_load_constr[(v, u)]= gp.LinExpr()

        normalization_constr={}

        unique_path_id=0
        for (s, d), paths in self.path_dict.items():
            if len(paths)>1: 
                normalization_constr[(s, d)]=gp.LinExpr()

            for path in paths:      
                if len(paths)>1:  
                    self.path_prob[unique_path_id]=self.model.addVar(vtype=GRB.CONTINUOUS, name=f'path_prob_({s}, {d})_{unique_path_id}')

                    self.path_prob[unique_path_id].setAttr(GRB.Attr.LB, 0)  # Lower bound
                    self.path_prob[unique_path_id].setAttr(GRB.Attr.UB, 1.0)  # Upper bound
                else:
                    self.path_prob[unique_path_id]=1.0

                if len(paths)>1: 
                    normalization_constr[(s, d)]+=self.path_prob[unique_path_id]
                for i in range(len(path) - 1):
                    vertex1, vertex2 = path[i], path[i + 1]
                    link_load_constr[(vertex1, vertex2)]+=self.path_prob[unique_path_id]*self.M_R[s][d]/self.Cap_remote
                unique_path_id+=1

        for (u, v), linexp in link_load_constr.items():
            self.model.addConstr(linexp==link_load_var[(u, v)])
            self.model.addConstr(self.Max_load>=link_load_var[(u, v)])
        for linexp in normalization_constr.values():
            self.model.addConstr(linexp==1.0)

        # print(f'number of variables = {len(self.path_prob)+len(link_load_var)}, number of constraints = {len(link_load_constr)+len(normalization_constr)}')
        # Set objective
        self.model.setObjective(self.Max_load, GRB.MINIMIZE)

    def solve(self):
        self.model.optimize()
        # traffic_shared = {} #{(s, d): {link (i->j): shared value}}
        all_weighted_paths={}
        if self.model.status == GRB.OPTIMAL:
            print("Optimal solution found")
            Max_load_result=self.Max_load.x
            if self.verbose:
                print("LP stats:")
                self.model.printStats() # only print out data if verbose
                print(f'Max link load is: {self.Max_load.x}')

            unique_path_id=0
            for (s,d), paths in self.path_dict.items():
                all_weighted_paths[(s, d)]=[]
                for path in paths:
                    if len(paths)>1:
                        all_weighted_paths[(s, d)].append( (path, self.path_prob[unique_path_id].x) )
                    else:
                        all_weighted_paths[(s, d)].append( (path, 1.0) )
                    unique_path_id+=1
            return Max_load_result, all_weighted_paths
            # return traffic_shared, result_link_loads, Max_load_result
        
        else:
            print("LP failed")
            self.model.setParam(GRB.Param.OutputFlag, 1)
            self.model.printStats()