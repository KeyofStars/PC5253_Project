# This file is to calculate largest component size after removing a fraction of nodes from the network.
# And it uses multithreading to speed up the process.

import concurrent.futures
import pickle
import networkx as nx
import random
import matplotlib.pyplot as plt
import math
import os
import pandas as pd


# Load one month's data
def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph

def site_percolation(graph, p):
    H = graph.copy()
    for node in list(H.nodes()):
        if random.random() < p:
            H.remove_node(node)
    return H

# Percolation functions
def percolation_single_iteration(graph, removal_fraction):
    # Create a copy of the original graph
    percolated_graph = graph.copy()

    # Calculate the initial component size
    initial_components = list(nx.connected_components(graph))
    initial_largest_component = max(initial_components, key=len)
    initial_size = len(initial_largest_component)

    # Remove nodes
    percolated_graph = site_percolation(percolated_graph, removal_fraction)


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
def plot_percolation(graph, month_to_load, num_iterations=500, removed_range=(0.0, 1.0), step=0.01):
    total_nodes = nx.number_of_nodes(graph)
    print(f"Month: {month_to_load}, Total nodes: {total_nodes}")

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
        elif true_size < avg_final_size:
            component_fraction.append(0)
        else:
            component_fraction.append(avg_final_size / true_size)
        #component_fraction.append(avg_final_size / total_nodes)
    
    # Plot the results
    phi = removed_fraction[::-1]
    plt.figure()
    plt.plot(phi, component_fraction)
    plt.xlabel(r"$\Phi$")
    plt.ylabel("Giant Cluster Size")
    plt.title(f"Component Fraction vs. Phi for {month_to_load}")

    # Save the plot
    plt.savefig(f"./S_Phi_figure/{month_to_load}.png")

    return


# Main function
def main():
    # Generate date range from 1999-01 to 2001-07
    date_range = pd.date_range(start='1999-01', end='2001-08', freq='ME')
    formatted_dates = date_range.strftime('%Y-%m').tolist()
    for month in formatted_dates:
        loaded_graph = load_monthly_network(month)
        plot_percolation(loaded_graph, month)

if __name__ == "__main__":
    main()