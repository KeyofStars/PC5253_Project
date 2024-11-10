# This file is to calculate largest component size after removing a fraction of edges from the network.

import time
import pickle
import random
import pandas as pd
import networkx as nx
import multiprocessing as mp
import matplotlib.pyplot as plt

# Load one month's data
def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph

def remove_absorbing_edges(graph):
    H = graph.copy()
    for edge in list(H.edges()):
        if edge[0] == edge[1]:
            H.remove_edge(edge[0], edge[1])
    return H

# Bond percolation removing edges
def bond_percolation(graph, p):
    H = graph.copy()
    for edge in list(H.edges()):
        if random.random() < p:
            H.remove_edge(edge[0], edge[1])
    return H

def percolation_single_iteration(graph, removal_fraction):
    # Create a copy of the original graph
    percolated_graph = graph.copy()

    # Calculate the initial component size
    initial_components = list(nx.connected_components(graph))
    initial_largest_component = max(initial_components, key=len)
    initial_size = len(initial_largest_component)

    # Remove edges
    percolated_graph = bond_percolation(percolated_graph, removal_fraction)

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

    # Create lists to store the initial and final component sizes
    initial_sizes = []
    final_sizes = []

    # Use a ProcessPoolExecutor to parallelize the percolation process
    num_cores = mp.cpu_count()
    with mp.Pool(num_cores) as pool:
        results = pool.starmap(percolation_single_iteration, [(graph, removal_fraction) for _ in range(num_iterations)])

    for initial_size, final_size in results:
        initial_sizes.append(initial_size)
        final_sizes.append(final_size)

    average_initial_size = sum(initial_sizes) / len(initial_sizes)
    average_final_size = sum(final_sizes) / len(final_sizes)

    return average_initial_size, average_final_size

def plot_percolation_curve(graph, month_to_load, num_iterations=50, removed_range=(0.0, 1.0), step=0.01):
    total_edges = nx.number_of_edges(graph)
    print(f"Month: {month_to_load}, Total edges: {total_edges}")

    removal_fractions = [round(x * step, 2) for x in range(int(removed_range[0]/step), int(removed_range[1]/step)+1)]
    component_sizes = []
    initial_sizes = []

    for removal_fraction in removal_fractions:
        tic = time.time()
        avg_initial_size, avg_final_size = percolation(graph, removal_fraction, num_iterations)
        toc = time.time()
        component_sizes.append(avg_final_size)
        initial_sizes.append(avg_initial_size)
        print(f"Removal Fraction: {removal_fraction}, Initial Size: {avg_initial_size}, Final Size: {avg_final_size}")
        print(f"Time taken: {toc - tic:.2f} seconds")

    phi = removal_fractions[::-1]
    plt.figure()
    plt.plot(phi, component_sizes, label="Final Component Size")
    plt.xlabel(r"$\Phi$")
    plt.ylabel("Component Size")
    plt.title(f"Component Size vs. Phi for {month_to_load}")

    return

def main():
    # Generate date range from 1999-01 to 2001-07
    date_range = pd.date_range(start='2001-07', end='2001-08', freq='ME')
    formatted_dates = date_range.strftime('%Y-%m').tolist()
    for month in formatted_dates:
        loaded_graph = load_monthly_network(month)
        plot_percolation_curve(loaded_graph, month)

if __name__ == "__main__":
    main()