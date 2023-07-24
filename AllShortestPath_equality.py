import matplotlib.pyplot as plt
import networkx as nx
import topologies.Equality as Equality
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
from globals import *
from statistics import mean
import pickle

# Equality networks: E441, E442, E443
eq_configs= [ # Note that E443 config is fault on the equality paper, so here it is commented out
# (800, 31, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E443"),
(900, 32, [-1, 1, 23, 25, 55, 121, 135, 165, 177, 333, 457, 475, 495, 543, 549, 557, 585, 615, 717, 727], [70, 130, 194, 256, 320, 360], "E441"),
(1000, 33, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E442")
]

eq_results={}
for config in eq_configs:
    eq_network=Equality.Equalitytopo(config[0], config[1], config[2], config[3])
    eq_diameter=eq_network.calculate_diameter()
    eq_all_shortest_paths_dict=eq_network.calculate_all_shortest_paths()

    eq_average_path_lengths=list(calculate_average_path_distribution(eq_all_shortest_paths_dict).values())
    eq_average_path_length_min=min(eq_average_path_lengths)
    eq_average_path_length_max=max(eq_average_path_lengths)
    eq_average_path_length_mean=mean(eq_average_path_lengths)

    eq_load_dict=list(eq_network.distribute_uniform_flow_on_paths(eq_all_shortest_paths_dict).values())
    eq_load_min=min(eq_load_dict)
    eq_load_max=max(eq_load_dict)
    eq_load_mean=mean(eq_load_dict)

    eq_results[config[4]]={ 
        "diameter": eq_diameter, 
        "ave_path_length_statistics": [eq_average_path_length_min, eq_average_path_length_mean, eq_average_path_length_max],
        "link_load_statistics": [eq_load_min, eq_load_mean, eq_load_max]
        }
    
pickle.dump(eq_results, open('./pickled_data/all_shortest_paths_equality.pickle', 'wb'))
