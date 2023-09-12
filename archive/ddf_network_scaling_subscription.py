import globals as gl
import topologies.DDF as DDF
import pickle
import pandas as pd
from statistics import mean
from math import ceil
import matplotlib.pyplot as plt

#DDF
topo_name='ddf'
configs={}
search_min=0  #lower bound of the search
search_max=1400 #upper bound of the search
print(f"Searching for Dally Dragonfly configurations: (num_vertices, k'), Number of routers between {search_min} and {search_max}")
a=0
while 1:
    a+=2
    h=a//2
    p=a//2
    k=a+p+h-1
    g=a*h+1
    R=a*g
    if R<search_min:
        continue
    elif R>search_max:
        break
    else:
        print(f"DDF config found: ({R}, {k-h}), (a={a}, h=p={h}, k={k} g={g}, N={R*p})")
        configs[(R, k-h)]=h


for config, EPs in configs.items():

    edge_list=pickle.load(open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'rb'))
    path_dict=pickle.load(open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'rb'))
    
    _network = DDF.DDFtopo(edge_list)
    _x=list(range(1, 20))
    _y=[]
    for p in _x:
        link_load, local_link_load = _network.distribute_uniform_flow_on_paths_with_EP(path_dict, p)
        predicted_saturation=local_link_load/max(link_load)
        if predicted_saturation>1.0:
            predicted_saturation=1.0
        _y.append(predicted_saturation)
    plt.scatter(_x, _y, label="{}".format(config))
    plt.plot(_x, _y)

plt.xlabel('router subscription')
plt.xticks(_x)
plt.ylabel('predicted saturation offered_load')
plt.title('dally-dragonfly network scaling effect with all-shortest path routing')
plt.ylim([0,1.0])
plt.legend(loc='lower left')

plt.savefig('ddf_scaling_all_shortest_paths.png')


plt.clf()

for config, EPs in configs.items():

    edge_list=pickle.load(open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'rb'))
    path_dict=pickle.load(open(f'./pickled_data/graphs_and_paths/unipath_{config}_{topo_name}_paths.pickle', 'rb'))
    
    _network = DDF.DDFtopo(edge_list)
    _x=list(range(1, 20))
    _y=[]
    for p in _x:
        link_load, local_link_load = _network.distribute_uniform_flow_on_paths_with_EP(path_dict, p)
        predicted_saturation=local_link_load/max(link_load)
        if predicted_saturation>1.0:
            predicted_saturation=1.0
        _y.append(predicted_saturation)
    plt.scatter(_x, _y, label="{}".format(config))
    plt.plot(_x, _y)

plt.xlabel('router subscription')
plt.xticks(_x)
plt.ylabel('predicted saturation offered_load')
plt.title('dally-dragonfly network scaling effect with all-shortest path routing')
plt.ylim([0,1.0])
plt.legend(loc='lower left')

plt.savefig('ddf_scaling_unipath.png')
