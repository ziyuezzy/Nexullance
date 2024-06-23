import sys
sys.path.append("/users/ziyzhang/topology-research/")
from topologies.DDF import DDFtopo
import globals as gl
import numpy as np
# add the path to the Nexullance_IT c++ library
sys.path.append("/users/ziyzhang/topology-research/nexullance/IT_boost/build")
from Nexullance_IT_cpp import Nexullance_IT_interface
Cap_remote = 10 #GBps
Cap_local = 10 #GBps

config = gl.ddf_configs[-1]
V= config[0]
D= config[1]
EPR = (D+1)//2
_network = DDFtopo(V, D)
arcs = _network.generate_graph_arcs()
ASP, _ = _network.calculate_all_shortest_paths()
ECMP_ASP = gl.ECMP(ASP)

def run_for_traffic_pattern(_arcs, _traffic_pattern, _M_EPs, _alpha, _beta):
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, _M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    _M_EPs = traffic_scaling * _M_EPs
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, _M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # run Nexullance_IT
    nexu_it = Nexullance_IT_interface(V, _arcs, gl.convert_M_EPs_to_M_R(_M_EPs, V, EPR), True)
    nexu_it.set_parameters(_alpha, _beta)
    nexu_it.run()
    Lremote_NEXU = nexu_it.get_max_link_load()
    Phi = gl.network_total_throughput(_M_EPs, Lremote_NEXU, max_local_link_load)
    return Phi/(V*EPR)

traffic_pattern = "router-cluster"
M_EPs = gl.generate_uniform_cluster_pattern(V, EPR, 4) # four clusters
print(f"phi: {run_for_traffic_pattern(arcs, traffic_pattern, M_EPs, 0.1, 7.0)}")