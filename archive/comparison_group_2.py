from globals import *
import topologies.RRG as RRG
import topologies.Slimfly as Slimfly
import topologies.Equality as Equality
# import topologies.GDBG as GDBG
import topologies.DDF as DDF
import pickle

sf_config = (1058, 35)
jf_config =  (1058, 35)
eq_config = (1000, 33, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E442")

sf_edge_list=pickle.load(open(f'pickled_data/graphs_and_paths/(1058, 35)_slimfly_edgelist.pickle', 'rb'))
sf_path_dict=pickle.load(open(f'pickled_data/graphs_and_paths/all_shortest_paths_(1058, 35)_slimfly_paths.pickle', 'rb'))
jf_edge_list=pickle.load(open(f'pickled_data/graphs_and_paths/(1058, 35)_jellyfish_edgelist.pickle', 'rb'))
jf_path_dict=pickle.load(open(f'pickled_data/graphs_and_paths/all_shortest_paths_(1058, 35)_jellyfish_paths.pickle', 'rb'))
eq_edge_list=pickle.load(open(f'pickled_data/graphs_and_paths/E442_equality_edgelist.pickle', 'rb'))
eq_path_dict=pickle.load(open(f'pickled_data/graphs_and_paths/all_shortest_paths_E442_equality_paths.pickle', 'rb'))

sf=Slimfly.Slimflytopo(sf_edge_list)
jf=RRG.RRGtopo(jf_edge_list)
eq=Equality.Equalitytopo(eq_edge_list)

sf_link_occ, sf_local_link_occ, sf_link_load, sf_local_link_load = sf.distribute_uniform_flow_on_paths_with_EP(sf_path_dict, 18)
jf_link_occ, jf_local_link_occ, jf_link_load, jf_local_link_load = jf.distribute_uniform_flow_on_paths_with_EP(jf_path_dict, 18)
eq_link_occ, eq_local_link_occ, eq_link_load, eq_local_link_load = eq.distribute_uniform_flow_on_paths_with_EP(eq_path_dict, 18)

print("sf link occupancy rate (min, ave, max) = {}, {}, {}".format(min(sf_link_occ), mean(sf_link_occ), max(sf_link_occ)))
print("sf local link occupancy rate (min, ave, max) = {}, {}, {}".format(min(sf_local_link_occ), mean(sf_local_link_occ), max(sf_local_link_occ)))
print("sf link load (min, ave, max) = {}, {}, {}".format(min(sf_link_load), mean(sf_link_load), max(sf_link_load)))
print("sf local link load (min, ave, max) = {}, {}, {}".format(min(sf_local_link_load), mean(sf_local_link_load), max(sf_local_link_load)))


print("jf link occupancy rate (min, ave, max) = {}, {}, {}".format(min(jf_link_occ), mean(jf_link_occ), max(jf_link_occ)))
print("jf local link occupancy rate (min, ave, max) = {}, {}, {}".format(min(jf_local_link_occ), mean(jf_local_link_occ), max(jf_local_link_occ)))
print("jf link load (min, ave, max) = {}, {}, {}".format(min(jf_link_load), mean(jf_link_load), max(jf_link_load)))
print("jf local link load (min, ave, max) = {}, {}, {}".format(min(jf_local_link_load), mean(jf_local_link_load), max(jf_local_link_load)))

print("eq link occupancy rate (min, ave, max) = {}, {}, {}".format(min(eq_link_occ), mean(eq_link_occ), max(eq_link_occ)))
print("eq local link occupancy rate (min, ave, max) = {}, {}, {}".format(min(eq_local_link_occ), mean(eq_local_link_occ), max(eq_local_link_occ)))
print("eq link load (min, ave, max) = {}, {}, {}".format(min(eq_link_load), mean(eq_link_load), max(eq_link_load)))
print("eq local link load (min, ave, max) = {}, {}, {}".format(min(eq_local_link_load), mean(eq_local_link_load), max(eq_local_link_load)))