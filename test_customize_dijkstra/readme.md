<!-- TODO: -->
generate the predessor tree by using graph-tool
then construct the paths :


There are some useful functions in networkx source code that are not in the documentation, such as "single_source_all_shortest_paths" and "all_pairs_all_shortest_paths"

The time complexity of "single_source_all_shortest_paths" is O((E+VlogV) + V*(V+E)), the first terms comes from the dijkstra search which produces the predecessor tree, and the second terms comes from the construction of the paths using a tree search in predecessor tree. This is because the multiple paths (but only one path) are not storaged in the lowest-layer dijkstra algorithm in networkx.

But in the context of HPC networkx, and the Nexullance problem, the second step of tree search is **probably** marginal, as only a small part of the predecessor tree should be explored. (low diameter graphs)

The time complexity of "all_pairs_all_shortest_paths" is simply V times the time complexity of "single_source_all_shortest_paths", which is O(V*((E+VlogV) + V*(V+E))).

https://networkx.org/documentation/stable/_modules/networkx/algorithms/shortest_paths/generic.html#all_shortest_paths

