import random
import numpy as np

# seed the rng
random.seed(0)

# define the perturbation function
def perturbate(input_matrix: np.ndarray, perturbation_rate: float, print_output: bool=False):
    output_matrix = np.zeros_like(input_matrix)
    num_nodes = input_matrix.shape[0]
    for i in range(num_nodes):
        for j in range(num_nodes):
            # output_matrix[i][j] = input_matrix[i][j] + random.uniform(-perturbation_rate*input_matrix[i][j], perturbation_rate*input_matrix[i][j])
            output_matrix[i][j] = input_matrix[i][j] + random.gauss(0, perturbation_rate*input_matrix[i][j])
    
    if print_output:
        print("Perturbed matrix:")
        print(output_matrix)
    return output_matrix