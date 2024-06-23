# first, try to compute ECMP_ASP for different sizes of DDF under a set of
# traffic demand matrices, then compare "Network throughput per EP"

# Then, calculate the average and standard deviation of the "Network throughput" 
# for different sizes of DDF under the same set of traffic demand matrices.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.Slimfly import Slimflytopo
import globals as gl
import numpy as np
import csv

# add the path to the Nexullance_IT c++ library
sys.path.append("/users/ziyzhang/topology-research/nexullance/IT_boost/build")
from Nexullance_IT_cpp import Nexullance_IT_interface

Cap_remote = 10 #GBps
Cap_local = 10 #GBps

def main():
    # initialize output data file
    filename = f'Slimfly.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'Phi', 'Phi_per_EP', 'i_conv'])

        configs = gl.sf_configs
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2

            _network = Slimflytopo(V, D)
            arcs = _network.generate_graph_arcs()
            ASP, _ = _network.calculate_all_shortest_paths()
            ECMP_ASP = gl.ECMP(ASP)


            def run_for_traffic_pattern(_traffic_pattern, _M_EPs):
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
                nexu_it = Nexullance_IT_interface(V, arcs, gl.convert_M_EPs_to_M_R(_M_EPs, V, EPR), False)
                nexu_it.set_parameters(0.11096655960689972, 8.72157628168244)
                nexu_it.run()
                Lremote_NEXU = nexu_it.get_max_link_load()

                Phi = gl.network_total_throughput(_M_EPs, Lremote_NEXU, max_local_link_load)
                csvwriter.writerow([V, D, EPR, _traffic_pattern, Phi, Phi/(V*EPR), nexu_it.get_num_attempts_step_2()])
                csvfile.flush()

            traffic_pattern = "uniform"
            M_EPs = gl.generate_uniform_traffic_pattern(V, EPR)
            run_for_traffic_pattern(traffic_pattern, M_EPs)

            traffic_pattern = "nearst-neighbour"
            M_EPs = gl.generate_diagonal_traffic_pattern(V, EPR, 1)
            run_for_traffic_pattern(traffic_pattern, M_EPs)

            traffic_pattern = "shift_1"
            M_EPs = gl.generate_shift_traffic_pattern(V, EPR, 1)
            run_for_traffic_pattern(traffic_pattern, M_EPs)

            traffic_pattern = "shift_half"
            M_EPs = gl.generate_half_shift_traffic_pattern(V, EPR)
            run_for_traffic_pattern(traffic_pattern, M_EPs)

            traffic_pattern = "router-cluster"
            M_EPs = gl.generate_uniform_cluster_pattern(V, EPR, 4) # four clusters
            run_for_traffic_pattern(traffic_pattern, M_EPs)

            traffic_pattern = "random-permute"
            M_EPs = gl.generate_random_permutation_pattern(V, EPR, 0)
            run_for_traffic_pattern(traffic_pattern, M_EPs)



if __name__ == '__main__':
    main()
