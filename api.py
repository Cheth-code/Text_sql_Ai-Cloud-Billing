import sqlite3
import json
import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from fastapi import FastAPI
from pydantic import BaseModel

# --- 1. Setup ---
load_dotenv()

DB_PATH = "cloud_costs.db"
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"Database '{DB_PATH}' not found. Please run 'load_data.py' first.")

sqlite_uri = f"sqlite:///{DB_PATH}"
db = SQLDatabase.from_uri(sqlite_uri, 
                          include_tables=['aws_cost_usage', 'azure_cost_usage'], 
                          sample_rows_in_table_info=2)

try:
    with open('semantic_metadata.json', 'r') as f:
        semantic_metadata = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("Error: 'semantic_metadata.json' not found. Please complete Step 2 first.")

llm = ChatOpenAI(model_name="gpt-4o")

# --- 2. Chain Definitions ---

# Table Selection
table_selection_template = """
Based on the database schema and the user's question, determine which table is the most relevant.
Return ONLY the table name (e.g., 'aws_cost_usage' or 'azure_cost_usage').
Schema: {schema}
Question: {question}
Relevant Table:
"""
table_selection_prompt = ChatPromptTemplate.from_template(table_selection_template)
_table_selection_chain = (
    RunnablePassthrough.assign(schema=lambda _: db.get_table_info())
    | table_selection_prompt
    | llm
    | StrOutputParser()
)
table_selection_chain = RunnablePassthrough.assign(table_name=_table_selection_chain)

# SQL Generation
sql_gen_template = """
Based on the table schema, semantic metadata, and the user's question, write a single-line SQLite query.
You MUST follow the 'expert_guidance' from the semantic metadata.
Return ONLY the raw SQL query. Do NOT add line breaks, comments, or ```sql``` markdown.

Database Schema: {schema}
Semantic Metadata for {table_name}: {metadata}
Question: {question}
--- EXAMPLES ---
Question: "Which AWS region had the highest spend last month?"
SQL Query: SELECT RegionName AS Region, SUM(EffectiveCost) AS TotalSpent FROM aws_cost_usage WHERE BillingPeriodStart >= substr(date('now','-1 month', 'start of month'), 1, 10) AND BillingPeriodStart < substr(date('now', 'start of month'), 1, 10) AND RegionName IS NOT NULL GROUP BY RegionName ORDER BY TotalSpent DESC LIMIT 1;
Question: "What is the daily trend of S3 storage cost?"
SQL Query: SELECT substr(BillingPeriodStart, 1, 10) AS BillingDate, SUM(EffectiveCost) AS TotalS3Cost FROM aws_cost_usage WHERE ServiceName = 'Amazon Simple Storage Service' AND BillingPeriodStart IS NOT NULL GROUP BY BillingDate ORDER BY BillingDate;
Question: "What is EC2 usage by instance type?"
SQL Query: SELECT UsageType, SUM(EffectiveCost) AS TotalCost FROM aws_cost_usage WHERE ServiceName = 'Amazon Elastic Compute Cloud' AND UsageType LIKE '%BoxUsage%' GROUP BY UsageType ORDER BY TotalCost DESC;
Question: "Show me the total compute cost for Azure grouped by service."
SQL Query: SELECT ServiceName, SUM(EffectiveCost) AS TotalComputeCost FROM azure_cost_usage WHERE MeterCategory = 'Virtual Machines' GROUP BY ServiceName ORDER BY TotalComputeCost DESC;
---
Question: {question}
SQL Query:
"""
sql_gen_prompt = ChatPromptTemplate.from_template(sql_gen_template)

def get_relevant_metadata(table_name):
    return json.dumps(semantic_metadata.get(table_name, {}), indent=2)

sql_chain = (
    RunnablePassthrough.assign(
        schema=lambda _: db.get_table_info(),
        metadata=lambda x: get_relevant_metadata(x['table_name'])
    )
    | sql_gen_prompt
    | llm
    | StrOutputParser()
)

# Full SQL Chain
full_sql_chain = table_selection_chain.assign(query=sql_chain)

# Answer Generation
description_template = """
Based on the user's question and the data retrieved from the database,
write a clear, natural language answer.
Question: {question}
SQL Query: {query}
Data: {data}
Descriptive Answer:
"""
description_prompt = ChatPromptTemplate.from_template(description_template)
description_chain = (
    description_prompt
    | llm
    | StrOutputParser()
)

# --- 3. FastAPI App Definition ---

# Initialize the app
app = FastAPI(
    title="Cloud Cost Text-to-SQL API",
    description="An API to answer FinOps questions using natural language."
)

# Define the request model
class QueryRequest(BaseModel):
    question: str

# Define the response model
class QueryResponse(BaseModel):
    question: str
    selected_table: str
    sql_query: str
    query_result: list
    descriptive_answer: str

@app.post("/query", response_model=QueryResponse)
async def run_query_endpoint(request: QueryRequest):
    """
    Main endpoint to run the full text-to-SQL process.
    """
    question = request.question
    
    # 1. Generate SQL
    try:
        sql_chain_output = await full_sql_chain.ainvoke({"question": question})
        sql_query = sql_chain_output['query'].replace("```sql", "").replace("```", "").strip()
        selected_table = sql_chain_output['table_name']
    except Exception as e:
        return {"error": f"Error during SQL generation: {e}"}

    # 2. Execute SQL
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        query_result = cursor.fetchall()
        conn.close()
    except Exception as e:
        return {"error": f"Error executing SQL: {e}", "sql_query": sql_query}

    # 3. Generate Descriptive Answer
    try:
        final_answer = await description_chain.ainvoke({
            "question": question,
            "query": sql_query,
            "data": str(query_result)
        })
    except Exception as e:
        return {"error": f"Error during answer generation: {e}"}

    # 4. Return the full response
    return QueryResponse(
        question=question,
        selected_table=selected_table,
        sql_query=sql_query,
        query_result=query_result,
        descriptive_answer=final_answer
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Text-to-SQL API. Post your questions to /query"}