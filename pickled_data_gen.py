from topologies.HPC_topo import HPC_topo
from topologies.DDF import DDFtopo
from topologies.Slimfly import Slimflytopo
from topologies.Equality import Equalitytopo
from topologies.RRG import RRGtopo
import pickle
import os

graph_data_path = os.environ.get('PICKLED_DATA')
## run this to know which topology classes are available
# HPC_topo.get_child_classes()

# create an instance of network topology
topo_name="RRGtopo"
topo_config=(4, 3)
topo_instance=HPC_topo.initialize_child_instance(topo_name, topo_config[0], topo_config[1])
edge_list=list(topo_instance.nx_graph.edges())
edgelist_file=graph_data_path+f"/from_graph_edgelists/({topo_config[0]},{topo_config[1]}){topo_name}_edgelist.pickle"
with open(edgelist_file, 'wb') as handle:
    pickle.dump(edge_list, handle)

path_dict, routing_name=topo_instance.calculate_all_shortest_paths()
pathdict_file=graph_data_path+f"/from_graph_pathdicts/{routing_name}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"
with open(pathdict_file, 'wb') as handle:
    pickle.dump(path_dict, handle)
    
path_dict, routing_name=topo_instance.calculate_all_paths_within_length(4)
pathdict_file=graph_data_path+f"/from_graph_pathdicts/{routing_name}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"
with open(pathdict_file, 'wb') as handle:
    pickle.dump(path_dict, handle)