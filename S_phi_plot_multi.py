# This file is to calculate largest component size after removing a fraction of nodes from the network.
# And it uses multithreading to speed up the process.

import concurrent.futures
import pickle
import networkx as nx
import random
import matplotlib.pyplot as plt
import math
import os


# Load one month's data
def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph


# Percolation functions
def percolation_single_iteration(graph, removal_fraction):
    # Create a copy of the original graph
    percolated_graph = graph.copy()

    # Calculate the initial component size
    initial_components = list(nx.connected_components(graph))
    initial_largest_component = max(initial_components, key=len)
    initial_size = len(initial_largest_component)

    # Calculate the number of nodes to remove
    num_nodes_to_remove = int(len(percolated_graph.nodes()) * removal_fraction)

    # Randomly select nodes to remove
    nodes_to_remove = random.sample(list(percolated_graph.nodes()), num_nodes_to_remove)

    # Remove the selected nodes
    percolated_graph.remove_nodes_from(nodes_to_remove)

    # Calculate the final component size
    final_components = list(nx.connected_components(percolated_graph))
    if final_components:
        final_largest_component = max(final_components, key=len)
        final_size = len(final_largest_component)
    else:
        final_size = 0

    return initial_size, final_size


# Percolation function for multiple iterations
def percolation(graph, removal_fraction=0.1, num_iterations=100):
    initial_sizes = []
    final_sizes = []

    # Use a ProcessPoolExecutor to parallelize the percolation process
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(percolation_single_iteration, graph, removal_fraction) for _ in range(num_iterations)]
        for future in concurrent.futures.as_completed(futures):
            initial_size, final_size = future.result()
            initial_sizes.append(initial_size)
            final_sizes.append(final_size)

    # Calculate the average initial and final sizes
    avg_initial_size = sum(initial_sizes) / num_iterations
    avg_final_size = sum(final_sizes) / num_iterations

    return avg_initial_size, avg_final_size


# Plot percolation curve
def plot_percolation(graph, month_to_load, num_iterations=100, removed_range=(0.0, 1.0), step=0.1):
    total_nodes = nx.number_of_nodes(graph)

    # Create a list of fractions to remove
    removed_fraction = [round(x * step, 2) for x in range(int(removed_range[0]/step), int(removed_range[1]/step)+1)]
    component_fraction = []

    # Iterate over each fraction
    for fraction in removed_fraction:
        avg_initial_size, avg_final_size = percolation(graph, fraction, num_iterations)
        true_size = math.ceil(avg_initial_size - nx.number_of_nodes(graph) * fraction)
        print(f"Fraction: {fraction}, True size: {true_size}, Final size: {avg_final_size}")
        if true_size == 0:
            component_fraction.append(0)
        else:
            component_fraction.append(avg_final_size / true_size)
        #component_fraction.append(avg_final_size / total_nodes)
    
    # Plot the results
    plt.plot(removed_fraction, component_fraction)
    plt.xlabel("Fraction of Nodes Removed")
    plt.ylabel("Fraction of Largest Component")
    plt.title("Percolation Curve")
    plt.show()

    # Save the plot
    plt.savefig(f"./percolation_figure/{month_to_load}.png")

    return


# Main function
def main():
    month_to_load = "2001-05"
    loaded_graph = load_monthly_network(month_to_load)
    plot_percolation(loaded_graph, month_to_load)


if __name__ == "__main__":
    main()