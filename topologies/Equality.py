import networkx as nx
from . import HPC_topo


# Notations for Equality network:
# n = number of routers; k = inter-router radix; p = number of endpoints per router
# ahops: a list of odd numbers, each number contribute to one link connected to each router
# bhops: a list of even numbers, each number contribute to two link connected to each router
# Therefore, this should hold: k = len(ahops)+2*len(bhops)
class Equalitytopo(HPC_topo.HPC_topo):
    def __init__(self, n, k, ahops, bhops):
        super(Equalitytopo, self).__init__()
        self.generate_Equality_topo(n, k, ahops, bhops)

    def generate_Equality_topo(self, n, k, ahops, bhops):
        assert(k==len(ahops)+2*len(bhops))
        assert(ahops[0]==-1 and ahops[1]==1)
        edges=[]
        # calculate edge list according to the rules of Equality network
        for v in range(n):
            if v%2 == 0:
                for odd_number in ahops:
                    edges.extend([(v, (odd_number+v)%n)])
                for even_number in bhops:
                    edges.extend([(v, (even_number+v)%n)])
            else:
                for odd_number in ahops:
                    edges.extend([(v, (-odd_number+v)%n)])
                for even_number in bhops:
                    edges.extend([(v, (-even_number+v)%n)])

        # create the embedded graph
        graph = nx.Graph()
        graph.add_edges_from(edges)
        self.nx_graph = graph
        return