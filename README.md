# topology-research

# required python packages:
numpy, matplotlib, networkx, joblib, galois

# class in folder "topolgies/":
Slimfly, RRG and Equality are implemented as child classes of "Unidirected_graph"
While GDBG is implemented separately because of its di-graph nature.

# Nexullance

# TODOs: 

for Nexullance_IT, try new things for approaching the optimality:
1. wrap up the heuristic
2. add new cost function cost(link)=alpha+load(link)^beta
Try to use Bayesian Optimization to fine tune the heuristic parameters

https://github.com/bayesian-optimization/BayesianOptimization

3. change the initial point of the algorithm

