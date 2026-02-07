import networkx as nx
import math
import pandas as pd

def load_nodes(csv_path="data/large_nodes.csv"):
    df = pd.read_csv(csv_path)
    nodes = {}
    for _, row in df.iterrows():
        nodes[row['node']] = {
            "pos": (row['latitude'], row['longitude']),
            "energy": row['energy'],
            "health": row['health'],
            "type": row['type']
        }
    return nodes

def build_graph(nodes):
    G = nx.Graph()
    for node, info in nodes.items():
        G.add_node(node, **info)
    # Connect nodes if distance < threshold
    node_list = list(nodes.items())
    for i in range(len(node_list)):
        n1, d1 = node_list[i]
        for j in range(i+1, len(node_list)):
            n2, d2 = node_list[j]
            dist = math.dist(d1["pos"], d2["pos"])
            if dist < 0.05:  # threshold distance
                G.add_edge(n1, n2, weight=dist*100)
    return G
