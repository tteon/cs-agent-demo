import networkx as nx
from pyvis.network import Network
import mgclient

# Function to connect to Memgraph and query graph data
def get_memgraph_data():
    # Connect to Memgraph
    connection = mgclient.connect(host='localhost', port=7687)
    cursor = connection.cursor()

    # Query nodes and relationships from Memgraph
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    cursor.execute(query)

    # Create a list to hold edges and nodes
    nodes = set()
    edges = []

    # Parse the results from Memgraph
    for record in cursor.fetchall():
        node1, relation, node2 = record
        
        # Extract node identifiers
        node1_id = node1.properties.get("id", str(node1.id))
        node2_id = node2.properties.get("id", str(node2.id))

        # Add nodes and edge
        nodes.add(node1_id)
        nodes.add(node2_id)
        edges.append((node1_id, node2_id))

    # Close the connection
    cursor.close()
    connection.close()

    return nodes, edges

# Function to visualize graph using PyVis
def visualize_graph(nodes, edges):
    # Create a NetworkX graph
    G = nx.Graph()

    # Add nodes and edges to the graph
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # Create a PyVis network for visualization
    net = Network(notebook=False, height="750px", width="100%", directed=True)

    # Convert NetworkX graph to PyVis
    net.from_nx(G)

    # Display the network graph
    net.show("memgraph_visualization.html")

# Main function to get data and visualize
if __name__ == "__main__":
    # Fetch data from Memgraph
    nodes, edges = get_memgraph_data()

    # Visualize the data
    visualize_graph(nodes, edges)

