import networkx as nx
import pickle
import random
import matplotlib.pyplot as plt
import time

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
    
    second_largest_list = [] # Use this to track the second largest component size and plot it later

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
            #print(f"Number of edges: {G.number_of_edges()}")
            pass  # if less than 2 components, break
        else:
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
            
            prev_second_largest = new_second_largest

    result = point_decrease_list[-1] if point_decrease_list else 0
    return result

def simulation(G, num_simulations):
    results = []
    for _ in range(num_simulations):
        H = G.copy()
        result = random_edge_removal(H)
        results.append(result)
    return results


def main():
    # Load the data
    G = load_monthly_network("2001-05")
    num_simulations = 10
    print(f"Number of edges: {G.number_of_edges()}")
    tic = time.time()
    simulation_results = simulation(G, num_simulations)
    toc = time.time()
    average = sum(simulation_results) / len(simulation_results)
    print(f"Average: {average:.4f}")
    print(f"Elapsed time: {toc - tic:.2f} seconds")
if __name__ == "__main__":
    main()
