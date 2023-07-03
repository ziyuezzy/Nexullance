import networkx as nx
from concurrent.futures import ThreadPoolExecutor
from joblib import Parallel, delayed
import sys
from itertools import islice
MAX_KERNELS = 12

def calculate_GDBG_edges(num_vertices, degree):

    assert(num_vertices > degree)
    # Create a list of edges
    edges = []
    
    for v in range(num_vertices):
        for e in range(degree):
            if v != (degree*v+e)%num_vertices: #exclude self-loop arcs
                edges.extend([(v, (degree*v+e)%num_vertices)])

    return edges

def calculate_k_shortest_paths(graph, v1, v2, k):
    return list( islice(nx.shortest_simple_paths(graph, v1, v2), k) )


def calculate_all_k_shortest_path_length(graph, k):
    vertices = graph.nodes()

    # Create a list of all vertex pairs
    vertex_pairs = [(v1, v2) for v1 in vertices for v2 in vertices if v1 != v2]

    # Calculate the average k-shortest path lengths in parallel with custom progress bar
    progress = 0
    total = len(vertex_pairs)
    print("Calculating shortest paths in GDBG:")

    # Custom progress bar update function
    def update_progress(future):
        nonlocal progress
        progress += 1
        sys.stdout.write('\r' + f"Progress: {progress}/{total}")
        sys.stdout.flush()

    with ThreadPoolExecutor() as executor:
        # Execute the parallel computation
        results = Parallel(n_jobs=MAX_KERNELS)(
            delayed(calculate_k_shortest_paths)(graph, v1, v2, k) for v1, v2 in vertex_pairs
        )

        # Update progress bar asynchronously using concurrent threads
        futures = [executor.submit(update_progress, future) for future in results]

        # Wait for all progress bar updates to complete
        for future in futures:
            future.result()

    print("\nCalculation completed.")
    
    # Process the results and store k-shortest paths in a dictionary
    k_shortest_paths_dict = {}
    k_shortest_average_lengths = {}
    for i, (v1, v2) in enumerate(vertex_pairs):
        k_shortest_paths_dict[(v1, v2)] = results[i]
        k_shortest_average_lengths[(v1, v2)] = sum(len(path) - 1 for path in results[i])/k

    return k_shortest_average_lengths, k_shortest_paths_dict

def distribute_flow_on_paths(graph, k_shortest_paths):
    link_loads = {}
    for u, v in graph.edges():
        link_loads[(u, v)]=0
    for paths in k_shortest_paths.values():
        k = len(paths)
        for path in paths:
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                link_loads[(u, v)] += 1 / k

    return link_loads

# small funtions above

# do calculations for one particular GDBG graph:
def calculate_single_network(num_vertices, degree, k):
    graph_edges = calculate_GDBG_edges(num_vertices, degree)
    graph = nx.DiGraph()
    graph.add_edges_from(graph_edges)
    k_shortest_average_lengths, k_shortest_paths = calculate_all_k_shortest_path_length(graph, k)
    arc_loads = distribute_flow_on_paths(graph, k_shortest_paths)

    return k_shortest_average_lengths, arc_loads
