import matplotlib.pyplot as plt
import networkx as nx
import topologies.Equality as Equality
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
from globals import *
from statistics import mean
import pickle

#slimfly configurations:
# sf_configs= [722]
sf_configs= [722, 1058]

sf_results={}
for config in sf_configs:
    sf_network=Slimfly.Slimflytopo(config)
    sf_diameter=sf_network.calculate_diameter()
    sf_all_shortest_paths_dict=sf_network.calculate_all_shortest_paths()

    sf_average_path_lengths=list(calculate_average_path_distribution(sf_all_shortest_paths_dict).values())
    sf_average_path_length_min=min(sf_average_path_lengths)
    sf_average_path_length_max=max(sf_average_path_lengths)
    sf_average_path_length_mean=mean(sf_average_path_lengths)

    sf_load_dict=list(sf_network.distribute_uniform_flow_on_paths(sf_all_shortest_paths_dict).values())
    sf_load_min=min(sf_load_dict)
    sf_load_max=max(sf_load_dict)
    sf_load_mean=mean(sf_load_dict)

    sf_results[config]={ 
        "diameter": sf_diameter, 
        "ave_path_length_statistics": [sf_average_path_length_min, sf_average_path_length_mean, sf_average_path_length_max],
        "link_load_statistics": [sf_load_min, sf_load_mean, sf_load_max]
        }
    
pickle.dump(sf_results, open('./pickled_data/all_shortest_paths_slimfly.pickle', 'wb'))
