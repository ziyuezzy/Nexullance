import topologies.DDF as DDF
import globals as gl
import lp_load_balancing.LP_gurobi as LP
from statistics import mean

NUM_EXPERIMENTS=10

# config=(264, 11)
config=(114, 8)
EPR=5
topo='ddf'
_network=DDF.DDFtopo(config[0], config[1])
uniform_traffic_matrix=gl.generate_uniform_traffic_pattern(config[0], EPR)
R2R_uniform=gl.convert_p2p_traffic_matrix_to_R2R(uniform_traffic_matrix, config[0], EPR)

print(f'==========results without any link failure:============')
# without any link failure
_result, edge_list, path_dict=gl.calculate_data_shortest_paths(_network, config)
# display(_result)
link_loads, local_link_load=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, uniform_traffic_matrix)
print(f'predicted saturation load = {local_link_load/max(link_loads)}')
# display(paths_dict)
all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_uniform, _verbose=0)
link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, uniform_traffic_matrix)
print(f'predicted saturation load after LP = {local_link_load/max(link_loads)}')


link_failure_ratio=0.01
print(f'==========results for random link failure_ratio={link_failure_ratio} ============')
diameter=[]
average_path_length=[]
average_path_diversity=[]
predicted_saturation_load=[]
LP_saturation_load=[]
for seed in range(NUM_EXPERIMENTS):
    # set link failures
    _network=DDF.DDFtopo(config[0], config[1]) #reset network
    _network.set_random_link_failures(link_failure_ratio, seed)
    # display(list(_network.nx_graph.edges()))
    _result, edge_list, path_dict=gl.calculate_data_shortest_paths(_network, config)
    diameter.append(_result['diameter'])
    average_path_length.append(_result['ave_path_length_statistics'][1])
    average_path_diversity.append(_result['num_paths_statistics'][1])
    link_loads, local_link_load=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, uniform_traffic_matrix)
    predicted_saturation_load.append(local_link_load/max(link_loads))

    all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_uniform, _verbose=0)
    link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, uniform_traffic_matrix)
    LP_saturation_load.append(local_link_load/max(link_loads))

    print(f'With seed = {seed}, average path length = {average_path_length[seed]}')
    print(f'With seed = {seed}, average path diversity = {average_path_diversity[seed]}')
    print(f'With seed = {seed}, predicted saturation load before LP = {predicted_saturation_load[seed]}')
    print(f'With seed = {seed}, predicted saturation load after LP = {LP_saturation_load[seed]}')

print(f'Across 10 seeds, (min, ave, max) average path length = ({min(average_path_length)}, {mean(average_path_length)}, {max(average_path_length)})')
print(f'Across 10 seeds, (min, ave, max) average path diversity = ({min(average_path_diversity)}, {mean(average_path_diversity)}, {max(average_path_diversity)})')
print(f'Across 10 seeds, (min, ave, max) predicted saturation load before LP = ({min(predicted_saturation_load)}, {mean(predicted_saturation_load)}, {max(predicted_saturation_load)})')
print(f'Across 10 seeds, (min, ave, max) predicted saturation load after LP = ({min(LP_saturation_load)}, {mean(LP_saturation_load)}, {max(LP_saturation_load)})')


link_failure_ratio=0.01
print(f'==========results for inter-group link failure_ratio={link_failure_ratio} ============')
diameter=[]
average_path_length=[]
average_path_diversity=[]
predicted_saturation_load=[]
LP_saturation_load=[]
for seed in range(NUM_EXPERIMENTS):
    # set link failures
    _network=DDF.DDFtopo(config[0], config[1]) #reset network
    _network.set_intergroup_link_failures(link_failure_ratio, seed)
    # display(list(_network.nx_graph.edges()))
    _result, edge_list, path_dict=gl.calculate_data_shortest_paths(_network, config)
    diameter.append(_result['diameter'])
    average_path_length.append(_result['ave_path_length_statistics'][1])
    average_path_diversity.append(_result['num_paths_statistics'][1])
    link_loads, local_link_load=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, uniform_traffic_matrix)
    predicted_saturation_load.append(local_link_load/max(link_loads))

    all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_uniform, _verbose=0)
    link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, uniform_traffic_matrix)
    LP_saturation_load.append(local_link_load/max(link_loads))

    print(f'With seed = {seed}, average path length = {average_path_length[seed]}')
    print(f'With seed = {seed}, average path diversity = {average_path_diversity[seed]}')
    print(f'With seed = {seed}, predicted saturation load before LP = {predicted_saturation_load[seed]}')
    print(f'With seed = {seed}, predicted saturation load after LP = {LP_saturation_load[seed]}')

print(f'Across 10 seeds, (min, ave, max) average path length = ({min(average_path_length)}, {mean(average_path_length)}, {max(average_path_length)})')
print(f'Across 10 seeds, (min, ave, max) average path diversity = ({min(average_path_diversity)}, {mean(average_path_diversity)}, {max(average_path_diversity)})')
print(f'Across 10 seeds, (min, ave, max) predicted saturation load before LP = ({min(predicted_saturation_load)}, {mean(predicted_saturation_load)}, {max(predicted_saturation_load)})')
print(f'Across 10 seeds, (min, ave, max) predicted saturation load after LP = ({min(LP_saturation_load)}, {mean(LP_saturation_load)}, {max(LP_saturation_load)})')


link_failure_ratio=0.01
print(f'==========results for intra-group link failure_ratio={link_failure_ratio} ============')
diameter=[]
average_path_length=[]
average_path_diversity=[]
predicted_saturation_load=[]
LP_saturation_load=[]
for seed in range(NUM_EXPERIMENTS):
    # set link failures
    _network=DDF.DDFtopo(config[0], config[1]) #reset network
    _network.set_intragroup_link_failures(link_failure_ratio, seed)
    # display(list(_network.nx_graph.edges()))
    _result, edge_list, path_dict=gl.calculate_data_shortest_paths(_network, config)
    diameter.append(_result['diameter'])
    average_path_length.append(_result['ave_path_length_statistics'][1])
    average_path_diversity.append(_result['num_paths_statistics'][1])
    link_loads, local_link_load=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, uniform_traffic_matrix)
    predicted_saturation_load.append(local_link_load/max(link_loads))

    all_weighted_paths, result_link_loads=LP.Solve_load_balancing(path_dict, edge_list,R2R_uniform, _verbose=0)
    link_loads, local_link_load=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, uniform_traffic_matrix)
    LP_saturation_load.append(local_link_load/max(link_loads))

    print(f'With seed = {seed}, average path length = {average_path_length[seed]}')
    print(f'With seed = {seed}, average path diversity = {average_path_diversity[seed]}')
    print(f'With seed = {seed}, predicted saturation load before LP = {predicted_saturation_load[seed]}')
    print(f'With seed = {seed}, predicted saturation load after LP = {LP_saturation_load[seed]}')

print(f'Across 10 seeds, (min, ave, max) average path length = ({min(average_path_length)}, {mean(average_path_length)}, {max(average_path_length)})')
print(f'Across 10 seeds, (min, ave, max) average path diversity = ({min(average_path_diversity)}, {mean(average_path_diversity)}, {max(average_path_diversity)})')
print(f'Across 10 seeds, (min, ave, max) predicted saturation load before LP = ({min(predicted_saturation_load)}, {mean(predicted_saturation_load)}, {max(predicted_saturation_load)})')
print(f'Across 10 seeds, (min, ave, max) predicted saturation load after LP = ({min(LP_saturation_load)}, {mean(LP_saturation_load)}, {max(LP_saturation_load)})')
