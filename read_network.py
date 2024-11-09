# This script is to test reading the monthly network files and plotting the fraction of the largest connected component over time

import pickle
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

def load_monthly_network(month_to_load):
    file_path = f"monthly_networks/{month_to_load}.pkl"
    with open(file_path, 'rb') as file:
        loaded_graph = pickle.load(file)

    return loaded_graph

def convert_to_undirected(graph):
    return nx.Graph(graph)

def remove_node(graph):
    centrality = nx.degree_centrality(graph)
    highest_centrality_node = max(centrality, key=centrality.get) 
    graph.remove_node(highest_centrality_node)

def plot_network():
    # Generate date range from 1999-01 to 2001-07
    date_range = pd.date_range(start='1999-01', end='2001-08', freq='ME')
    formatted_dates = date_range.strftime('%Y-%m').tolist()

    # Create a list to store the fraction of the largest connected component for each month
    fraction = []
    for month in formatted_dates:
        loaded_graph = load_monthly_network(month)
        largest_component = max(nx.connected_components(loaded_graph), key=len)
        remove_node(loaded_graph)
        largest_component_after = max(nx.connected_components(loaded_graph), key=len)
        fraction.append(len(largest_component_after)/len(largest_component))

    # Plot the fraction of the largest connected component over time
    plt.plot(date_range, fraction)
    plt.xlabel('Date')
    plt.ylabel('Fraction of largest connected component')
    plt.title('Fraction of largest connected component over time')
    plt.show()

    return


plot_network()
