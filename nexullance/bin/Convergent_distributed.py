import globals as gl
import numpy as np
import matplotlib.pyplot as plt

def load_len_cost_func(path, max_edge_load):
    return max_edge_load*len(path)
    
def Convergent_Distributed_LB(weighted_path_dict, network_instance, EPR, cost_func=load_len_cost_func, 
        M_EPs=[], max_prob_transfer=0.1, num_iterations=500, _plot=True, transfer_threshold=0.05, always_sync=False):
    link_flows, local_link_flows=network_instance.distribute_arbitrary_flow_on_weighted_paths_with_EPs_return_dict(
                                            weighted_path_dict, EPR, M_EPs)
    # define Cost = len(path)*max(edge loads)
    max_link_load=max(link_flows.values())
    initial_mu=local_link_flows/max_link_load
    plot_y_data=[]
    plot_x_data=[]

    M_R=gl.convert_M_EPs_to_M_R(M_EPs,
                network_instance.nx_graph.number_of_nodes(), EPR)
    data={} # {(s, d): [[path], prob, max link load, cost]}
    for (s, d), weighted_paths in weighted_path_dict.items():
        data[(s, d)] = []
        for path, prob in weighted_paths:
            max_edge_load = 0
            for i in range(len(path)-1):
                if max_edge_load < link_flows[(path[i], path[i+1])]:
                    max_edge_load=link_flows[(path[i], path[i+1])]
            
            data[(s, d)].append([path, prob, max_edge_load, cost_func(path, max_edge_load)])

    def vary_path_prob(data_list, increment_prob, s, d):
        # [path, prob, max_edge_load, cost_func(path, max_edge_load)]
        assert(-1<=increment_prob<=1)
        data_list[1]+=increment_prob
        assert(0<=data_list[1]<=1)
        data_list[2]+=increment_prob*M_R[(s, d)]
        data_list[3]=cost_func(data_list[0], data_list[2])

    for it in range(num_iterations):
        for (s, d), data_lists in data.items():

            if M_R[s][d] == 0:
                continue

            if len(data_lists)==1:
                continue # meaning there is only one path to choose
            
            max_path_cost=0
            max_cost_path_enum=-1
            min_path_cost=np.inf
            min_cost_path_enum=-1

            for i , data_list in enumerate(data_lists):
                cost=data_list[3]
                max_edge_load=data_list[2]
                path_prob=data_list[1]
                if cost > max_path_cost and path_prob>0 and abs(max_edge_load-max_link_load)<transfer_threshold:
                    max_path_cost = cost
                    max_cost_path_enum=i
            # have to loop twice because there exist a case when prob>0 and prob>1 does not overlap, 
            # the minimum cost found can be greater than the maximum cost found
            for i , data_list in enumerate(data_lists): 
                cost=data_list[3]
                max_edge_load=data_list[2]
                path_prob=data_list[1]
                if cost < min_path_cost and path_prob<1 and cost < max_path_cost :
                    min_path_cost = cost
                    min_cost_path_enum=i
            
            if max_path_cost==min_path_cost or max_cost_path_enum==-1 or min_cost_path_enum==-1:
                continue

            max_cost_path_prob=data[(s, d)][max_cost_path_enum][1]
            min_cost_path_prob=data[(s, d)][min_cost_path_enum][1]
            # max_cost_path=data[(s, d)][max_cost_path_enum][3]
            # min_cost_path=data[(s, d)][min_cost_path_enum][3]
            max_cost_path_load=data[(s, d)][max_cost_path_enum][2]
            min_cost_path_load=data[(s, d)][min_cost_path_enum][2]

            # #TODO: ??
            # if max_cost_path_load <= min_cost_path_load:
            #     continue

            prob_to_transfer = min([max_prob_transfer, 
                                (1 - min_cost_path_prob),
                                max_cost_path_prob])
            if max_cost_path_load>min_cost_path_load:
                prob_to_transfer=min([prob_to_transfer, (max_cost_path_load-min_cost_path_load)/M_R[s][d]/2])
            # TODO: also include the secondary maximal path load? (for monotonic growth)
            assert(0.0<=prob_to_transfer<=1.0)

            vary_path_prob(data_lists[min_cost_path_enum], prob_to_transfer, s, d )
            vary_path_prob(data_lists[max_cost_path_enum], -prob_to_transfer, s, d )

            if always_sync:
                # ================ sync =================
                for (s, d), data_lists in data.items():
                    for i, data_list in enumerate(data_lists):
                        path=data_list[0]
                        if data_list[1] != weighted_path_dict[(s, d)][i][1]:
                            weighted_path_dict[(s, d)][i]=(weighted_path_dict[(s, d)][i][0], data_list[1])

                link_flows, local_link_flows=network_instance.distribute_arbitrary_flow_on_weighted_paths_with_EPs_return_dict(
                                                        weighted_path_dict, EPR, M_EPs)
                max_link_load=max(link_flows.values())
                for (s, d), data_lists in data.items():
                    for i, data_list in enumerate(data_lists):
                        path=data_list[0]
                        max_edge_load = 0
                        for i in range(len(path)-1):
                            if max_edge_load < link_flows[(path[i], path[i+1])]:
                                max_edge_load=link_flows[(path[i], path[i+1])]
                        data_list[2]=max_edge_load
                        data_list[3]=cost_func(data_list[0], max_edge_load)
                # ======================================

        if not always_sync:
            # ================ sync =================
            for (s, d), data_lists in data.items():
                for i, data_list in enumerate(data_lists):
                    path=data_list[0]
                    if data_list[1] != weighted_path_dict[(s, d)][i][1]:
                        weighted_path_dict[(s, d)][i]=(weighted_path_dict[(s, d)][i][0], data_list[1])

            link_flows, local_link_flows=network_instance.distribute_arbitrary_flow_on_weighted_paths_with_EPs_return_dict(
                                                    weighted_path_dict, EPR, M_EPs)
            max_link_load=max(link_flows.values())
            for (s, d), data_lists in data.items():
                for i, data_list in enumerate(data_lists):
                    path=data_list[0]
                    max_edge_load = 0
                    for i in range(len(path)-1):
                        if max_edge_load < link_flows[(path[i], path[i+1])]:
                            max_edge_load=link_flows[(path[i], path[i+1])]
                    data_list[2]=max_edge_load
                    data_list[3]=cost_func(data_list[0], max_edge_load)
            # ======================================

        print(f"at it{it}, sat load={local_link_flows/max(link_flows.values())}")
        plot_x_data.append(it)
        plot_y_data.append(local_link_flows/max(link_flows.values()))

        if len(plot_y_data)>10 and max(plot_y_data[-9:])-min(plot_y_data[-9:]) < 0.0001:
            print("seems to converge, terminating")
            break
        if plot_y_data[-1]<initial_mu:
            print("seems that it is not converging, terminating")
            break

    if _plot:
        plt.scatter(plot_x_data, plot_y_data)
        plt.xlabel("iterations")
        plt.ylabel("Local-Remote link utilization ratio")

    return weighted_path_dict, plot_y_data
