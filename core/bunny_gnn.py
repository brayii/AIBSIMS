# bunny_gnn.py
import torch
import torch.nn as nn
from torch_geometric.nn import SAGEConv

class BunnyGNNPolicy(nn.Module):
    def __init__(self, in_features=6, hidden_dim=32, out_features=3):
        super().__init__()
        self.conv1 = SAGEConv(in_features, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, hidden_dim)
        self.head = nn.Linear(hidden_dim, out_features)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = self.conv1(x, edge_index)
        x = torch.relu(x)
        x = self.conv2(x, edge_index)
        x = torch.relu(x)
        out = self.head(x)
        return out


# Check if the graph data is valid
def is_valid_graph(data):
    return (
        data.x is not None
        and data.x.shape[0] > 0
        and data.edge_index is not None
        and data.edge_index.ndim == 2
        and data.edge_index.shape[1] > 0
    )


# helper to convert bunny world into graph
def build_bunny_graph(grid):
    from torch_geometric.data import Data
    
    node_features = []
    edge_index = []

    id_lookup = {bunny.name: idx for idx, bunny in enumerate(grid.bunnies)}
    
    for bunny in grid.bunnies:
        features = [
            bunny.age / 10.0,  # normalized age
            1.0 if bunny.sex == 'F' else 0.0,
            1.0 if bunny.is_adult() else 0.0,
            1.0 if bunny.is_mutant else 0.0,
            grid.colony_rewards['population_bonus'] / 100.0,
            grid.colony_rewards['vampire_free_bonus'] / 100.0,
        ]
        node_features.append(features)

    # create edges
    for i, bunny_i in enumerate(grid.bunnies):
        for j, bunny_j in enumerate(grid.bunnies):
            if i != j:
                dist = abs(bunny_i.x - bunny_j.x) + abs(bunny_i.y - bunny_j.y)
                if dist <= 2:
                    edge_index.append([i, j])
    
    edge_index = torch.tensor(edge_index).t().contiguous()
    x = torch.tensor(node_features, dtype=torch.float)
    
    return Data(x=x, edge_index=edge_index), id_lookup

# example usage each turn:
# graph_data = build_bunny_graph(grid)
# action_scores = gnn(graph_data)

