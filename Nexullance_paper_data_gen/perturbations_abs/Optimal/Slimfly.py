import os
import sys
sys.path.append("/users/ziyzhang/topology-research/")
from topologies.Slimfly import Slimflytopo
import globals as gl
import numpy as np
from Nexullance_paper_data_gen.perturbations.perturbate import perturbate
from nexullance.Nexullance_MP import Nexullance_MP
import csv

Cap_remote = 10 #GBps
Cap_local = 10 #GBps

def main():
    # initialize output data file
    filename = f'Slimfly.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'perturbation_ratio', 'traffic', 'Phi_per_EP', 'min', 'max', 'std'])

        configs = gl.sf_configs
        # configs = gl.sf_configs[:1]
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2
            _network = Slimflytopo(V, D)
            ASP, _ = _network.calculate_all_shortest_paths()
            APST4, _ = _network.calculate_all_paths_within_length(4)
            ECMP_ASP = gl.ECMP(ASP)

            # define a helper function
            def calculate_results(_traffic_pattern, _M_EPs):
                remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, _M_EPs)
                max_remote_link_load = np.max(remote_link_flows)/Cap_remote
                max_local_link_load = np.max(local_link_flows)/Cap_local
                # adapt the traffic scaling factor to 10x saturation
                traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
                _M_EPs = traffic_scaling * _M_EPs
                remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, _M_EPs)
                max_remote_link_load = np.max(remote_link_flows)/Cap_remote
                max_local_link_load = np.max(local_link_flows)/Cap_local

                nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(_M_EPs, V, EPR), Cap_remote, 0, False)
                nexu.init_model()
                max_remote_link_load, _ = nexu.solve()
                # write data without perturbation
                Phi=gl.network_total_throughput(_M_EPs, max_remote_link_load, max_local_link_load)
                csvwriter.writerow([V, D, EPR, 0.0, _traffic_pattern, Phi/(V*EPR), 
                                    Phi/(V*EPR), Phi/(V*EPR), 0.0])
                csvfile.flush()
                # perturbation_ratio from 0.0% to 10% in steps of 1.0%
                for perturbation_ratio in np.arange(0.01, 0.1, 0.01):
                    num_repetitions = 10
                    Phis = []
                    # repeat for 10 times and take the average
                    for i in range(num_repetitions):
                        # generate perturbed demand matrix:
                        perturbed_M_EPs = perturbate(_M_EPs, perturbation_ratio)
                        _, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, perturbed_M_EPs)
                        max_local_link_load = np.max(local_link_flows)/Cap_local
                        # apply routing algorithm here:
                        nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(perturbed_M_EPs, V, EPR), Cap_remote, 0, False)
                        nexu.init_model()
                        max_remote_link_load, _ = nexu.solve()
                        Phi=gl.network_total_throughput(perturbed_M_EPs, max_remote_link_load, max_local_link_load)
                        Phis.append(Phi/(V*EPR))
                    csvwriter.writerow([V, D, EPR, perturbation_ratio, _traffic_pattern, np.average(Phis), 
                                        np.min(Phis), np.max(Phis), np.std(Phis)])
                    csvfile.flush()

            traffic_pattern = "uniform"
            M_EPs = gl.generate_uniform_traffic_pattern(V, EPR)
            calculate_results(traffic_pattern, M_EPs)

            traffic_pattern = "nearst-neighbour"
            M_EPs = gl.generate_diagonal_traffic_pattern(V, EPR, 1)
            calculate_results(traffic_pattern, M_EPs)

            traffic_pattern = "shift_1"
            M_EPs = gl.generate_shift_traffic_pattern(V, EPR, 1)
            calculate_results(traffic_pattern, M_EPs)

            traffic_pattern = "shift_half"
            M_EPs = gl.generate_half_shift_traffic_pattern(V, EPR)
            calculate_results(traffic_pattern, M_EPs)

            traffic_pattern = "router-cluster"
            M_EPs = gl.generate_uniform_cluster_pattern(V, EPR, 4) # four clusters
            calculate_results(traffic_pattern, M_EPs)

            traffic_pattern = "random-permute"
            M_EPs = gl.generate_random_permutation_pattern(V, EPR, 0)
            calculate_results(traffic_pattern, M_EPs)


if __name__ == '__main__':
    main()
