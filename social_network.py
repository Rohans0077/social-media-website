import networkx as nx
from collections import defaultdict
import random
import re

class SocialNetwork:
    def __init__(self):
        """Initialize the social network with an empty directed graph."""
        self.graph = nx.DiGraph()

    def add_user(self, user, attributes=None):
        """
        Add a user to the network with optional attributes.
        
        Args:
            user (str): Username to add
            attributes (dict, optional): User attributes like name, age, etc.
        """
        if attributes is None:
            attributes = {}
        
        # Add required attributes if missing
        if "name" not in attributes:
            attributes["name"] = user
            
        self.graph.add_node(user, **attributes)

    def remove_user(self, user):
        """
        Remove a user from the network.
        
        Args:
            user (str): Username to remove
            
        Raises:
            ValueError: If user doesn't exist
        """
        if user in self.graph:
            self.graph.remove_node(user)
        else:
            raise ValueError(f"User '{user}' not found")

    def add_friendship(self, user1, user2, attributes=None):
        """
        Add a directional relationship from user1 to user2.
        
        Args:
            user1 (str): Source username
            user2 (str): Target username
            attributes (dict, optional): Relationship attributes like type, strength, etc.
            
        Raises:
            ValueError: If either user doesn't exist
        """
        if user1 not in self.graph:
            raise ValueError(f"User '{user1}' not found")
        if user2 not in self.graph:
            raise ValueError(f"User '{user2}' not found")
            
        # Set default attributes if none provided
        if attributes is None:
            attributes = {"type": "Friend", "strength": 5}
            
        self.graph.add_edge(user1, user2, **attributes)

    def remove_friendship(self, user1, user2):
        """
        Remove a relationship between users.
        
        Args:
            user1 (str): Source username
            user2 (str): Target username
            
        Raises:
            ValueError: If the relationship doesn't exist
        """
        if self.graph.has_edge(user1, user2):
            self.graph.remove_edge(user1, user2)
        else:
            raise ValueError(f"Relationship from '{user1}' to '{user2}' not found")

    def shortest_path(self, start, end):
        """
        Find the shortest path between two users.
        
        Args:
            start (str): Starting username
            end (str): Ending username
            
        Returns:
            list or str: The path as a list of usernames or an error message
        """
        try:
            return nx.shortest_path(self.graph, source=start, target=end)
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            return str(e)

    def recommend_friends(self, user):
        """
        Recommend potential friends based on mutual connections.
        
        Args:
            user (str): Username to get recommendations for
            
        Returns:
            list: List of (username, mutual_count) tuples, sorted by mutual count
        """
        if user not in self.graph:
            return []
        
        # Get current friends
        current_friends = set(self.graph.successors(user))
        
        # Count mutual friends
        mutual_friends = defaultdict(int)
        for friend in current_friends:
            for friend_of_friend in self.graph.successors(friend):
                if friend_of_friend != user and friend_of_friend not in current_friends:
                    mutual_friends[friend_of_friend] += 1
        
        # Sort by number of mutual friends
        return sorted(mutual_friends.items(), key=lambda x: x[1], reverse=True)

    def detect_communities(self, method="girvan_newman"):
        """
        Detect communities in the network.
        
        Args:
            method (str): Community detection method to use
            
        Returns:
            list: List of communities (each a list of usernames)
        """
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        if method == "girvan_newman":
            from networkx.algorithms.community import girvan_newman
            communities_generator = girvan_newman(undirected)
            # Take the first partition
            communities = next(communities_generator)
            return [list(c) for c in communities]
        
        elif method == "greedy_modularity":
            from networkx.algorithms.community import greedy_modularity_communities
            communities = list(greedy_modularity_communities(undirected))
            return [list(c) for c in communities]
            
        elif method == "label_propagation":
            from networkx.algorithms.community import label_propagation_communities
            communities = list(label_propagation_communities(undirected))
            return [list(c) for c in communities]
            
        elif method == "louvain":
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(undirected)
                communities = defaultdict(list)
                for node, community_id in partition.items():
                    communities[community_id].append(node)
                return list(communities.values())
            except ImportError:
                # Fall back to greedy_modularity if python-louvain not available
                from networkx.algorithms.community import greedy_modularity_communities
                communities = list(greedy_modularity_communities(undirected))
                return [list(c) for c in communities]
        
        else:
            # Default to girvan_newman
            from networkx.algorithms.community import girvan_newman
            communities_generator = girvan_newman(undirected)
            communities = next(communities_generator)
            return [list(c) for c in communities]

    def get_user_attributes(self, user):
        """
        Get all attributes for a user.
        
        Args:
            user (str): Username to get attributes for
            
        Returns:
            dict: Dictionary of user attributes
        """
        if user in self.graph:
            return dict(self.graph.nodes[user])
        return {}

    def update_user_attributes(self, user, attributes):
        """
        Update attributes for a user.
        
        Args:
            user (str): Username to update
            attributes (dict): New attributes to set
            
        Raises:
            ValueError: If user doesn't exist
        """
        if user in self.graph:
            for key, value in attributes.items():
                self.graph.nodes[user][key] = value
        else:
            raise ValueError(f"User '{user}' not found")

    def search_users(self, search_term):
        """
        Search for users by username or attributes.
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            list: List of matching usernames
        """
        search_term = search_term.lower()
        results = []
        
        for user in self.graph.nodes():
            # Search in username
            if search_term in user.lower():
                results.append(user)
                continue
                
            # Search in attributes
            attributes = self.get_user_attributes(user)
            for key, value in attributes.items():
                if value is not None and search_term in str(value).lower():
                    results.append(user)
                    break
        
        return results
