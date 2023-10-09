import topologies.DDF as DDF
import globals as gl
import nexullance.LP_gurobi as LP
from statistics import mean

#NUM_EXPERIMENTS=10

config=(114, 8)
EPR=6
topo='ddf'
_network=DDF.DDFtopo(config[0], config[1])
# TODO: define traffic pattern
_traffic_matrix=gl.generate_uniform_traffic_pattern(config[0], EPR)
R2R_traffic_matrix=gl.convert_p2p_traffic_matrix_to_R2R(_traffic_matrix, config[0], EPR)

# print(f'==========results without any link failure:============')
# # without any link failure
# _result, edge_list, path_dict=gl.calculate_data_shortest_paths(_network, config)
# # display(_result)
# link_loads, local_link_load=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, _traffic_matrix)
# print(f'predicted saturation load = {local_link_load/max(link_loads)}')
# # display(paths_dict)
# all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_traffic_matrix, _verbose=0)
# link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, _traffic_matrix)
# print(f'predicted saturation load LP = {local_link_load/max(link_loads)}')


# link_failure_ratio_list=[0.000, 0.002, 0.004, 0.006, 0.008, 0.010]

# link_failure_ratio_list=[0.015, 0.020, 0.025, 0.030, 0.035, 0.040]

link_failure_ratio_list=[0.05, 0.10, 0.15, 0.20, 0.25]
for link_failure_ratio in link_failure_ratio_list:
    print(f'==========results for random link failure_ratio={link_failure_ratio} ============')
    diameter=[]
    average_path_length=[]
    average_path_diversity=[]
    predicted_saturation_load=[]

    LP_ASP_saturation_load=[]
    LP_ASP_average_path_length=[]
    LP_ASP_average_path_diversity=[]

    LP_ASTP_3_saturation_load=[]
    LP_ASTP_3_average_path_length=[]
    LP_ASTP_3_average_path_diversity=[]

    LP_ASTP_4_saturation_load=[]
    LP_ASTP_4_average_path_length=[]
    LP_ASTP_4_average_path_diversity=[]

    LP_4_SP_saturation_load=[]
    LP_4_SP_average_path_length=[]
    LP_4_SP_average_path_diversity=[]

    if link_failure_ratio>0:
        NUM_EXPERIMENTS=10
    else:
        NUM_EXPERIMENTS=1
    for seed in range(NUM_EXPERIMENTS):
        # set link failures
        _network=DDF.DDFtopo(config[0], config[1]) #reset network
        _network.set_random_link_failures(link_failure_ratio, seed)
        # display(list(_network.nx_graph.edges()))
        _result, edge_list, path_dict=gl.calculate_data_shortest_paths(_network, config)
        diameter.append(_result['diameter'])
        average_path_length.append(_result['ave_path_length_statistics'][1])
        average_path_diversity.append(_result['num_paths_statistics'][1])
        link_loads, local_link_load=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, _traffic_matrix)
        predicted_saturation_load.append(local_link_load/max(link_loads))

        all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_traffic_matrix, _verbose=0)
        link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, _traffic_matrix)
        average_path_lengths, num_paths=gl.process_weighted_path_dict(all_weighted_paths)
        LP_ASP_saturation_load.append(local_link_load/max(link_loads))
        LP_ASP_average_path_length.append(mean(average_path_lengths))
        LP_ASP_average_path_diversity.append(mean(num_paths))
        print(f'With seed = {seed}, network diameter = {diameter[seed]}')
        print('ASP :')
        print(f'With seed = {seed}, average path length = {average_path_length[seed]}')
        print(f'With seed = {seed}, average path diversity = {average_path_diversity[seed]}')
        print(f'With seed = {seed}, predicted saturation load = {predicted_saturation_load[seed]}')
        print('LP-ASP :')
        print(f'With seed = {seed}, average path length = {LP_ASP_average_path_length[seed]}')
        print(f'With seed = {seed}, average path diversity = {LP_ASP_average_path_diversity[seed]}')
        print(f'With seed = {seed}, predicted saturation load = {LP_ASP_saturation_load[seed]}')

        if diameter[seed]<=3:
            _, edge_list, path_dict=gl.calculate_data_paths_within_length(_network, config, 3)
            all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_traffic_matrix, _verbose=0)
            link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, _traffic_matrix)
            average_path_lengths, num_paths=gl.process_weighted_path_dict(all_weighted_paths)
            LP_ASTP_3_saturation_load.append(local_link_load/max(link_loads))
            LP_ASTP_3_average_path_length.append(mean(average_path_lengths))
            LP_ASTP_3_average_path_diversity.append(mean(num_paths))
            print('LP-ASTP-3:')
            print(f'With seed = {seed}, average path length = {LP_ASTP_3_average_path_length[-1]}')
            print(f'With seed = {seed}, average path diversity = {LP_ASTP_3_average_path_diversity[-1]}')
            print(f'With seed = {seed}, predicted saturation load = {LP_ASTP_3_saturation_load[-1]}')
        else:
            print("network diameter is smaller than 3, ASTP-3 is skipped")

        if diameter[seed]<=4:
            _, edge_list, path_dict=gl.calculate_data_paths_within_length(_network, config, 4)
            all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_traffic_matrix, _verbose=0)
            link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, _traffic_matrix)
            average_path_lengths, num_paths=gl.process_weighted_path_dict(all_weighted_paths)
            LP_ASTP_4_saturation_load.append(local_link_load/max(link_loads))
            LP_ASTP_4_average_path_length.append(mean(average_path_lengths))
            LP_ASTP_4_average_path_diversity.append(mean(num_paths))
            print('LP-ASTP-4:')
            print(f'With seed = {seed}, average path length = {LP_ASTP_4_average_path_length[-1]}')
            print(f'With seed = {seed}, average path diversity = {LP_ASTP_4_average_path_diversity[-1]}')
            print(f'With seed = {seed}, predicted saturation load = {LP_ASTP_4_saturation_load[-1]}')
        else:
            print("network diameter is smaller than 4, ASTP-4 is skipped")

        _, _, path_dict=gl.calculate_data_k_shortest_paths(_network, config, 4)
        all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_traffic_matrix, _verbose=0)
        link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, _traffic_matrix)
        average_path_lengths, num_paths=gl.process_weighted_path_dict(all_weighted_paths)
        LP_4_SP_saturation_load.append(local_link_load/max(link_loads))
        LP_4_SP_average_path_length.append(mean(average_path_lengths))
        LP_4_SP_average_path_diversity.append(mean(num_paths))
        print('LP-4-SP:')
        print(f'With seed = {seed}, average path length = {LP_4_SP_average_path_length[-1]}')
        print(f'With seed = {seed}, average path diversity = {LP_4_SP_average_path_diversity[-1]}')
        print(f'With seed = {seed}, predicted saturation load = {LP_4_SP_saturation_load[-1]}')

    print('Summarizing, ASP :')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path length = ({min(average_path_length)}, \n {mean(average_path_length)}, \n {max(average_path_length)})')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path diversity = ({min(average_path_diversity)}, \n {mean(average_path_diversity)}, \n {max(average_path_diversity)})')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) predicted saturation = ({min(predicted_saturation_load)}, \n {mean(predicted_saturation_load)}, \n {max(predicted_saturation_load)})')
    print('Summarizing, LP-ASP :')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path length = ({min(LP_ASP_average_path_length)}, \n {mean(LP_ASP_average_path_length)}, \n {max(LP_ASP_average_path_length)})')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path diversity = ({min(LP_ASP_average_path_diversity)}, \n {mean(LP_ASP_average_path_diversity)}, \n {max(LP_ASP_average_path_diversity)})')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) predicted saturation = ({min(LP_ASP_saturation_load)}, \n {mean(LP_ASP_saturation_load)}, \n {max(LP_ASP_saturation_load)})')

    if LP_ASTP_3_saturation_load:
        print('Summarizing, LP-ASTP-3:')
        print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path length = ({min(LP_ASTP_3_average_path_length)}, \n {mean(LP_ASTP_3_average_path_length)}, \n {max(LP_ASTP_3_average_path_length)})')
        print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path diversity = ({min(LP_ASTP_3_average_path_diversity)}, \n {mean(LP_ASTP_3_average_path_diversity)}, \n {max(LP_ASTP_3_average_path_diversity)})')
        print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) predicted saturation = ({min(LP_ASTP_3_saturation_load)}, \n {mean(LP_ASTP_3_saturation_load)}, \n {max(LP_ASTP_3_saturation_load)})')

    if LP_ASTP_4_saturation_load:
        print('Summarizing, LP-ASTP-4:')
        print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path length = ({min(LP_ASTP_4_average_path_length)}, \n {mean(LP_ASTP_4_average_path_length)}, \n {max(LP_ASTP_4_average_path_length)})')
        print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path diversity = ({min(LP_ASTP_4_average_path_diversity)}, \n {mean(LP_ASTP_4_average_path_diversity)}, \n {max(LP_ASTP_4_average_path_diversity)})')
        print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) predicted saturation = ({min(LP_ASTP_4_saturation_load)}, \n {mean(LP_ASTP_4_saturation_load)}, \n {max(LP_ASTP_4_saturation_load)})')

    print('Summarizing, LP-4-SP:')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path length = ({min(LP_4_SP_average_path_length)}, \n {mean(LP_4_SP_average_path_length)}, \n {max(LP_4_SP_average_path_length)})')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) average path diversity = ({min(LP_4_SP_average_path_diversity)}, \n {mean(LP_4_SP_average_path_diversity)}, \n {max(LP_4_SP_average_path_diversity)})')
    print(f'Across {NUM_EXPERIMENTS} seeds, (min, ave, max) predicted saturation = ({min(LP_4_SP_saturation_load)}, \n {mean(LP_4_SP_saturation_load)}, \n {max(LP_4_SP_saturation_load)})')
