import pickle
import networkx as nx
import random
import matplotlib.pyplot as plt
import time

# Load one month's data
def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph

# Percolation function
def percolation(graph, removal_fraction=0.1, num_iterations=100):
    initial_sizes = []
    final_sizes = []

    for _ in range(num_iterations):
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

        initial_sizes.append(initial_size)
        final_sizes.append(final_size)

    # Calculate the average initial and final sizes
    avg_initial_size = sum(initial_sizes) / num_iterations
    avg_final_size = sum(final_sizes) / num_iterations

    return avg_initial_size, avg_final_size

def plot_percolation(graph):

    # Create a list of fractions to remove
    removed_fraction = [round(x * 0.1, 2) for x in range(1, 11)]
    component_fraction = []

    # Iterate over each fraction
    for fraction in removed_fraction:
        tic = time.time()
        initial_size, final_size = percolation(graph, fraction)
        print(f"Fraction: {fraction}, Initial size: {initial_size}, Final size: {final_size}")
        toc = time.time()
        print(f"Time taken: {toc - tic}")
        true_size = initial_size - nx.number_of_nodes(graph) * fraction
        component_fraction.append(final_size / true_size)
    
    # Plot the results
    plt.plot(removed_fraction, component_fraction)
    plt.xlabel("Fraction of Nodes Removed")
    plt.ylabel("Fraction of Largest Component")
    plt.title("Percolation Curve")
    plt.show()

# Main function
def main():
    month_to_load = "2001-04"
    loaded_graph = load_monthly_network(month_to_load)
    initial_size, new_size = percolation(loaded_graph)
    print(f"Month: {month_to_load}, Initial size: {initial_size}, New size: {new_size}")
    plot_percolation(loaded_graph)

if __name__ == "__main__":
    main()