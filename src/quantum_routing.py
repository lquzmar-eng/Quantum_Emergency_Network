import random
import networkx as nx

def quantum_inspired_routing(G, start, end, node_data):
    """
    Quantum-inspired routing:
    - لكل مسار محتمل، نحسب score = weight + energy_penalty
    - نختار probabilistically مسار بأقل score
    """
    all_paths = list(nx.all_simple_paths(G, start, end, cutoff=6))
    path_scores = []
    for path in all_paths:
        score = 0
        for i in range(len(path)-1):
            edge_w = G[path[i]][path[i+1]]['weight']
            energy_penalty = 100 - node_data[path[i]]['energy']
            score += edge_w + energy_penalty
        path_scores.append((path, score))

    # اختيار probabilistic favoring lower score
    path_scores.sort(key=lambda x: x[1])
    top_paths = path_scores[:3]  # أعلى 3 مسارات
    selected_path = random.choice(top_paths)[0]
    return selected_path
