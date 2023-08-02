from globals import *
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
import topologies.Equality as Equality
import topologies.GDBG as GDBG
import topologies.fake_GDBG as fake_GDBG
import pickle

# try: 
#     topo_name='jellyfish'
#     for config in jf_configs:
#         edgelist=pickle.load(open(f'pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'rb'))
#         _network = RRG.RRGtopo(edgelist)
#         _result, _graph, paths_dict =calculate_data_shortest_paths(_network, config)
#         print(f"calculation done for {topo_name} {config}")
#         pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
#         # pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
#         pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for rrg")

# try:
#     topo_name='slimfly'
#     for config in sf_configs:
#         _network=Slimfly.Slimflytopo(config)
#         _result, _graph, paths_dict =calculate_data_shortest_paths(_network, config)
#         print(f"calculation done for {topo_name} {config}")
#         pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
#         # pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
#         pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for sf")


# try:
#     topo_name='equality'
#     _results={}
#     for config in eq_configs:
#         _network=Equality.Equalitytopo(config[0], config[1], config[2], config[3])
#         _result, _graph, paths_dict =calculate_data_shortest_paths(_network, config[4])
#         print(f"calculation done for {topo_name} {config[4]}")
#         pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config[4]}_{topo_name}_uniform_flow.pickle', 'wb'))
#         # pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config[4]}_{topo_name}_edgelist.pickle', 'wb'))
#         pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config[4]}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for eq")


# try:
#     topo_name='fake_gdbg'
#     for config in fake_gdbg_configs:
#         _network=fake_GDBG.fakeGDBGtopo(config[0], config[1])
#         _result, _graph, paths_dict =calculate_data_paths_within_length(_network, config, 2)
#         print(f"calculation done for {topo_name} {config}")
#         pickle.dump(_result, open(f'./pickled_data/statistics/ALLPATH_2_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
#         pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
#         pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/ALLPATH_2_{config}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for fake_gdbg")

# # try:
# topo_name='gdbg'
# for config in fake_gdbg_configs:
#     _network=GDBG.GDBG_topo(config[0], config[1])
#     _result, _graph, paths_dict =calculate_data_paths_within_length(_network, config, 2)
#     print(f"calculation done for {topo_name} {config}")
#     pickle.dump(_result, open(f'./pickled_data/statistics/ALLPATH_2_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
#     pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
#     pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/ALLPATH_2_{config}_{topo_name}_paths.pickle', 'wb'))
# # except:
# #     print("An exception occurred for gdbg")

# try:
topo_name='fake_gdbg'
for config in fake_gdbg_configs:
    _network=fake_GDBG.fakeGDBGtopo(config[0], config[1])
    _result, _graph, paths_dict =calculate_data_shortest_paths(_network, config)
    print(f"calculation done for {topo_name} {config}")
    pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
    # pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
    pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for fake_gdbg")

# try:
topo_name='gdbg'
for config in fake_gdbg_configs:
    _network=GDBG.GDBG_topo(config[0], config[1])
    _result, _graph, paths_dict =calculate_data_shortest_paths(_network, config)
    print(f"calculation done for {topo_name} {config}")
    pickle.dump(_result, open(f'./pickled_data/statistics/all_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
    # pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
    pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
# except:
#     print("An exception occurred for gdbg")

# # 8-shortest path routing for RRG
# # try: 
# topo_name='jellyfish'
# k=8
# for config in jf_configs:
#     edgelist=pickle.load(open(f'pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'rb'))
#     _network = RRG.RRGtopo(edgelist)
#     _result, _graph, paths_dict =calculate_data_k_shortest_paths(_network, config, k)
#     print(f"calculation done for {topo_name} {config}")
#     pickle.dump(_result, open(f'./pickled_data/statistics/8_shortest_paths_{config}_{topo_name}_uniform_flow.pickle', 'wb'))
#     # pickle.dump(_graph, open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'wb'))
#     pickle.dump(paths_dict, open(f'./pickled_data/graphs_and_paths/8_shortest_paths_{config}_{topo_name}_paths.pickle', 'wb'))
# # except:
# #     print("An exception occurred for rrg")