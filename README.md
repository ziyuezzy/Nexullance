# topology-research

# required python packages:
numpy, matplotlib, networkx, joblib (for multi-thread cpu algorithms), galois (for slimfly), gurobipy, (pynauty)

# classes in folder "topolgies/":
Slimfly, RRG and Equality are implemented as child classes of "HPC_topo" which are based on undiretional graphs.
While GDBG is implemented separately because of its di-graph nature.

# Nexullance:

Nexullance is an optimization technique for improving the link load balance in a network under a specific traffic demand matrix.

Input: 
inter-router graph (read from file), demand matrix

Output:
Link load distribution,
(ideally, ) also the traffic-agnostic routing tables,
network bandwidth utilization (NBU) before satruation: data throughput/ the total aggregated bandwidth of the network (as a function of: demand matrix, link capacties, routing, network configurations). $NBU = SUM(TM^{R})*MAX({L^{local}})$?

$sum(\{f^{local}\})$ at saturation
$f^{local}_{i} = sum_j(TM^{EP}_{i,j})*C_{local}/max(\{f^{local}_{i}\})$ at saturation 


Measurements:
Execution time,
RAM occupation,


# TODOs: 

for Nexullance_IT, try new things for approaching the optimality:
1. wrap up the heuristic
2. add new cost function cost(link)=alpha+load(link)^beta
Try to use Bayesian Optimization to fine tune the heuristic parameters
https://github.com/bayesian-optimization/BayesianOptimization
3. change the initial point of the algorithm


# Notations for flow-level modeling:
Load ($L^{local}$ and $L^{remote}$) (unit-less): the utilization of a resource. e.g., link load = aggregated flow on the link / link capacity
Flow ($f^{local}$ and $f^{remote}$) [Gbps]: The data rate of a data stream
    A flow originates from an EP and ends up in another EP
    The aggregated flow on a link is defined as the summation of data rates of flow that passes by the link.

Link capacity ($C^{local}$ and $C^{remote}$) [Gbps]: The maximum data rate (aggregated flow) on a link

$L=f/C$

Inter-router Traffic demand matrix ($TM^{R}$) (unit-less): the relative values of the aggregated flows between the src and dest routers

Inter-EP Traffic demand matrix ($TM^{EP}$) (unit-less): the relative values of the flows among s and d EPs

Local-Remote ratio $\mu = MAX({L^{local}})/MAX({L^{remote}})$

