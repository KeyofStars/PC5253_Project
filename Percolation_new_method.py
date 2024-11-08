import networkx as nx
import random
import pickle
import matplotlib.pyplot as plt
import time

# Load one month's data
def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph

def site_percolation(graph, p):
    H = graph.copy()
    for node in list(H.nodes()):
        if random.random() > p:
            H.remove_node(node)
    return H

def calculate_connectivity(H):
    
    components = list(nx.connected_components(H))
    if components:
        largest_component = max(components, key=len)
        return len(components), len(largest_component)
    else:
        return len(components), 0

def has_spanning_path(G, p, threshold_ratio=0.5):
    H = site_percolation(G, p)
    components = list(nx.connected_components(H))
    if not components:
        return False

    largest_component = max(components, key=len)
    if len(largest_component) >= threshold_ratio * H.number_of_nodes():
        return True
    else:
        return False
    
def simulate_percolation(G, p_values, num_simulations,threshold_ratio=0.5):
    results = []
    for p in p_values:
        success_count = 0

        for _ in range(num_simulations):
            if has_spanning_path(G, p, threshold_ratio):
                success_count += 1
        success_ratio = success_count / num_simulations
        results.append((p, success_ratio))
    return results

p_values = [i/10 for i in range(1, 11)]
num_simulations = 100
G = load_monthly_network("2000-05")

tic = time.time()
results = simulate_percolation(G, p_values, num_simulations)
toc = time.time()
print(toc - tic)

plt.plot([result[0] for result in results], [result[1] for result in results])
plt.xlabel("p")
plt.ylabel("Success ratio")
plt.title("Percolation simulation")

plt.show()


