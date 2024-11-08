import os
import pickle
import pandas as pd
import networkx as nx

data = pd.read_csv("cs_proj_enron.csv")

data['Date'] = pd.to_datetime(data['Date'], infer_datetime_format=True)

data['YearMonth'] = data['Date'].dt.to_period('M')
unique_months = data['YearMonth'].unique()

# Create a dictionary to store each monthly network
monthly_networks = {}

# Iterate over each unique month to create networks
for month in unique_months:
    # Filter data for the current month
    monthly_data = data[data['YearMonth'] == month]

    # Create a directed graph
    G = nx.MultiGraph()

    # Iterate over each row in the filtered data
    for _, row in monthly_data.iterrows():
        from_email = row['From_copy']
        to_email = row['To_copy']
        from_position = row['from_position_copy']
        to_position = row['to_position']

        # Add sender and recipient nodes with email and position information
        G.add_node(from_email, position=from_position)
        G.add_node(to_email, position=to_position)

        # Add a directed edge representing the email, with content and label as attributes
        G.add_edge(from_email, to_email, content=row['content'], label=row['labels'])

    # Store the graph in the dictionary with the month as the key
    monthly_networks[str(month)] = G

# Output a message indicating that the networks have been created
print("Finished creating networks. Each network contains email information for one month.")


if __name__ == "__main__":
    os.makedirs("monthly_networks", exist_ok=True)

    for month, graph in monthly_networks.items():
        file_path = f"monthly_networks/{month}.pkl"
        with open(file_path, 'wb') as file:
            pickle.dump(graph, file)

    print("All networks have been saved as .pkl files.")