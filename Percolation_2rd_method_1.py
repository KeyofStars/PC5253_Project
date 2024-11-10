# This script is to do the percolation for all months' data

import networkx as nx
import pickle
import random
import matplotlib.pyplot as plt
import time
import pandas as pd

# Load one month's data
def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph

# Remove isolated nodes
def remove_self_connected_nodes(G):
    self_connected_nodes = [node for node in G.nodes if all(neighbor == node for neighbor in G.neighbors(node))]
    G.remove_nodes_from(self_connected_nodes)

# Retain 5% of the edges
def retain_5_percent_edges(G):
    #Delete 95% of the edges
    initial_edge_count = G.number_of_edges()
    final_edge_count = int(initial_edge_count * 0.05)
    all_edges = list(G.edges(keys=True))
    random.shuffle(all_edges) # Shuffle the edges

    edges_to_keep = all_edges[:final_edge_count]
    G.clear_edges()
    G.add_edges_from(edges_to_keep)

# Calculate component's number and size
def get_components_info(graph):
    components = [component for component in nx.connected_components(graph) if len(component) > 1]
    component_sizes = [len(component) for component in components]
    return len(components), component_sizes

def calculate_remaining_edge_ratio(G, initial_edge_count):
    final_remaining_edge_count = G.number_of_edges()
    remaining_edge_ratio = final_remaining_edge_count / initial_edge_count
    print(f"final_remaining_edge_count: {final_remaining_edge_count}")
    print(f"Remaining edge ratio: {remaining_edge_ratio:.4f}")
    return remaining_edge_ratio

# Remove edges randomly and track the second largest component size
def random_edge_removal(G):

    initial_edge_count = G.number_of_edges()
    remove_self_connected_nodes(G)
    retain_5_percent_edges(G)
    
    second_largest_list = []
    prev_second_largest = sorted(get_components_info(G)[1])[-2] if len(get_components_info(G)[1]) >= 2 else 0
    second_largest_list.append(prev_second_largest)
    found_decreasing = False
    found_increasing = False
    point_decrease_list = []

    while True:
        
        remaining_edges = list(G.edges(keys=True))
        if not remaining_edges:
            break  # if no edges left, break

        edge_to_remove = random.choice(remaining_edges)
        G.remove_edge(*edge_to_remove[:3])  # remove a random edge

        # calculate the number of components and their sizes after removing the edge
        new_num_components, new_component_sizes = get_components_info(G)
        
        # compare the second largest component size
        if len(new_component_sizes) < 2:
            print(f"Number of edges: {G.number_of_edges()}")
            break  # if less than 2 components, break

        new_second_largest = sorted(new_component_sizes)[-2] if len(new_component_sizes) >= 2 else 0
        second_largest_list.append(new_second_largest)

        if new_second_largest < prev_second_largest:
            if not found_decreasing:
                found_decreasing = True
                print("Second largest component started decreasing.")
                ratio_decrease = calculate_remaining_edge_ratio(G, initial_edge_count)
                point_decrease_list.append(ratio_decrease)
            found_increasing = False
        elif new_second_largest > prev_second_largest:
            if not found_increasing:
                found_increasing = True
                print("Second largest component started increasing.")
                calculate_remaining_edge_ratio(G, initial_edge_count)

            found_decreasing = False
        else:
            # if the second largest component size remains the same,
            pass

        # track the component info
        prev_second_largest = new_second_largest
        #print(f"Number of components: {new_num_components}")
        #print(f"Sizes of components: {new_component_sizes}")

    result = point_decrease_list[-1] if point_decrease_list else 0
    return result

def simulation(G, num_simulations):
    results = []
    for _ in range(num_simulations):
        H = G.copy()
        result = random_edge_removal(H)
        results.append(result)
    return results

def Calculate_All_Months(num_simulations):
    # Generate date range from 1999-05 to 2002-05
    date_range = pd.date_range(start='1999-05', end='2002-06', freq='ME')
    formatted_dates = date_range.strftime('%Y-%m').tolist()

    ratio_per_month = []
    for month in formatted_dates:
        loaded_graph = load_monthly_network(month)
        simulation_results_month = simulation(loaded_graph, num_simulations)
        average = sum(simulation_results_month) / len(simulation_results_month)
        ratio_per_month.append(average)
    return formatted_dates,ratio_per_month

def plot_percolation_ratio(date,ratio_per_month):
    plt.figure(figsize=(14,7))
    plt.plot(date, ratio_per_month)
    plt.xlabel('Date')
    plt.ylabel(r'$ \Phi_c $')
    plt.title(r'$\Phi_c$ over time')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

def main():
    num_simulations = 1000
    date,ratio_per_month = Calculate_All_Months(num_simulations)
    plot_percolation_ratio(date,ratio_per_month)

if __name__ == "__main__":
    main()
