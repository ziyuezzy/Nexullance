# topology-research

# required python packages:
numpy, networkx, galois
, (matplotlib), if you want to plot
, (joblib), if you want to launch parallel algorithms

# class in folder "topolgies/":

class "HPC_topo" is the mother class of most of network topologies, it is based on undirected graph.
Slimfly, RRG, DDF and Equality are implemented as child classes of "HPC_topo"

While GDBG is implemented separately because of its di-graph nature, but this topology has not been studied anymore.

# Nexullance
load balancing algorithm that is still in research

# Example of usage:
see "example_compare_topos.ipynb" for flow-level simulations of the topologies
see "Nexullance_LP_gurobi_*.ipynb" for the usage of nexullance (with LP solver)

in "globals.py", there are functions that can do flow-level simulations of the topologies, or manipulate data structures
in "find_simfly_and_DDF.ipynb", some simple code has been written to find valid configurations for slimfly and ddf topologies.