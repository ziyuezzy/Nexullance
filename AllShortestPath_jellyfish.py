import matplotlib.pyplot as plt
import networkx as nx
import topologies.Equality as Equality
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
from globals import *
from statistics import mean
import pickle

#slimfly configurations:
jf_configs= [(722, 28), (800,31), (900,32), (1058, 34)]

jf_results={}
for config in jf_configs:
    jf_network=RRG.RRGtopo(config[1], config[0])
    jf_diameter=jf_network.calculate_diameter()
    jf_all_shortest_paths_dict=jf_network.calculate_all_shortest_paths()

    jf_average_path_lengths=list(calculate_average_path_distribution(jf_all_shortest_paths_dict).values())
    jf_average_path_length_min=min(jf_average_path_lengths)
    jf_average_path_length_max=max(jf_average_path_lengths)
    jf_average_path_length_mean=mean(jf_average_path_lengths)

    jf_load_dict=list(jf_network.distribute_uniform_flow_on_paths(jf_all_shortest_paths_dict).values())
    jf_load_min=min(jf_load_dict)
    jf_load_max=max(jf_load_dict)
    jf_load_mean=mean(jf_load_dict)

    jf_results[config]={ 
        "diameter": jf_diameter, 
        "ave_path_length_statistics": [jf_average_path_length_min, jf_average_path_length_mean, jf_average_path_length_max],
        "link_load_statistics": [jf_load_min, jf_load_mean, jf_load_max]
        }
    
pickle.dump(jf_results, open('./pickled_data/all_shortest_paths_jellyfish.pickle', 'wb'))
