import streamlit as st
import requests
from pyvis.network import Network
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Get username and password from environment variables
VALID_USERNAME = os.getenv("VALID_USERNAME")
VALID_PASSWORD = os.getenv("VALID_PASSWORD")

# Load and display the logo at the top of the page
st.markdown(
    """
    <style>
        .header {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .header img {
            width: 100px;
        }
        .header h1 {
            color: #4CAF50;  /* You can choose your brand color */
            font-size: 2.5em;
        }
        .stTextInput > div > input {
            background-color: #f9f9f9;
            padding: 10px;
        }
        .reportview-container {
            background: #FFFFFF;
        }
        .css-18e3th9 {
            padding-top: 2rem;  /* Extra padding for a nice look */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load and display the logo at the top of the page
logo = Image.open("./image/logo.png")
st.image(logo, width=100)  # Adjust the width as needed
# Authentication Functionality
st.header("Chain-insights ai fund flow AGI - demo(test)", divider=True)

def authenticate(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

# Login Box Layout
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.subheader("Login to Access Application")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.success("Successfully authenticated!")
        else:
            st.sidebar.error("Invalid username or password.")
else:
    # Split into two columns for better layout
    col1, col2 = st.columns([2, 3])  # First column for input, second for output

    with col1:
        st.subheader("Cypher Query Input")
        user_query = st.text_area("Enter your query below:", height=300)
        if st.button("Generate and Visualize"):
            if user_query.strip():
                # API call to generate and get records
                API_URL = "http://3.91.230.242:8000/generate-query/"
                with st.spinner("Generating Cypher query and fetching results..."):
                    try:
                        response = requests.post(API_URL, json={"text": user_query})

                        if response.status_code == 200:
                            print(response)
                            data = response.json()
                            results = data.get("results", [])

                            if results:
                                st.success("Query successfully executed. Visualizing...")
                                
                                # Visualization using PyVis
                                net = Network(notebook=False, height="500px", width="100%", directed=True, cdn_resources='in_line')

                                # Assuming nodes are address and transaction data based on result schema
                                for record in results:
                                    from_address = record.get("sender_address")
                                    to_address = record.get("receiver_address")
                                    timestamp = record.get("t.timestamp")
                                    block_height = record.get("t.block_height")
                                    in_total_amount = record.get("t.in_total_amount")
                                    out_total_amount = record.get("t.out_total_amount")

                                    if from_address and to_address:
                                        formatted_time = (
                                            datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
                                            if timestamp else "Unknown"
                                        )

                                        net.add_node(from_address, label=from_address, title=f"From Address: {from_address}", color='blue')
                                        net.add_node(to_address, label=to_address, title=f"To Address: {to_address}", color='green')

                                        edge_title = (f"Block Height: {block_height}, "
                                                      f"Timestamp: {formatted_time}, "
                                                      f"In Total Amount: {in_total_amount}, "
                                                      f"Out Total Amount: {out_total_amount}")

                                        net.add_edge(from_address, to_address, title=edge_title, color='black')

                                net.show_buttons(filter_=['physics'])
                                net.save_graph("cypher_query_visualization.html")

                                # Display HTML in Streamlit
                                with col2:
                                    HtmlFile = open("cypher_query_visualization.html", 'r', encoding='utf-8')
                                    source_code = HtmlFile.read()
                                    st.components.v1.html(source_code, height=600)
                            else:
                                st.warning("No results found for the given query.")
                        else:
                            st.error("Failed to generate or execute the query. Please check the server.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"API request failed: {str(e)}")

        if st.button("Logout"):
            st.session_state.authenticated = False
            st.warning("You have been logged out.")

    # Instructions Section
    st.sidebar.subheader("Instructions")
    st.sidebar.write("""
        - Enter the query related to transactions or addresses.
        - Click 'Generate and Visualize' to see the graph visualization.
        - You can log out using the button provided.
    """)

    # Footer
    st.sidebar.markdown("""
        ---
        <div style="text-align: center;">
            Developed by <a href="https://yourwebsite.com" target="_blank">Your Company</a>
        </div>
        """, unsafe_allow_html=True)
