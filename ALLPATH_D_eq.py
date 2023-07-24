import matplotlib.pyplot as plt
import networkx as nx
import topologies.Equality as Equality
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
from globals import *
from statistics import mean
import pickle

# Equality networks: E441, E442, E443
eq_configs= [
(900, 32, [-1, 1, 23, 25, 55, 121, 135, 165, 177, 333, 457, 475, 495, 543, 549, 557, 585, 615, 717, 727], [70, 130, 194, 256, 320, 360], "E441"),
]

_results={}
for config in eq_configs:
    _network=Equality.Equalitytopo(config[0], config[1], config[2], config[3])
    _diameter=_network.calculate_diameter()
    _allpath_D_dict=_network.calculate_all_paths_within_length_parallel(_diameter)

    _average_path_lengths=list(calculate_average_path_distribution(_allpath_D_dict).values())
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)

    _load_dict=list(_network.distribute_uniform_flow_on_paths(_allpath_D_dict).values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    _results[config[4]]={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max]
        }
    
pickle.dump(_results, open('./pickled_data/ALLPATH_D_equality.pickle', 'wb'))
