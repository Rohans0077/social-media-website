import networkx as nx
import pandas as pd
import io
import csv
import json

class DataManager:
    def __init__(self, network):
        """
        Initialize the data manager with a social network instance.
        
        Args:
            network (SocialNetwork): The social network to manage data for
        """
        self.network = network
    
    def export_network(self, format_type):
        """
        Export the network to various file formats.
        
        Args:
            format_type (str): Format to export (GraphML, GML, etc.)
            
        Returns:
            str: String representation of the exported network
        """
        G = self.network.graph
        output = io.StringIO()
        
        if format_type == "GraphML":
            nx.write_graphml(G, output)
        
        elif format_type == "GML":
            nx.write_gml(G, output)
        
        elif format_type == "GEXF":
            nx.write_gexf(G, output)
        
        elif format_type == "Adjacency List":
            nx.write_adjlist(G, output)
        
        elif format_type == "Edge List":
            nx.write_edgelist(G, output)
        
        elif format_type == "CSV":
            # Export nodes with attributes
            nodes_data = []
            for node in G.nodes():
                node_data = {"id": node}
                node_data.update(G.nodes[node])
                nodes_data.append(node_data)
            
            # Export edges with attributes
            edges_data = []
            for u, v, data in G.edges(data=True):
                edge_data = {"source": u, "target": v}
                edge_data.update(data)
                edges_data.append(edge_data)
            
            # Combine into a single string
            output.write("# NODES\n")
            if nodes_data:
                pd.DataFrame(nodes_data).to_csv(output, index=False)
            else:
                output.write("id\n")
            
            output.write("\n# EDGES\n")
            if edges_data:
                pd.DataFrame(edges_data).to_csv(output, index=False)
            else:
                output.write("source,target\n")
        
        value = output.getvalue()
        output.close()
        return value
    
    def import_network(self, file_content, format_type, replace=True):
        """
        Import a network from a file.
        
        Args:
            file_content (str): Content of the file to import
            format_type (str): Format of the file (GraphML, GML, etc.)
            replace (bool): Whether to replace or merge with existing network
            
        Returns:
            bool: Success status
        """
        input_file = io.StringIO(file_content)
        new_graph = None
        
        try:
            if format_type == "GraphML":
                new_graph = nx.read_graphml(input_file)
            
            elif format_type == "GML":
                new_graph = nx.read_gml(input_file)
            
            elif format_type == "GEXF":
                new_graph = nx.read_gexf(input_file)
            
            elif format_type == "Adjacency List":
                new_graph = nx.read_adjlist(input_file)
            
            elif format_type == "Edge List":
                new_graph = nx.read_edgelist(input_file)
            
            elif format_type == "CSV":
                # Parse the CSV format
                lines = file_content.split('\n')
                
                # Find the boundary between nodes and edges
                edge_section_start = -1
                for i, line in enumerate(lines):
                    if line.strip() == "# EDGES":
                        edge_section_start = i
                        break
                
                if edge_section_start == -1:
                    raise ValueError("Invalid CSV format: Missing '# EDGES' section")
                
                # Parse nodes
                nodes_content = '\n'.join(lines[1:edge_section_start])
                nodes_df = pd.read_csv(io.StringIO(nodes_content))
                
                # Parse edges
                edges_content = '\n'.join(lines[edge_section_start+1:])
                edges_df = pd.read_csv(io.StringIO(edges_content))
                
                # Create a new graph
                new_graph = nx.DiGraph()
                
                # Add nodes with attributes
                for _, row in nodes_df.iterrows():
                    attrs = {k: row[k] for k in row.index if k != 'id'}
                    new_graph.add_node(row['id'], **attrs)
                
                # Add edges with attributes
                for _, row in edges_df.iterrows():
                    attrs = {k: row[k] for k in row.index if k not in ['source', 'target']}
                    new_graph.add_edge(row['source'], row['target'], **attrs)
            
            # Apply the imported network
            if new_graph is not None:
                if replace:
                    # Replace the current graph
                    self.network.graph = new_graph
                else:
                    # Merge with existing graph
                    self.network.graph.add_nodes_from(new_graph.nodes(data=True))
                    self.network.graph.add_edges_from(new_graph.edges(data=True))
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Import error: {str(e)}")
            return False
        finally:
            input_file.close()
    
    def export_analytics(self, analytics_type):
        """
        Export analytics data to CSV.
        
        Args:
            analytics_type (str): Type of analytics to export
            
        Returns:
            str: CSV data as string
        """
        from analytics import NetworkAnalytics
        analytics = NetworkAnalytics(self.network)
        
        output = io.StringIO()
        
        if analytics_type == "User Centrality Measures":
            # Export centrality measures
            centrality_measures = analytics.get_centrality_measures()
            
            if centrality_measures:
                # Convert to DataFrame
                data = []
                for user, measures in centrality_measures.items():
                    row = {"User": user}
                    row.update(measures)
                    data.append(row)
                
                df = pd.DataFrame(data)
                
                # Calculate overall score
                df['overall_influence'] = (df['degree_centrality'] + 
                                          df['eigenvector_centrality'] + 
                                          df['betweenness_centrality'] + 
                                          df['closeness_centrality']) / 4
                
                # Sort by influence
                df = df.sort_values('overall_influence', ascending=False)
                
                df.to_csv(output, index=False)
            else:
                output.write("No data available")
        
        elif analytics_type == "Community Analysis":
            # Detect communities
            communities = analytics.detect_communities()
            
            # Get community metrics
            metrics = analytics.get_community_metrics(communities)
            
            if not metrics.empty:
                metrics.to_csv(output, index=False)
            else:
                output.write("No community data available")
        
        elif analytics_type == "Network Metrics":
            # Calculate various network metrics
            metrics = {
                "Network Density": analytics.get_density(),
                "Average Clustering": analytics.get_avg_clustering(),
                "Average Path Length": analytics.get_avg_path_length(),
                "Number of Connected Components": analytics.get_num_connected_components(),
                "Degree Assortativity": analytics.get_degree_assortativity()
            }
            
            # Convert to DataFrame
            df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
            df.to_csv(output, index=False)
        
        value = output.getvalue()
        output.close()
        return value
