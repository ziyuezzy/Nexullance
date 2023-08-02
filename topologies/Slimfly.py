from . import HPC_topo
import networkx as nx

#========================some functions to calculate the MMS graph=======================================
# This part of the code is copied from this github repo: https://github.com/AdamLatos/slimfly-gen/blob/master/
def find_primitive(q, Fq):
    primitive_element = 0
    for elem in Fq:
        hist = []
        for power in range(1,q+1):
            res = pow(elem,power) % q
            if res in hist:
                break
            hist.append(res)
        if len(hist) == q-1:
            primitive_element = elem
            break
    if primitive_element == 0:
        raise ValueError("primitive_element == 0")
    return primitive_element
# Find generator sets
def find_generator_sets(q, primitive_elem):
    X1 = [1]
    X2 = []
    for i in range(1,q-1):
        elem = pow(primitive_elem, i) % q
        if i % 2 == 0:
            X1.append(elem)
        else:
            X2.append(elem)
    return (X1, X2)
# Create routes - each route as list in dict with ({0,1}, x, y) as key
def create_routes(q, Fq, X1, X2):
    keys = [(i,x,y) for i in range(2) for x in Fq for y in Fq]
    routes = {k: [] for k in keys}
    for x in Fq:
        for y in Fq:
            for yp in Fq:
                if (y - yp)%q in X1:
                    routes[(0,x,y)].append((0,x,yp))
                    routes[(0,x,yp)].append((0,x,y))
                if (y - yp)%q in X2:
                    routes[(1,x,y)].append((1,x,yp))
                    routes[(1,x,yp)].append((1,x,y))
                for xp in Fq:
                    if (xp * x + yp) % q == y:
                        routes[(0,x,y)].append((1,xp,yp))
                        routes[(1,xp,yp)].append((0,x,y))
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
        if len(args) == 1 and isinstance(args[0], int):
            super(Slimflytopo, self).__init__()
            self.generate_slimfly_topo(args[0])

        elif isinstance(args[0], list):
            super(Slimflytopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')

            
    def generate_slimfly_topo(self, num_vertices):
        q=pow(num_vertices/2, 0.5)
        if not q.is_integer():
            raise KeyError("specified number of vertices is not supported by 2-Diameter Slimfly, num_vertices need to be 2*q^2")

        q=int(q)
        Fq = range(q)
        primitive_elem = find_primitive(q, Fq)
        (X1, X2) = find_generator_sets(q, primitive_elem)
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
        return
