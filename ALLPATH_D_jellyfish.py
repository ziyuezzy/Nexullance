import matplotlib.pyplot as plt
import networkx as nx
import topologies.Equality as Equality
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
from globals import *
from statistics import mean
import pickle

#jellyfish configurations:
jf_configs= [(722, 28), (800,31), (900,32), (1058, 34)]

_results={}
for config in jf_configs:
    _network=RRG.RRGtopo(config[1], config[0])
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

    _results[config]={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max]
        }
    print(f"calculation done for {config}")
    
pickle.dump(_results, open('./pickled_data/ALLPATH_D_jellyfish.pickle', 'wb'))