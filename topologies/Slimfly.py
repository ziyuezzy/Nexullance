from . import HPC_topo
import networkx as nx
from statistics import mean
import galois
import random

#========================some functions to calculate the MMS graph=======================================
# This part of the code is copied from this github repo: https://github.com/AdamLatos/slimfly-gen/blob/master/

# Find generator sets
def find_generator_sets(q, primitive_elem, delta):
    l=(q-delta)/4
    assert(l.is_integer())
    l = int(l)

    if delta == 1:
        X1 = [1]
        X2 = []
        for i in range(1,q-1):
            elem = pow(primitive_elem, i)
            if i % 2 == 0:
                X1.append(elem)
            else:
                X2.append(elem)
        return (X1, X2)
    elif delta == 0:
        X1 = [1]
        X2 = []
        for i in range(1,4*l):
            elem = pow(primitive_elem, i)
            if i % 2 == 0:
                X1.append(elem)
            else:
                X2.append(elem)
        return (X1, X2)
    elif delta == -1:
        X1 = [1]
        X2 = []
        for i in range(1,4*l-1):
            elem = pow(primitive_elem, i)
            if (i % 2 == 0 and i<=2*l-2) or (i % 2 == 1 and i>2*l-2):
                X1.append(elem)
            else:
                X2.append(elem)
        return (X1, X2)
    else:
        raise ValueError(f"delta cannot be {delta}")


# Create routes - each route as list in dict with ({0,1}, x, y) as key
def create_routes(q, Fq, X1, X2):
    keys = [(i,int(x),int(y)) for i in range(2) for x in Fq for y in Fq]
    routes = {k: set() for k in keys}
    for x in Fq:
        for y in Fq:
            for yp in Fq:
                if (y - yp) in X1:
                    routes[(0,int(x),int(y))].add((0,int(x),int(yp)))
                    routes[(0,int(x),int(yp))].add((0,int(x),int(y)))
                if (y - yp) in X2:
                    routes[(1,int(x),int(y))].add((1,int(x),int(yp)))
                    routes[(1,int(x),int(yp))].add((1,int(x),int(y)))
                for xp in Fq:
                    if (xp * x + yp) == y:
                        routes[(0,int(x),int(y))].add((1,int(xp),int(yp)))
                        routes[(1,int(xp),int(yp))].add((0,int(x),int(y)))
    return routes
#========================================== end ============================================

# define the slimfly class
class Slimflytopo(HPC_topo.HPC_topo):
    # def __init__(self, num_vertices):
    #     super(Slimflytopo, self).__init__()
    #     self.generate_slimfly_topo(num_vertices)

    # def __init__(self, edgelist):
    #     super(Slimflytopo, self).__init__()
    #     # create the embedded graph
    #     graph = nx.Graph()
    #     graph.add_edges_from(edgelist)
    #     self.nx_graph = graph

    def __init__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            super(Slimflytopo, self).__init__()
            self.generate_slimfly_topo(args[0], args[1])

        elif isinstance(args[0], list):
            super(Slimflytopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')

            
    def generate_slimfly_topo(self, num_vertices, degree):
        q=pow(num_vertices/2, 0.5)
        if not q.is_integer():
            raise KeyError("specified number of vertices is not supported by 2-Diameter Slimfly, num_vertices need to be 2*q^2")
        q=int(q)
        delta=3*q-degree*2
        GF=galois.GF(q)
        Fq=GF.elements
        primitive_elem = GF.primitive_element
        X1= None
        X2=None
        if delta==0 or delta==1 or delta==-1:
            (X1, X2) = find_generator_sets(q, primitive_elem, delta)
        else:
            raise ValueError(f"incorrect input for slimfly topology: {num_vertices}, {degree}")
        connectivity = create_routes(q, Fq, X1, X2)
        assert(len(connectivity)==num_vertices)
        def Cartesian_product_to_N(i,x,y):
            return i*(pow(q,2))+x*q+y
        def N_to_Cartesian_product(N):
            return N//(pow(q,2)), (N%(pow(q,2)))//q, N%q
        edges=[]
        for u in range(num_vertices):
            i, x, y = N_to_Cartesian_product(u)
            for connection in connectivity[(i,x,y)]:
                v = Cartesian_product_to_N(connection[0], connection[1], connection[2])
                edges.extend([(u, v)])

        # create the embedded graph
        graph = nx.Graph()
        graph.add_edges_from(edges)
        self.nx_graph = graph
        assert(mean([i[1] for i in list(self.nx_graph.degree)])==degree)
        return


        
    def set_critical_link_failures(self, failure_ratio, seed=0):

        return

    def set_noncritical_link_failures(self, failure_ratio, seed=0):

        return