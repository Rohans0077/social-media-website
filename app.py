
# Author : Rohan.s
# usn: 1RV24SSE11




import streamlit as st

import pandas as pd
import numpy as np
import io
import base64
from PIL import Image

from social_network import SocialNetwork
from visualizations import NetworkVisualizer
from analytics import NetworkAnalytics
from data_manager import DataManager

# Set page config
st.set_page_config(
    page_title="Social Media Network by Rohan.S",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'network' not in st.session_state:
    st.session_state.network = SocialNetwork()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = NetworkVisualizer(st.session_state.network)
if 'analytics' not in st.session_state:
    st.session_state.analytics = NetworkAnalytics(st.session_state.network)
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager(st.session_state.network)
if 'visualization_type' not in st.session_state:
    st.session_state.visualization_type = "spring"
if 'node_color_option' not in st.session_state:
    st.session_state.node_color_option = "Default"
if 'current_communities' not in st.session_state:
    st.session_state.current_communities = None
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'highlighted_nodes' not in st.session_state:
    st.session_state.highlighted_nodes = []
if 'highlighted_edges' not in st.session_state:
    st.session_state.highlighted_edges = []

# Title and description
st.title("Dynamic Graph Algorithms for Social Network")
st.markdown("""
This application was created by Rohan S (1RV24SSE11)""")
st.markdown("""It allows you to create, visualize, and analyze social networks. 
You can add users, create connections, perform various analyses, and export results.
""")

# Sidebar for navigation

st.sidebar.title("Navigation page")
page = st.sidebar.radio(
    "Select a page",
    ["Network Management", "Visualization", "Contact Us", "User Profiles", "Import/Export"]
)

# Network Management Page
if page == "Network Management":
    st.header("Network Management")
    
    # Create two columns for user actions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Management")
        
        # Add User
        with st.expander("Add User"):
            with st.form("add_user_form"):
                username = st.text_input("Username")
                name = st.text_input("Full Name (optional)")
                age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0)
                gender = st.selectbox("Gender (optional)", ["", "Male", "Female", "Other"])
                location = st.text_input("Location (optional)")
                bio = st.text_area("Bio (optional)")
                
                submit_button = st.form_submit_button("Add User")
                if submit_button and username:
                    if username in st.session_state.network.graph:
                        st.error(f"User '{username}' already exists!")
                    else:
                        attributes = {
                            "name": name if name else username,
                            "age": age if age > 0 else None,
                            "gender": gender if gender else None,
                            "location": location if location else None,
                            "bio": bio if bio else None
                        }
                        st.session_state.network.add_user(username, attributes)
                        st.success(f"User '{username}' added successfully!")
                        st.session_state.visualizer.update_graph()
        
        # Remove User
        with st.expander("Remove User"):
            users = list(st.session_state.network.graph.nodes())
            if users:
                user_to_remove = st.selectbox("Select user to remove", users, key="remove_user")
                if st.button("Remove User", key="remove_user_button"):
                    try:
                        st.session_state.network.remove_user(user_to_remove)
                        st.success(f"User '{user_to_remove}' removed successfully!")
                        st.session_state.visualizer.update_graph()
                    except ValueError as e:
                        st.error(str(e))
            else:
                st.info("No users available to remove.")
                
        # Search Users
        with st.expander("Search Users"):
            search_term = st.text_input("Search by username or attributes")
            if search_term:
                results = st.session_state.network.search_users(search_term)
                if results:
                    st.write("Search Results:")
                    for user in results:
                        st.write(f"- {user}")
                        # Display user info in a small box
                        user_info = st.session_state.network.get_user_attributes(user)
                        if user_info:
                            with st.expander(f"Details for {user}"):
                                for key, value in user_info.items():
                                    if value is not None:
                                        st.write(f"{key.capitalize()}: {value}")
                else:
                    st.info("No users found matching your search.")
    
    with col2:
        st.subheader("Relationship Management")
        
        # Add Friendship
        with st.expander("Add Relationship"):
            users = list(st.session_state.network.graph.nodes())
            if len(users) >= 2:
                user1 = st.selectbox("Select first user", users, key="add_rel_user1")
                user2 = st.selectbox("Select second user", users, key="add_rel_user2")
                relationship_type = st.selectbox("Relationship Type", 
                                               ["Friend", "Family", "Colleague", "Acquaintance"],
                                               index=0)
                relationship_strength = st.slider("Relationship Strength", 1, 10, 5)
                
                if st.button("Add Relationship"):
                    if user1 == user2:
                        st.error("Cannot create a relationship with the same user.")
                    else:
                        try:
                            st.session_state.network.add_friendship(
                                user1, user2, 
                                {"type": relationship_type, "strength": relationship_strength}
                            )
                            st.success(f"Relationship from {user1} to {user2} added successfully!")
                            st.session_state.visualizer.update_graph()
                        except ValueError as e:
                            st.error(str(e))
            else:
                st.info("Add at least two users to create relationships.")
        
        # Remove Friendship
        with st.expander("Remove Relationship"):
            users = list(st.session_state.network.graph.nodes())
            if len(users) >= 2:
                user1 = st.selectbox("Select first user", users, key="remove_rel_user1")
                
                # Get connected users for the selected user
                connected_users = list(st.session_state.network.graph.successors(user1)) if user1 in st.session_state.network.graph else []
                
                if connected_users:
                    user2 = st.selectbox("Select second user", connected_users, key="remove_rel_user2")
                    if st.button("Remove Relationship"):
                        try:
                            st.session_state.network.remove_friendship(user1, user2)
                            st.success(f"Relationship from {user1} to {user2} removed successfully!")
                            st.session_state.visualizer.update_graph()
                        except ValueError as e:
                            st.error(str(e))
                else:
                    st.info(f"User '{user1}' has no outgoing relationships.")
            else:
                st.info("Add at least two users to manage relationships.")
                
        # Find Path Between Users
        with st.expander("Find Path Between Users"):
            users = list(st.session_state.network.graph.nodes())
            if len(users) >= 2:
                start_user = st.selectbox("Select start user", users, key="path_start_user")
                end_user = st.selectbox("Select end user", users, key="path_end_user")
                
                if st.button("Find Shortest Path"):
                    if start_user == end_user:
                        st.info("Start and end users are the same.")
                    else:
                        path = st.session_state.network.shortest_path(start_user, end_user)
                        if isinstance(path, list):
                            st.success(f"Shortest path found with {len(path)-1} steps")
                            st.write(" → ".join(path))
                            
                            # Highlight the path in the graph
                            st.session_state.highlighted_nodes = path
                            st.session_state.highlighted_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                            
                            # Create a button to visualize this path
                            if st.button("Visualize This Path"):
                                st.session_state.visualization_type = "spring"  # Set a good layout for path visualization
                                st.session_state.selected_user = None
                                st.session_state.current_communities = None
                                st.session_state.node_color_option = "Default"
                                st.session_state.visualizer.update_graph()
                                st.session_state.page = "Visualization"
                                st.rerun()
                        else:
                            st.error(f"No path found: {path}")
            else:
                st.info("Add at least two users to find paths.")
                
    # Display current network summary
    st.subheader("Current Network Summary")
    num_users = st.session_state.network.graph.number_of_nodes()
    num_relationships = st.session_state.network.graph.number_of_edges()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", num_users)
    with col2:
        st.metric("Total Relationships", num_relationships)
    with col3:
        if num_users > 0:
            density = nx.density(st.session_state.network.graph)
            st.metric("Network Density", f"{density:.4f}")
        else:
            st.metric("Network Density", "N/A")
    
    # Show a basic visualization of the current network
    if num_users > 0:
        st.write("Current Network Visualization:")
        fig = st.session_state.visualizer.get_visualization("spring", node_color="Default")
        st.pyplot(fig)

# Visualization Page
elif page == "Visualization":
    st.header("Network Visualization")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("Visualization Settings")
        
        # Layout selection
        layout_options = {
            "spring": "Spring Layout (Force-Directed)",
            
            "random": "Random Layout"
            
        }
        selected_layout = st.selectbox(
            "Select Layout Algorithm",
            list(layout_options.keys()),
            format_func=lambda x: layout_options[x],
            index=list(layout_options.keys()).index(st.session_state.visualization_type)
        )
        
        # Node coloring options
        color_options = {
            "Default": "Default (Single Color)",
            "Degree": "Node Degree (Popularity)",
            "Communities": "Communities",
            "Centrality": "Centrality (Importance)",
            "Attribute": "User Attribute"
        }
        selected_color = st.selectbox(
            "Node Coloring",
            list(color_options.keys()),
            format_func=lambda x: color_options[x],
            index=list(color_options.keys()).index(st.session_state.node_color_option)
        )
        
        # If attribute-based coloring is selected
        attribute_to_color = None
        if selected_color == "Attribute":
            attributes = ["name", "age", "gender", "location"]
            attribute_to_color = st.selectbox("Select attribute for coloring", attributes)
        
        # User highlighting
        users = list(st.session_state.network.graph.nodes())
        if users:
            highlight_user = st.selectbox(
                "Highlight User and Connections",
                ["None"] + users,
                index=0
            )
            if highlight_user != "None":
                st.session_state.selected_user = highlight_user
            else:
                st.session_state.selected_user = None
                
        # Community detection option
        if st.button("Detect and Visualize Communities"):
            with st.spinner("Detecting communities..."):
                st.session_state.current_communities = st.session_state.network.detect_communities()
                st.session_state.node_color_option = "Communities"
                # Force update
                selected_color = "Communities"
                st.success(f"Detected {len(st.session_state.current_communities)} communities")
        
        # Update visualization based on settings
        if (selected_layout != st.session_state.visualization_type or 
            selected_color != st.session_state.node_color_option):
            st.session_state.visualization_type = selected_layout
            st.session_state.node_color_option = selected_color
    
    with col1:
        if len(st.session_state.network.graph.nodes()) > 0:
            # Generate the visualization
            fig = st.session_state.visualizer.get_visualization(
                st.session_state.visualization_type,
                node_color=st.session_state.node_color_option,
                highlighted_user=st.session_state.selected_user,
                communities=st.session_state.current_communities,
                highlighted_nodes=st.session_state.highlighted_nodes,
                highlighted_edges=st.session_state.highlighted_edges,
                attribute_to_color=attribute_to_color
            )
            st.pyplot(fig)
            
            # Export options
            st.subheader("Export Visualization")
            export_format = st.selectbox("Export Format", ["PNG", "SVG"])
            if st.button("Export Visualization"):
                buf = io.BytesIO()
                fig.savefig(buf, format=export_format.lower(), dpi=300, bbox_inches='tight')
                buf.seek(0)
                
                btn = st.download_button(
                    label=f"Download {export_format}",
                    data=buf,
                    file_name=f"social_network.{export_format.lower()}",
                    mime=f"image/{export_format.lower()}"
                )
        else:
            st.info("Add users and relationships to visualize the network.")
            
    # Clear any highlights
    if st.sidebar.button("Clear Highlights"):
        st.session_state.highlighted_nodes = []
        st.session_state.highlighted_edges = []
        st.session_state.selected_user = None
        st.rerun()

#Contact US page
elif page == "Contact Us":
    st.header("Rohan S")
    
    if len(st.session_state.network.graph.nodes()) == 0:
        st.info("Below are the contact Details to contact the Owner.")
   
        tab1, tab2, tab3, tab4,tab5 = st.tabs(["About Me","LinkedIn","GitHub","Gmail","Location"])
        
        with tab1:
            st.subheader("Phone Number: +91 9110876625")
            st.image("rohan.jpg", use_column_width="50px" )
            st.write("""
                                                      
I am a highly motivated and meticulous Programmer with experience in Web development and AI, ML model development. I 
have a deep understanding of how systems work and their Interrelations. My expertise in data structures and Algorithms further 
strengthens my abilities, making me an exceptional candidate for Software Developer role. I have a proven track record of 
delivering high-quality results and am confident in my ability to drive impactful solutions and contribute to your organization's 
success. 
""")
            
            
            
        with tab2:
            st.subheader("Link - https://www.linkedin.com/in/rohan-s-85143922a/")
            
        with tab3:
            st.subheader("Link - https://github.com/Rohans0077")
                    
                   
                  
        with tab4:
            st.subheader("Gmail 1 - roh142002@gmail.com")
            
            # Information spreaders analysis
            st.subheader("Gmail 2 - rohans.sse24@rvce.edu.in")
            
        with tab5:
            st.subheader("RV COLLEGE OF ENGINEERING")
            
            # Information spreaders analysis
            st.subheader("India,  Bangalore- 560072")
                 
                    
                   

# User Profiles Page
elif page == "User Profiles":
    st.header("User Profiles")
    
    users = list(st.session_state.network.graph.nodes())
    
    if not users:
        st.info("No users in the network. Add some users first.")
    else:
        # User search and selection
        search_term = st.text_input("Search Users", "")
        
        filtered_users = users
        if search_term:
            filtered_users = [user for user in users if search_term.lower() in user.lower()]
        
        selected_user = st.selectbox("Select a user to view or edit profile", filtered_users) if filtered_users else None
        
        if selected_user:
            st.subheader(f"Profile: {selected_user}")
            
            user_attributes = st.session_state.network.get_user_attributes(selected_user)
            
            # Display and edit user information
            with st.expander("View and Edit User Information", expanded=True):
                with st.form("edit_profile_form"):
                    name = st.text_input("Full Name", user_attributes.get("name", ""))
                    age = st.number_input("Age", min_value=0, max_value=120, value=user_attributes.get("age", 0) or 0)
                    gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], 
                                         index=["", "Male", "Female", "Other"].index(user_attributes.get("gender", "")) if user_attributes.get("gender", "") in ["", "Male", "Female", "Other"] else 0)
                    location = st.text_input("Location", user_attributes.get("location", ""))
                    bio = st.text_area("Bio", user_attributes.get("bio", ""))
                    
                    submit_button = st.form_submit_button("Update Profile")
                    if submit_button:
                        updated_attributes = {
                            "name": name if name else selected_user,
                            "age": age if age > 0 else None,
                            "gender": gender if gender else None,
                            "location": location if location else None,
                            "bio": bio if bio else None
                        }
                        st.session_state.network.update_user_attributes(selected_user, updated_attributes)
                        st.success(f"Profile for {selected_user} updated successfully!")
            
            # Display user connections
            with st.expander("User Connections", expanded=True):
                # Outgoing connections
                outgoing = list(st.session_state.network.graph.successors(selected_user))
                st.write(f"Outgoing Connections ({len(outgoing)}):")
                if outgoing:
                    for connection in outgoing:
                        edge_data = st.session_state.network.graph.get_edge_data(selected_user, connection)
                        relationship_type = edge_data.get("type", "Friend") if edge_data else "Friend"
                        relationship_strength = edge_data.get("strength", 5) if edge_data else 5
                        st.write(f"→ {connection} ({relationship_type}, Strength: {relationship_strength})")
                        
                        # Option to edit or remove this connection
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            if st.button(f"Edit", key=f"edit_{selected_user}_{connection}"):
                                st.session_state.edit_connection = (selected_user, connection)
                                st.rerun()
                        with col2:
                            if st.button(f"Remove", key=f"remove_{selected_user}_{connection}"):
                                try:
                                    st.session_state.network.remove_friendship(selected_user, connection)
                                    st.success(f"Relationship from {selected_user} to {connection} removed!")
                                    st.session_state.visualizer.update_graph()
                                    st.rerun()
                                except ValueError as e:
                                    st.error(str(e))
                else:
                    st.write("No outgoing connections.")
                
                # Incoming connections
                incoming = [node for node in st.session_state.network.graph.nodes() 
                            if selected_user in st.session_state.network.graph.successors(node)]
                st.write(f"Incoming Connections ({len(incoming)}):")
                if incoming:
                    for connection in incoming:
                        edge_data = st.session_state.network.graph.get_edge_data(connection, selected_user)
                        relationship_type = edge_data.get("type", "Friend") if edge_data else "Friend"
                        relationship_strength = edge_data.get("strength", 5) if edge_data else 5
                        st.write(f"← {connection} ({relationship_type}, Strength: {relationship_strength})")
                else:
                    st.write("No incoming connections.")
            
            # Display analytics for this user
            with st.expander("User Analytics", expanded=True):
                centrality_measures = st.session_state.analytics.get_user_centrality(selected_user)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Degree Centrality", f"{centrality_measures['degree_centrality']:.4f}")
                    st.caption("Measure of direct connections")
                    
                    st.metric("Eigenvector Centrality", f"{centrality_measures['eigenvector_centrality']:.4f}")
                    st.caption("Measure of connection to important nodes")
                    
                with col2:
                    st.metric("Betweenness Centrality", f"{centrality_measures['betweenness_centrality']:.4f}")
                    st.caption("Measure of how often this user is on the shortest path between others")
                    
                    st.metric("Closeness Centrality", f"{centrality_measures['closeness_centrality']:.4f}")
                    st.caption("Measure of how close this user is to all others")
                
                # User's influence score
                influence_score = st.session_state.analytics.calculate_influence_score(selected_user)
                st.metric("Overall Influence Score", f"{influence_score:.4f}")
                st.caption("Combined measure of user's importance in the network")
                
                # Recommend friends for this user
                st.subheader("Friend Recommendations")
                recommendations = st.session_state.network.recommend_friends(selected_user)
                
                if recommendations:
                    st.write("People you might know:")
                    for user, mutual_count in recommendations:
                        st.write(f"- {user} ({mutual_count} mutual connections)")
                        if st.button(f"Add Connection to {user}", key=f"add_rec_{selected_user}_{user}"):
                            try:
                                st.session_state.network.add_friendship(
                                    selected_user, user, 
                                    {"type": "Friend", "strength": 5}
                                )
                                st.success(f"Relationship from {selected_user} to {user} added!")
                                st.session_state.visualizer.update_graph()
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                else:
                    st.write("No friend recommendations available.")

# Import/Export Page
elif page == "Import/Export":
    st.header("Import/Export Data")
    
    tab1, tab2 = st.tabs(["Export", "Import"])
    
    with tab1:
        st.subheader("Export Network Data")
        
        export_format = st.selectbox(
            "Export Format",
            [ "CSV"]
        )
        
        if st.button("Export Network"):
            data = st.session_state.data_manager.export_network(export_format)
            
            file_extension = {
               
                "CSV": "csv"
            }
            
            st.download_button(
                label=f"Download {export_format} File",
                data=data,
                file_name=f"social_network.{file_extension[export_format]}",
                mime="text/plain"
            )
            
        # Export analytics data
        st.subheader("Export Analytics")
        
        analytics_options = [
            "User Centrality Measures",
            "Community Analysis",
            "Network Metrics"
        ]
        
        analytics_export = st.selectbox("Select Analytics to Export", analytics_options)
        
        if st.button("Export Analytics"):
            analytics_data = st.session_state.data_manager.export_analytics(analytics_export)
            
            st.download_button(
                label="Download Analytics CSV",
                data=analytics_data,
                file_name=f"social_network_{analytics_export.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.subheader("Import Network Data")
        
        import_format = st.selectbox(
            "Import Format",
            ["CSV"]
        )
        
        uploaded_file = st.file_uploader("Upload network file", type=[ "csv"])
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                file_content = uploaded_file.getvalue().decode("utf-8")
                
                # Ask user if they want to replace or merge with existing network
                import_action = st.radio("Import Action", ["Replace existing network", "Merge with existing network"])
                
                if st.button("Import Network"):
                    replace = import_action == "Replace existing network"
                    success = st.session_state.data_manager.import_network(file_content, import_format, replace)
                    
                    if success:
                        st.success("Network imported successfully!")
                        st.session_state.visualizer.update_graph()
                        # Force a rerun to update the visualization
                        st.rerun()
                    else:
                        st.error("Failed to import network. Check the file format.")
            except Exception as e:
                st.error(f"Error importing file: {str(e)}")

# Add a footer
st.sidebar.markdown("---")
st.sidebar.info("All rights Reserved, Copyrights  - 2024-25 ")

# Reset highlighted elements when changing pages
if 'last_page' not in st.session_state:
    st.session_state.last_page = page
elif st.session_state.last_page != page:
    st.session_state.highlighted_nodes = []
    st.session_state.highlighted_edges = []
    st.session_state.last_page = page
