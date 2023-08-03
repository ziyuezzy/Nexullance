# topology-research

# required python packages:
numpy, matplotlib, networkx, joblib, galois

# class in folder "topolgies/":
Slimfly, RRG and Equality are implemented as child classes of "Unidirected_graph"
While GDBG is implemented separately because of its di-graph nature.

# TODOs: 
1. Test the same static routing functions (k-shortest path, ALLPATH(H), uniform_load) in four topologies.
2. With the same number of EPs, compare topologies with different diameters
3. Given a topology, what is the optimal #EPs per router? Modify the 'distribute load on links' function and find out. 
4. What if the traffic is random uniform instead of uniform?
5. Slimfly link load calculation on p????
