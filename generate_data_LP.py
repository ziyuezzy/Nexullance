from globals import *
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
import topologies.Equality as Equality
import topologies.GDBG as GDBG
import topologies.fake_GDBG as fake_GDBG
import topologies.DDF as DDF
import pickle
import lp_load_balancing.LP_cvspy as LP_cvspy

topo_name='jellyfish'
for config in jf_configs:
    _network = RRG.RRGtopo(config[0], config[1])
    _result, _graph, paths_dict, LP_paths_dict =calculate_data_shortest_paths_with_LP(_network, config)
    print(f"calculation done for {topo_name} {config}")
    pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
    pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
    pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
    pickle.dump(LP_paths_dict, open(f'./pickled_data/graphs_and_paths/LP_weighted_all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))


topo_name='slimfly'
for config in sf_configs:
    _network=Slimfly.Slimflytopo(config[0], config[1])
    _result, _graph, paths_dict, LP_paths_dict =calculate_data_shortest_paths_with_LP(_network, config)
    print(f"calculation done for {topo_name} {config}")
    pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
    pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
    pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
    pickle.dump(LP_paths_dict, open(f'./pickled_data/graphs_and_paths/LP_weighted_all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))

# try:
topo_name='equality'
for config in eq_configs:
    _network=Equality.Equalitytopo(config[0], config[1], config[2], config[3])
    _result, _graph, paths_dict, LP_paths_dict =calculate_data_shortest_paths_with_LP(_network, config)
    print(f"calculation done for {topo_name} {config}")
    pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
    pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
    pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
    pickle.dump(LP_paths_dict, open(f'./pickled_data/graphs_and_paths/LP_weighted_all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for eq")
