import sys
import os
sys.path.append("/users/ziyzhang/topology-research")
from topologies.RRG import RRGtopo
import globals as gl
import numpy as np
import networkx as nx

def main():
    # configs = [(16, 5)]
    configs = [(16, 5), (25, 6), (36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
    for V, D in configs:
        EPR=(D+1)//2
        _network = RRGtopo(V, D)
        G = _network.nx_graph
        # convert the graph to directional, and clear all vertex/edge attributes
        G = nx.to_directed(G)
        # Sort nodes by ID
        sorted_nodes = sorted(G.nodes())
        # Create a new graph and add nodes and edges (ensuring order)
        G_sorted = nx.DiGraph()
        G_sorted.add_nodes_from(sorted_nodes)
        G_sorted.add_edges_from(G.edges())

        # create a new directory "RRG_{V}_{D}" and enter it
        directory = f"/users/ziyzhang/topology-research/nexullance/handover_data/RRG_{V}_{D}"
        os.mkdir(directory)


        # Write GraphML with explicit node ordering
        output_file = directory+f"/graph.graphml"
        with open(output_file, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
            f.write('<graph edgedefault="directed">\n')
            # Write nodes in sorted order
            for node in sorted_nodes:
                f.write(f'<node id="{node}"/>\n')
            # Write edges
            for u, v in G_sorted.edges():
                f.write(f'<edge source="{u}" target="{v}"/>\n')
            f.write('</graph>\n')
            f.write('</graphml>\n')

        # write uniform demand matrices:
        Cap_remote = 10 #GBps
        Cap_local = 10 #GBps
        M_EPs = gl.generate_uniform_traffic_pattern(V, EPR)
        # apply simple ECMP:
        ASP, _ = _network.calculate_all_shortest_paths()
        ECMP = gl.ECMP(ASP)
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP, EPR, M_EPs)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        # adapt the traffic scaling factor to 10x saturation
        traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
        M_EPs = traffic_scaling * M_EPs
        M_R = gl.convert_M_EPs_to_M_R(M_EPs, V, EPR)
        # write M_R into a csv file, rounding to 1e-3
        output_file = directory+f"/uniform.txt"
        np.savetxt(output_file, M_R, delimiter=",", fmt="%.3f")


        # write shift demand matrices:
        Cap_remote = 10 #GBps
        Cap_local = 10 #GBps
        M_EPs = gl.generate_shift_traffic_pattern(V, EPR, 1)
        # apply simple ECMP:
        ASP, _ = _network.calculate_all_shortest_paths()
        ECMP = gl.ECMP(ASP)
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP, EPR, M_EPs)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        # adapt the traffic scaling factor to 10x saturation
        traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
        M_EPs = traffic_scaling * M_EPs
        M_R = gl.convert_M_EPs_to_M_R(M_EPs, V, EPR)
        # write M_R into a csv file, rounding to 1e-3
        output_file = directory+f"/shift_1.txt"
        np.savetxt(output_file, M_R, delimiter=",", fmt="%.3f")


        # write shift demand matrices:
        Cap_remote = 10 #GBps
        Cap_local = 10 #GBps
        M_EPs = gl.generate_shift_traffic_pattern(V, EPR, EPR*V//2)
        # apply simple ECMP:
        ASP, _ = _network.calculate_all_shortest_paths()
        ECMP = gl.ECMP(ASP)
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP, EPR, M_EPs)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        # adapt the traffic scaling factor to 10x saturation
        traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
        M_EPs = traffic_scaling * M_EPs
        M_R = gl.convert_M_EPs_to_M_R(M_EPs, V, EPR)
        # write M_R into a csv file, rounding to 1e-3
        output_file = directory+f"/shift_half.txt"
        np.savetxt(output_file, M_R, delimiter=",", fmt="%.3f")



if __name__ == "__main__":
    main()