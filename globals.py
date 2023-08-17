from statistics import mean

#Configurations:
#slimfly configurations:
# sf_configs= [722]
sf_configs= [(722, 29), (1058, 35)]
#jellyfish configurations:
jf_configs =  [(722, 29), (900,32), (1058, 35)]
#GDBG configurations, the degree is doubled because it is a directed graph: 
gdbg_configs = [(722, 29), (900,32), (1058, 35)]
#Equality configurations:
eq_configs= [ # Note that E443 config is fault on the equality paper, so here it is commented out
# (800, 31, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E443"),
(900, 32, [-1, 1, 23, 25, 55, 121, 135, 165, 177, 333, 457, 475, 495, 543, 549, 557, 585, 615, 717, 727], [70, 130, 194, 256, 320, 360], "E441"),
(1000, 33, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E442")
]
ddf_configs=[(264, 11), (876, 17), (1386, 20)]

def process_path_dict(path_dict):
    # input is a path dictionary
    average_path_lengths=[]
    num_paths=[]

    for _, paths in path_dict.items():
        average_length=0
        for path in paths:
            average_length+=(len(path)-1)
        average_length/=len(paths)
        average_path_lengths.append(average_length)
        num_paths.append(len(paths))
    # Calculate the average path length of all s-d pairs, 
    # The output is a dictionary of average path lengths
    return average_path_lengths, num_paths

def is_disjoint(path1, path2):
    # Function to check if two paths are edge-disjoint
    edges1 = [(path1[i], path1[i + 1]) for i in range(len(path1) - 1)]
    edges2 = [(path2[i], path2[i + 1]) for i in range(len(path2) - 1)]

    return not any(edge in edges2 for edge in edges1)

def count_disjoint_paths(paths_dict):
    disjoint_paths_count = []
    disjoint_paths_ratio = []
    for (s, d), paths in paths_dict.items():
        count = 0
        for i in range(len(paths)):
            is_disjoint_path = True
            for j in range(i + 1, len(paths)):
                if not is_disjoint(paths[i], paths[j]):
                    is_disjoint_path = False
                    break
            if is_disjoint_path:
                count += 1
        disjoint_paths_ratio.append(count/len(paths))
        disjoint_paths_count.append(count)
    return disjoint_paths_count, disjoint_paths_ratio



def calculate_data_shortest_paths(topology_instance, config):
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.calculate_all_shortest_paths()

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with shortest paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict


def calculate_DDF_routing(topology_instance, config):
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.DDF_unipath_routing()

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with shortest paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict


def calculate_data_k_shortest_paths(topology_instance, config, k):
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.calculate_all_k_shortest_paths(k)

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with {k} shortest paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict


def calculate_data_paths_within_length(topology_instance, config, max_path_length):
    _diameter=topology_instance.calculate_diameter()
    if (_diameter > max_path_length):
        print(f"ERROR: diameter bigger than max path length")
    paths_dict=topology_instance.calculate_all_paths_within_length_parallel(max_path_length)

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with shortest paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict
