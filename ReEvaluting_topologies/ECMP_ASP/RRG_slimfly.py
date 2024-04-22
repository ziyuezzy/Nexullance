# TODO: first, try to compute ECMP_ASP for different sizes of DDF under a set of
# traffic demand matrices, then compare "Network throughput per EP"

# Then, calculate the average and standard deviation of the "Network throughput" 
# for different sizes of DDF under the same set of traffic demand matrices.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
import globals as gl
import numpy as np
import csv


Cap_remote = 10 #GBps
Cap_local = 10 #GBps

def main():
    # initialize output data file
    filename = f'RRG.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'Phi', 'Phi_per_EP'])

        configs = [(18, 5), (32, 6), (50, 7), (98, 11), (128, 12), (162, 13), (242, 17)]
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2
            traffic_pattern = "uniform"
            M_EPs = gl.generate_uniform_traffic_pattern(V, EPR)

            _network = RRGtopo(V, D)
            ASP, _ = _network.calculate_all_shortest_paths()
            ECMP_ASP = gl.ECMP(ASP)

            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 1x saturation
            traffic_scaling = 1.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            Phi=gl.network_total_throughput(M_EPs, max_remote_link_load, max_local_link_load)

            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()

if __name__ == '__main__':
    main()
