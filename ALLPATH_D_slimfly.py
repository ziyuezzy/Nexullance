import matplotlib.pyplot as plt
import networkx as nx
import topologies.Equality as Equality
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
from globals import *
from statistics import mean
import pickle

#slimfly configurations:
# _configs= [722]
sf_configs= [722, 1058]

_results={}
for config in sf_configs:
    _network=Slimfly.Slimflytopo(config)
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
    
pickle.dump(_results, open('./pickled_data/ALLPATH_D_slimfly.pickle', 'wb'))

# #jellyfish configurations:
# jf_configs= [(722, 28), (800,31), (900,32), (1058, 34)]

# _results={}
# for config in jf_configs:
#     _network=RRG.RRGtopo(config[1], config[0])
#     _diameter=_network.calculate_diameter()
#     _allpath_D_dict=_network.calculate_all_paths_within_length_parallel(_diameter)

#     _average_path_lengths=list(calculate_average_path_distribution(_allpath_D_dict).values())
#     _average_path_length_min=min(_average_path_lengths)
#     _average_path_length_max=max(_average_path_lengths)
#     _average_path_length_mean=mean(_average_path_lengths)

#     _load_dict=list(_network.distribute_flow_on_paths(_allpath_D_dict).values())
#     _load_min=min(_load_dict)
#     _load_max=max(_load_dict)
#     _load_mean=mean(_load_dict)

#     _results[config]={ 
#         "diameter": _diameter, 
#         "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
#         "link_load_statistics": [_load_min, _load_mean, _load_max]
#         }
    
# pickle.dump(_results, open('./pickled_data/ALLPATH_D_jellyfish.pickle', 'wb'))

# # Equality networks: E441, E442, E443
# eq_configs= [ # Note that E443 config is fault on the equality paper, so here it is commented out
# # (800, 31, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E443"),
# (900, 32, [-1, 1, 23, 25, 55, 121, 135, 165, 177, 333, 457, 475, 495, 543, 549, 557, 585, 615, 717, 727], [70, 130, 194, 256, 320, 360], "E441"),
# (1000, 33, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E442")
# ]

# _results={}
# for config in eq_configs:
#     _network=Equality.Equalitytopo(config[0], config[1], config[2], config[3])
#     _diameter=_network.calculate_diameter()
#     _allpath_D_dict=_network.calculate_all_paths_within_length_parallel(_diameter)

#     _average_path_lengths=list(calculate_average_path_distribution(_allpath_D_dict).values())
#     _average_path_length_min=min(_average_path_lengths)
#     _average_path_length_max=max(_average_path_lengths)
#     _average_path_length_mean=mean(_average_path_lengths)

#     _load_dict=list(_network.distribute_flow_on_paths(_allpath_D_dict).values())
#     _load_min=min(_load_dict)
#     _load_max=max(_load_dict)
#     _load_mean=mean(_load_dict)

#     _results[config[4]]={ 
#         "diameter": _diameter, 
#         "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
#         "link_load_statistics": [_load_min, _load_mean, _load_max]
#         }
    
# pickle.dump(_results, open('./pickled_data/ALLPATH_D_equality.pickle', 'wb'))
