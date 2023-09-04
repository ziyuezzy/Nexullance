import globals as gl
import topologies.Slimfly as Slimfly
import pickle
import pandas as pd
from statistics import mean
from math import ceil
import matplotlib.pyplot as plt

#slimfly
topo_name='slimfly'
configs={}
search_min=0  #lower bound of the search
search_max=1100 #upper bound of the search
# list of prime number less than 10: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 
# This should be enough for finding all slimfly configurations with less than 20k nodes
prime_numbers=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 ]
print(f"Searching for slimfly configurations: (num_vertices, k'), Number of routers between {search_min} and {search_max}")
configs={}
for delta in [-1, 0, 1]:
    for prime in prime_numbers:
        power = 1
        while(1):
            q=pow(prime,power)
            num_vertices=q**2*2
            if(search_min >= num_vertices):
                power+=1
                continue
            if(num_vertices <= search_max ):
                if ((q-delta)%4==0):
                    kp=int((3*q-delta)/2)
                    print(f"slimfly configuration found: q={q}, delta={delta} ({num_vertices}, {kp}) p={ceil(kp/2)}")
                    configs[(num_vertices, kp)]=ceil(kp/2)
                power+=1
            else:
                break
configs = dict(sorted(configs.items(), key=lambda x:x[1]))

for config, EPs in configs.items():

    edge_list=pickle.load(open(f'./pickled_data/graphs_and_paths/{config}_{topo_name}_edgelist.pickle', 'rb'))
    path_dict=pickle.load(open(f'./pickled_data/graphs_and_paths/all_shortest_paths_{config}_{topo_name}_paths.pickle', 'rb'))
    
    _network = Slimfly.Slimflytopo(edge_list)
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
plt.ylabel('predicted saturation offered_load')
plt.title('slimfly network scaling effect')
plt.ylim([0,1.0])
plt.legend(loc='lower left')

plt.savefig('slimfly_scaling.png')


