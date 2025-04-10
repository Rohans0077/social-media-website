import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import Patch

class NetworkVisualizer:
    def __init__(self, network):
        """
        Initialize the visualizer with a social network instance.
        
        Args:
            network (SocialNetwork): The social network to visualize
        """
        self.network = network
        self.fig = None
        self.ax = None
        self.pos = None
        self.node_size = 800
        self.edge_width = 1.5
        self.font_size = 10
        self.arrow_size = 15
        
        # Color palettes
        self.community_colors = plt.cm.tab20
        self.default_node_color = '#1f78b4'  # Default blue
        self.highlight_color = 'red'
        self.edge_color = '#666666'
        self.highlighted_edge_color = 'red'
        
    def update_graph(self):
        """Update the graph layout if needed"""
        # This will be called when the network changes
        self.pos = None
    
    def get_layout(self, layout_type):
        """
        Get node positions using the specified layout algorithm.
        
        Args:
            layout_type (str): Layout algorithm to use
            
        Returns:
            dict: Node positions
        """
        G = self.network.graph
        
        layout_functions = {
            "spring": nx.spring_layout,
           
            "random": nx.random_layout
          
        }
        
        if layout_type in layout_functions:
            return layout_functions[layout_type](G, seed=42)
        else:
            # Default to spring layout
            return nx.spring_layout(G, seed=42)
    
    def get_node_colors(self, node_color_option, communities=None, attribute_to_color=None):
        """
        Get node colors based on selected coloring option.
        
        Args:
            node_color_option (str): Coloring method to use
            communities (list, optional): List of communities if community coloring is used
            attribute_to_color (str, optional): Attribute to use for coloring if attribute-based
            
        Returns:
            list: List of node colors
        """
        G = self.network.graph
        nodes = list(G.nodes())
        
        if not nodes:
            return []
            
        if node_color_option == "Default":
            return [self.default_node_color] * len(nodes)
            
        elif node_color_option == "Degree":
            # Color by node degree (number of connections)
            degrees = [G.degree(node) for node in nodes]
            if max(degrees) == min(degrees):
                # If all nodes have the same degree, use default color
                return [self.default_node_color] * len(nodes)
            else:
                # Normalize degrees to [0, 1] for color mapping
                norm_degrees = [(d - min(degrees)) / (max(degrees) - min(degrees)) for d in degrees]
                cmap = plt.cm.viridis
                return [cmap(d) for d in norm_degrees]
                
        elif node_color_option == "Communities" and communities:
            # Assign colors by community
            node_to_community = {}
            for i, community in enumerate(communities):
                for node in community:
                    node_to_community[node] = i
            
            colors = []
            for node in nodes:
                if node in node_to_community:
                    community_idx = node_to_community[node]
                    colors.append(self.community_colors(community_idx % 20))
                else:
                    colors.append(self.default_node_color)
            return colors
            
        elif node_color_option == "Centrality":
            # Color by eigenvector centrality (importance)
            try:
                centrality = nx.eigenvector_centrality(G)
                centrality_values = [centrality[node] for node in nodes]
                if max(centrality_values) == min(centrality_values):
                    return [self.default_node_color] * len(nodes)
                else:
                    norm_centrality = [(c - min(centrality_values)) / (max(centrality_values) - min(centrality_values)) 
                                    for c in centrality_values]
                    cmap = plt.cm.coolwarm
                    return [cmap(c) for c in norm_centrality]
            except:
                # In case of convergence failure, fallback to degree centrality
                centrality = nx.degree_centrality(G)
                centrality_values = [centrality[node] for node in nodes]
                if max(centrality_values) == min(centrality_values):
                    return [self.default_node_color] * len(nodes)
                else:
                    norm_centrality = [(c - min(centrality_values)) / (max(centrality_values) - min(centrality_values)) 
                                    for c in centrality_values]
                    cmap = plt.cm.coolwarm
                    return [cmap(c) for c in norm_centrality]
                
        elif node_color_option == "Attribute" and attribute_to_color:
            # Color by a specific attribute
            attribute_values = {}
            unique_values = set()
            
            # Collect all values of the attribute
            for node in nodes:
                attrs = self.network.get_user_attributes(node)
                if attribute_to_color in attrs and attrs[attribute_to_color] is not None:
                    value = attrs[attribute_to_color]
                    attribute_values[node] = value
                    unique_values.add(value)
                else:
                    attribute_values[node] = None
            
            # Map unique values to colors
            unique_values = sorted([v for v in unique_values if v is not None])
            value_to_color = {}
            cmap = plt.cm.tab10
            
            for i, value in enumerate(unique_values):
                value_to_color[value] = cmap(i % 10)
            
            # Assign colors based on attribute values
            colors = []
            for node in nodes:
                value = attribute_values[node]
                if value is not None and value in value_to_color:
                    colors.append(value_to_color[value])
                else:
                    colors.append('#cccccc')  # Gray for missing values
            
            return colors
            
        else:
            # Default case
            return [self.default_node_color] * len(nodes)
    
    def get_visualization(self, layout_type="spring", node_color="Default", 
                         highlighted_user=None, communities=None,
                         highlighted_nodes=None, highlighted_edges=None,
                         attribute_to_color=None):
        """
        Generate a visualization of the network.
        
        Args:
            layout_type (str): Layout algorithm to use
            node_color (str): Coloring method to use
            highlighted_user (str, optional): Username to highlight
            communities (list, optional): List of communities if community coloring is used
            highlighted_nodes (list, optional): List of nodes to highlight
            highlighted_edges (list, optional): List of edges to highlight
            attribute_to_color (str, optional): Attribute to use for coloring if attribute-based
            
        Returns:
            matplotlib.figure.Figure: The generated visualization
        """
        G = self.network.graph
        
        # Create figure and axes
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.clear()
        
        if len(G.nodes()) == 0:
            self.ax.text(0.5, 0.5, "No users in the network", 
                      horizontalalignment='center', verticalalignment='center',
                      transform=self.ax.transAxes, fontsize=14)
            return self.fig
        
        # Get or calculate node positions
        self.pos = self.get_layout(layout_type)
        
        # Get node colors based on selected option
        node_colors = self.get_node_colors(node_color, communities, attribute_to_color)
        
        # Draw nodes
        nodes = list(G.nodes())
        
        # Create a copy for the highlighted state
        node_colors_with_highlights = node_colors.copy()
        node_sizes = [self.node_size] * len(nodes)
        
        # Handle highlighted user
        if highlighted_user and highlighted_user in G:
            for i, node in enumerate(nodes):
                if node == highlighted_user:
                    node_colors_with_highlights[i] = self.highlight_color
                    node_sizes[i] = self.node_size * 1.3
        
        # Handle highlighted nodes list
        if highlighted_nodes:
            for i, node in enumerate(nodes):
                if node in highlighted_nodes:
                    node_colors_with_highlights[i] = self.highlight_color
                    node_sizes[i] = self.node_size * 1.3
        
        # Draw all edges first with default styling
        edges = list(G.edges())
        edge_colors = [self.edge_color] * len(edges)
        edge_widths = [self.edge_width] * len(edges)
        
        # Handle highlighted edges
        if highlighted_edges:
            for i, (u, v) in enumerate(edges):
                if (u, v) in highlighted_edges:
                    edge_colors[i] = self.highlighted_edge_color
                    edge_widths[i] = self.edge_width * 2
        
        # Draw edges and nodes
        nx.draw_networkx_edges(
            G, self.pos, 
            edgelist=edges,
            ax=self.ax,
            edge_color=edge_colors,
            width=edge_widths,
            arrowsize=self.arrow_size,
            arrows=True
        )
        
        nx.draw_networkx_nodes(
            G, self.pos,
            nodelist=nodes,
            node_color=node_colors_with_highlights,
            node_size=node_sizes,
            ax=self.ax,
            alpha=0.8
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            G, self.pos,
            font_size=self.font_size,
            font_weight='bold',
            ax=self.ax
        )
        
        # Add a legend for special coloring modes
        if node_color == "Communities" and communities:
            # Create legend for communities
            legend_elements = []
            
            for i, community in enumerate(communities):
                if i < 20:  # Show up to 20 communities in legend
                    color = self.community_colors(i % 20)
                    legend_elements.append(
                        Patch(facecolor=color, edgecolor='black',
                              label=f'Community {i+1} ({len(community)} members)')
                    )
            
            self.ax.legend(handles=legend_elements, loc='upper right', 
                        title="Communities", fontsize='small')
                        
        elif node_color == "Degree":
            # Add a colorbar for degree
            norm = plt.Normalize(
                min([G.degree(node) for node in G.nodes()]),
                max([G.degree(node) for node in G.nodes()])
            )
            sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=self.ax)
            cbar.set_label('Node Degree (Connections)')
            
        elif node_color == "Centrality":
            # Add a colorbar for centrality
            try:
                centrality_values = list(nx.eigenvector_centrality(G).values())
            except:
                centrality_values = list(nx.degree_centrality(G).values())
                
            norm = plt.Normalize(min(centrality_values), max(centrality_values))
            sm = plt.cm.ScalarMappable(cmap=plt.cm.coolwarm, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=self.ax)
            cbar.set_label('Centrality (Importance)')
            
        elif node_color == "Attribute" and attribute_to_color:
            # Add a legend for attribute values
            attribute_values = {}
            unique_values = set()
            
            # Collect values
            for node in G.nodes():
                attrs = self.network.get_user_attributes(node)
                if attribute_to_color in attrs and attrs[attribute_to_color] is not None:
                    value = attrs[attribute_to_color]
                    attribute_values[node] = value
                    unique_values.add(value)
            
            # Create legend
            unique_values = sorted([v for v in unique_values if v is not None])
            legend_elements = []
            cmap = plt.cm.tab10
            
            for i, value in enumerate(unique_values):
                if i < 10:  # Limit to 10 legend items
                    color = cmap(i % 10)
                    legend_elements.append(
                        Patch(facecolor=color, edgecolor='black', label=str(value))
                    )
            
            if legend_elements:
                self.ax.legend(handles=legend_elements, loc='upper right', 
                            title=attribute_to_color.capitalize(), fontsize='small')
        
        # Remove axis
        plt.axis('off')
        
        # Add a title with network stats
        num_users = G.number_of_nodes()
        num_relationships = G.number_of_edges()
        self.fig.suptitle(
            f"Social Network - {num_users} Users, {num_relationships} Relationships",
            fontsize=16
        )
        
        plt.tight_layout()
        return self.fig
