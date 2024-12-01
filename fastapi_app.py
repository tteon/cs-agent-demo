from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from datetime import datetime
import openai
import ell

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.Client()

# Define FastAPI application
app = FastAPI()

# Define the schema for user input
class QueryRequest(BaseModel):
    text: str

# Function to preprocess and execute the Cypher query
def execute_query(query, uri="bolt://memgraph.chain-insights.io:30768", auth=("hyperclouds", "YouWish99"), database="memgraph"):
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session(database=database) as session:
            result = session.run(query)
            records = [record.data() for record in result]
            return records
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        if 'driver' in locals():
            driver.close()

def preprocess_query(raw_query):
    clean_query = raw_query.strip()
    if clean_query.startswith("```") and clean_query.endswith("```"):
        clean_query = clean_query[3:-3].strip()
    clean_query = clean_query.replace("\\n", " ").replace("\n", " ").strip()
    clean_query = ' '.join(clean_query.split())
    return clean_query

@ell.simple(model="gpt-4o-mini", client=client)
def text2cypher(text: str):
    """
    <instruction>
    - You are an expert in Neo4j Database Administration (DBA), specializing in Cypher query generation.
    - Your mission is to generate accurate and efficient Cypher queries to answer users' requests in the Neo4j or Memgraph database.
    - Generate a Cypher query that directly fulfills the user's request by interacting with the database.
    - Use the <schema> to understand the structure, labels, relationships, and properties of the database.
    - If the request involves multiple steps, ensure each step is integrated into the final Cypher query (e.g., filters, conditions, and specific properties).
    - Always rely on the <schema> provided to ensure consistency with the actual data model of the database.
    - Extract information about node labels, relationship types, and properties to construct queries that align with the database schema accurately.
    - If a property, label, or relationship type is missing or unknown in the schema, refrain from guessing. Either return an informative response or default to the schema details available.
    - When the generated query is intended for direct database execution, output only the Cypher query.
    - Avoid adding any additional explanatory text, comments, or metadata around the query. The response should be formatted as a pure Cypher query.
    - When generating queries, if user instructions are ambiguous, make reasonable assumptions based on typical graph modeling patterns. Document these assumptions internally if needed.
    - When the user's question involves aggregates, filters, or sorting, add the appropriate clauses (MATCH, WHERE, RETURN, ORDER BY, etc.).
    </instruction>

    <schema>    
    Nodes:
    - Address: Properties include address (string).
    - Transaction: Properties include block_height (int) in_total_amount (int) in_coinbase (bool) out_total_amount (int) timestamp (int) tx_id (string)
    
    Relationships:
    - SENT: Address -> Transaction -> Address with property value_satoshi (int)
    </schema>
    """
    return f"{text}"

# FastAPI endpoint to receive a query
@app.post("/generate-query/")
async def generate_query(request: QueryRequest):
    try:
        # Generate Cypher query from user text
        generated_cypher = text2cypher(request.text)
        clean_query = preprocess_query(generated_cypher)

        # Execute query and get results
        records = execute_query(clean_query)

        # Return the records to the client
        return {"results": records}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
