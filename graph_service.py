import networkx as nx
from typing import Dict, Any, List
import pandas as pd

class GraphService:
    @staticmethod
    def build_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> nx.Graph:
        """Build NetworkX graph from nodes and edges"""
        G = nx.Graph()

        # Add nodes
        for node in nodes:
            G.add_node(node["id"], **node)

        # Add edges
        for edge in edges:
            G.add_edge(
                edge["source"],
                edge["target"],
                type=edge.get("type", "transaction"),
                weight=edge.get("value", 1)
            )

        return G

    @staticmethod
    def calculate_centrality_measures(G: nx.Graph) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality measures"""
        measures = {}

        try:
            measures["degree_centrality"] = nx.degree_centrality(G)
            measures["betweenness_centrality"] = nx.betweenness_centrality(G)
            measures["closeness_centrality"] = nx.closeness_centrality(G)
        except:
            # Handle disconnected graphs
            measures["degree_centrality"] = {node: G.degree(node) / (len(G) - 1) if len(G) > 1 else 0
                                           for node in G.nodes()}

        return measures

    @staticmethod
    def detect_communities(G: nx.Graph) -> Dict[str, int]:
        """Detect communities using greedy modularity maximization"""
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            communities = list(greedy_modularity_communities(G))

            community_map = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_map[node] = i

            return community_map
        except:
            # Fallback: assign all nodes to community 0
            return {node: 0 for node in G.nodes()}

    @staticmethod
    def find_circular_patterns(G: nx.Graph, max_length: int = 4) -> List[List[str]]:
        """Find circular transaction patterns"""
        cycles = []
        try:
            # Find all simple cycles up to max_length
            all_cycles = list(nx.simple_cycles(G))
            cycles = [cycle for cycle in all_cycles if len(cycle) <= max_length]
        except:
            pass

        return cycles

    @staticmethod
    def analyze_fraud_clusters(G: nx.Graph, suspicious_nodes: List[str]) -> Dict[str, Any]:
        """Analyze clusters around suspicious nodes"""
        clusters = {}

        for suspicious_node in suspicious_nodes:
            if suspicious_node in G:
                # Find neighbors within 2 hops
                neighbors_1 = set(G.neighbors(suspicious_node))
                neighbors_2 = set()

                for neighbor in neighbors_1:
                    neighbors_2.update(G.neighbors(neighbor))

                neighbors_2.discard(suspicious_node)
                neighbors_2 -= neighbors_1

                clusters[suspicious_node] = {
                    "direct_connections": list(neighbors_1),
                    "second_degree_connections": list(neighbors_2),
                    "cluster_size": len(neighbors_1) + len(neighbors_2) + 1
                }

        return clusters