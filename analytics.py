import networkx as nx
import numpy as np
import pandas as pd
from collections import defaultdict
import random

class NetworkAnalytics:
    def __init__(self, network):
        """
        Initialize the analytics module with a social network instance.
        
        Args:
            network (SocialNetwork): The social network to analyze
        """
        self.network = network
    
    def get_density(self):
        """
        Calculate the density of the network.
        
        Returns:
            float: Network density (0-1)
        """
        return nx.density(self.network.graph)
    
    def get_avg_clustering(self):
        """
        Calculate the average clustering coefficient.
        
        Returns:
            float: Average clustering coefficient
        """
        # Convert to undirected for clustering calculation
        undirected = self.network.graph.to_undirected()
        if len(undirected.nodes()) > 0:
            return nx.average_clustering(undirected)
        return 0.0
    
    def get_avg_path_length(self):
        """
        Calculate the average shortest path length.
        
        Returns:
            float: Average path length or 0 if not connected
        """
        # Convert to undirected for path calculations
        undirected = self.network.graph.to_undirected()
        if len(undirected.nodes()) > 1:
            try:
                return nx.average_shortest_path_length(undirected)
            except nx.NetworkXError:
                # Graph is not connected
                components = list(nx.connected_components(undirected))
                if components:
                    # Calculate for largest component
                    largest = max(components, key=len)
                    subgraph = undirected.subgraph(largest)
                    return nx.average_shortest_path_length(subgraph)
                return 0.0
        return 0.0
    
    def get_num_connected_components(self):
        """
        Calculate the number of connected components.
        
        Returns:
            int: Number of connected components
        """
        undirected = self.network.graph.to_undirected()
        return nx.number_connected_components(undirected)
    
    def get_degree_assortativity(self):
        """
        Calculate the degree assortativity coefficient.
        
        Returns:
            float: Degree assortativity coefficient (-1 to 1)
        """
        try:
            return nx.degree_assortativity_coefficient(self.network.graph)
        except:
            return 0.0
    
    def get_connectivity_data(self):
        """
        Generate connectivity information for the network.
        
        Returns:
            dict: Connectivity data
        """
        G = self.network.graph
        undirected = G.to_undirected()
        
        # Check if graph is connected
        is_connected = nx.is_connected(undirected)
        
        # Get connected components
        components = list(nx.connected_components(undirected))
        
        # Get component sizes
        component_sizes = [len(c) for c in components]
        
        # Get largest component
        largest_component_size = max(component_sizes) if component_sizes else 0
        largest_component_percentage = (largest_component_size / len(G.nodes())) * 100 if len(G.nodes()) > 0 else 0
        
        # Prepare results
        results = {
            "Connected": is_connected,
            "Number of components": len(components),
            "Largest component size": largest_component_size,
            "Largest component percentage": f"{largest_component_percentage:.2f}%",
            "Component sizes": component_sizes
        }
        
        return results
    
    def get_centrality_measures(self):
        """
        Calculate various centrality measures for all nodes.
        
        Returns:
            dict: Dictionary mapping usernames to centrality measures
        """
        G = self.network.graph
        
        # Skip if graph is empty
        if len(G.nodes()) == 0:
            return {}
        
        # Calculate centrality measures
        degree_centrality = nx.degree_centrality(G)
        
        try:
            eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
        except:
            # Fallback if eigenvector centrality fails to converge
            eigenvector_centrality = {node: 0.0 for node in G.nodes()}
        
        try:
            betweenness_centrality = nx.betweenness_centrality(G)
        except:
            # Fallback if betweenness calculation fails
            betweenness_centrality = {node: 0.0 for node in G.nodes()}
        
        try:
            closeness_centrality = nx.closeness_centrality(G)
        except:
            # Fallback if closeness calculation fails
            closeness_centrality = {node: 0.0 for node in G.nodes()}
        
        # Combine all measures
        results = {}
        for node in G.nodes():
            results[node] = {
                "degree_centrality": degree_centrality.get(node, 0.0),
                "eigenvector_centrality": eigenvector_centrality.get(node, 0.0),
                "betweenness_centrality": betweenness_centrality.get(node, 0.0),
                "closeness_centrality": closeness_centrality.get(node, 0.0)
            }
        
        return results
    
    def get_user_centrality(self, user):
        """
        Get centrality measures for a specific user.
        
        Args:
            user (str): Username to get measures for
            
        Returns:
            dict: Dictionary of centrality measures for the user
        """
        centrality_measures = self.get_centrality_measures()
        return centrality_measures.get(user, {
            "degree_centrality": 0.0,
            "eigenvector_centrality": 0.0,
            "betweenness_centrality": 0.0,
            "closeness_centrality": 0.0
        })
    
    def detect_communities(self, method="girvan_newman"):
        """
        Detect communities in the network.
        
        Args:
            method (str): Community detection method to use
            
        Returns:
            list: List of communities (each a list of usernames)
        """
        return self.network.detect_communities(method)
    
    def get_community_metrics(self, communities):
        """
        Calculate metrics for detected communities.
        
        Args:
            communities (list): List of communities (each a list of usernames)
            
        Returns:
            pd.DataFrame: DataFrame with community metrics
        """
        G = self.network.graph
        undirected = G.to_undirected()
        
        metrics = []
        
        for i, community in enumerate(communities):
            # Skip empty communities
            if not community:
                continue
                
            # Create subgraph for this community
            subgraph = undirected.subgraph(community)
            
            # Calculate metrics
            size = len(community)
            internal_edges = subgraph.number_of_edges()
            
            # Calculate possible internal edges
            possible_internal_edges = (size * (size - 1)) / 2
            internal_density = internal_edges / possible_internal_edges if possible_internal_edges > 0 else 0
            
            # Calculate external connections
            external_connections = 0
            for node in community:
                neighbors = set(undirected.neighbors(node))
                external_connections += len(neighbors - set(community))
            
            # Calculate cohesion (ratio of internal to all connections)
            total_connections = internal_edges + external_connections
            cohesion = internal_edges / total_connections if total_connections > 0 else 0
            
            # Calculate average clustering for community
            avg_clustering = nx.average_clustering(subgraph) if size > 1 else 0
            
            metrics.append({
                "Community ID": i + 1,
                "Size": size,
                "Internal Edges": internal_edges,
                "External Connections": external_connections,
                "Internal Density": internal_density,
                "Cohesion": cohesion,
                "Avg Clustering": avg_clustering
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_influence_score(self, user):
        """
        Calculate an influence score for a specific user.
        
        Args:
            user (str): Username to calculate score for
            
        Returns:
            float: Influence score (0-1)
        """
        if user not in self.network.graph:
            return 0.0
            
        # Get centrality measures
        centrality = self.get_user_centrality(user)
        
        # Combine measures with weights
        weights = {
            "degree_centrality": 0.3,
            "eigenvector_centrality": 0.3,
            "betweenness_centrality": 0.3,
            "closeness_centrality": 0.1
        }
        
        score = sum(centrality[measure] * weight for measure, weight in weights.items())
        
        # Normalize to 0-1 scale
        max_possible_score = sum(weights.values())
        normalized_score = score / max_possible_score
        
        return normalized_score
    
    def calculate_influence_scores(self):
        """
        Calculate influence scores for all users.
        
        Returns:
            dict: Dictionary mapping usernames to influence scores
        """
        scores = {}
        for user in self.network.graph.nodes():
            scores[user] = self.calculate_influence_score(user)
        return scores
    
    def simulate_information_spread(self, start_user, probability=0.5, iterations=10):
        """
        Simulate information spreading through the network.
        
        Args:
            start_user (str): Username where information starts
            probability (float): Probability of spreading to neighbors (0-1)
            iterations (int): Number of iterations to simulate
            
        Returns:
            dict: Dictionary mapping usernames to whether they received the information
        """
        if start_user not in self.network.graph:
            return {}
            
        G = self.network.graph
        
        # Track which users have the information
        informed = {user: False for user in G.nodes()}
        informed[start_user] = True
        
        # Perform iterations
        for _ in range(iterations):
            newly_informed = []
            
            # Check each informed user
            for user in [u for u, has_info in informed.items() if has_info]:
                # Try to spread to neighbors
                for neighbor in G.neighbors(user):
                    if not informed[neighbor]:
                        # Spread with probability
                        if random.random() < probability:
                            newly_informed.append(neighbor)
            
            # Update informed status
            for user in newly_informed:
                informed[user] = True
                
            # Stop if no new spreads
            if not newly_informed:
                break
        
        return informed
