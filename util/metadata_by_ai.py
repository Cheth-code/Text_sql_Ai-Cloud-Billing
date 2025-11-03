import sqlite3
import os
import json
from openai import OpenAI  # <-- Import OpenAI
import time
from dotenv import load_dotenv  # <-- Import dotenv
from pathlib import Path

# --- 1. Configuration ---  # <-- Load variables from .env file
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / '.env'  # <-- Path to .env file
load_dotenv(dotenv_path=env_path) 
DB_PATH = 'cloud_costs.db'
FINAL_OUTPUT_FILE = "semantic_metadata.json"

# !!! IMPORTANT !!!
# SET YOUR API KEY IN YOUR .env FILE
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # <-- Load key from environment

# --- 2. Setup OpenAI API ---
if not OPENAI_API_KEY:  # <-- Updated check
    print("=" * 50)
    print("ERROR: OPENAI_API_KEY not found.")
    print("Please create a .env file and add your key (e.g., OPENAI_API_KEY=sk-...)")
    print("=" * 50)
    exit()

try:
    # Initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    # Test the connection (optional, but good practice)
    client.models.list()
except Exception as e:
    print(f"Error configuring OpenAI API: {e}")
    exit()
print("✅ OpenAI API configured.")

# --- 3. Setup Database ---
if not os.path.exists(DB_PATH):
    print(f"Error: Database '{DB_PATH}' not found.")
    print("Please run your data loading script first to create the database.")
    exit()

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit()
print(f"✅ Database '{DB_PATH}' connected.")

# --- 4. Initialize Results Dictionary ---
# This will be populated automatically by the auto-discovery phase
profile_results = {}

# --- 5. Define Helper Functions ---

def profile_column(table_name, column_name):
    """
    Profiles a single column for quantitative stats (samples, nulls, distinct).
    Modifies the global 'profile_results' dictionary in-place.
    """
    print(f"\n--- Profiling {table_name}.{column_name} ---")

    column_stats = {}

    try:
        # 1. Get 5 random sample values
        # Using f-strings here is safe because table/column names are from PRAGMA
        query_sample = f"SELECT \"{column_name}\" FROM \"{table_name}\" WHERE \"{column_name}\" IS NOT NULL ORDER BY RANDOM() LIMIT 5"
        cursor.execute(query_sample)
        samples = [row[0] for row in cursor.fetchall()]
        print(f"  Sample Values: {samples}")
        column_stats["sample_values"] = samples

        # 2. Get Null Percentage
        query_nulls = f"SELECT CAST(COUNT(*) - COUNT(\"{column_name}\") AS REAL) / COUNT(*) * 100 FROM \"{table_name}\""
        cursor.execute(query_nulls)
        null_pct = cursor.fetchone()[0]
        if null_pct is None: null_pct = 0.0
        print(f"  Null Percentage: {null_pct:.2f}%")
        column_stats["null_percentage"] = f"{null_pct:.2f}%"

        # 3. Get Distinct Value Count
        query_distinct = f"SELECT COUNT(DISTINCT \"{column_name}\") FROM \"{table_name}\""
        cursor.execute(query_distinct)
        distinct_count = cursor.fetchone()[0]
        print(f"  Distinct Values: {distinct_count}")
        column_stats["distinct_values"] = distinct_count

        # Store this column's stats in the main dictionary
        profile_results[table_name][column_name] = column_stats

    except sqlite3.OperationalError as e:
        print(f"  !!! ERROR profiling {table_name}.{column_name}: {e} !!!")
        profile_results[table_name][column_name] = {"error": str(e)}
    except Exception as e:
        print(f"  An unexpected error occurred: {e}")
        profile_results[table_name][column_name] = {"error": str(e)}

def create_ai_prompt(table_name, column_name, stats):
    """Creates a specific prompt for the LLM to get semantic metadata."""

    # Convert the stats dictionary to a clean string for the prompt
    stats_str = json.dumps(stats, indent=2)

    # This prompt is passed as the "user" message
    return f"""
    Database Table: {table_name}
    Column Name: {column_name}
    Profiled Statistics:
    {stats_str}

    Based on this information, please provide:
    1.  A "description": A concise, plain-English description of what this column represents (e.g., "The total cost of the service in USD.").
    2.  A "semantic_type": The general data category. Choose only from: 
        'Categorical', 'Numerical', 'Date', 'Time', 'Text', 'Boolean', 'Identifier', 'Other'

    Respond *only* with a valid JSON object containing these two keys.
    """

# --- 6. Execution Phase 1: Auto-Discovery and Profiling ---
print("\n=== PHASE 1: AUTO-DISCOVERING & PROFILING DATABASE ===")

# 1. Get all user tables (excluding sqlite system tables)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [row[0] for row in cursor.fetchall()]
print(f"Found tables: {tables}")

for table_name in tables:
    print(f"\n=== PROFILING TABLE: {table_name} ===")
    profile_results[table_name] = {}
    
    # 2. For each table, get its columns
    cursor.execute(f"PRAGMA table_info(\"{table_name}\")")
    # PRAGMA returns (cid, name, type, notnull, dflt_value, pk)
    columns = [row[1] for row in cursor.fetchall()]
    print(f"  Found columns: {columns}")
    
    # 3. Profile each column
    for column_name in columns:
        profile_column(table_name, column_name)


# Close the database connection as we are done with it
conn.close()
print("\n✅ Database connection closed.")

# --- 7. Execution Phase 2: Run AI Enrichment ---
print("\n=== PHASE 2: ENRICHING METADATA VIA LLM (OpenAI) ===")

# System prompt to guide the model's behavior
SYSTEM_PROMPT = """
You are an expert data analyst and database architect.
Your task is to provide semantic metadata for a database column based on its profiled statistics.
Respond *only* with a valid JSON object. Do not add any other text, explanations, or markdown formatting.
"""

# We now loop directly through the 'profile_results' dictionary
# that Phase 1 just populated.
for table_name, columns in profile_results.items():
    print(f"\n--- Processing Table: {table_name} ---")

    # 'stats' is the dictionary created in profile_column()
    for column_name, stats in columns.items():
        print(f"  > Enriching '{column_name}'...")

        if "error" in stats:
            print(f"    - SKIPPING (original script had an error: {stats['error']})")
            continue

        # 1. Create the user prompt using the stats we just gathered
        user_prompt = create_ai_prompt(table_name, column_name, stats)

        try:
            # 2. Call the LLM (OpenAI Chat Completions)
            response = client.chat.completions.create(
                # Using gpt-4o-mini as a fast, capable, and cost-effective model
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                # Enable JSON mode for reliable JSON output
                response_format={"type": "json_object"}
            )
            
            # 3. Parse the LLM's JSON response
            response_text = response.choices[0].message.content
            ai_metadata = json.loads(response_text)

            # 4. Merge the new metadata *directly back into the stats dictionary*
            stats['ai_description'] = ai_metadata.get('description', 'N/A')
            stats['semantic_type'] = ai_metadata.get('semantic_type', 'N/A')

            print(f"    - SUCCESS: Added AI description and semantic type.")

        except json.JSONDecodeError:
            print(f"    - ERROR: Failed to decode LLM response for '{column_name}'.")
            print(f"    - Response was: {response_text}")
            stats['ai_error'] = "Failed to parse LLM response"
        except Exception as e:
            # This will catch OpenAI-specific errors (RateLimitError, APIError)
            print(f"    - ERROR: An unexpected error occurred with '{column_name}': {e}")
            stats['ai_error'] = str(e)

        # Be nice to the API - add a small delay to avoid rate limiting
        time.sleep(1)

# --- 8. Final Step: Write the final enriched JSON file ---
print("\n--- All Phases Complete ---")
try:
    with open(FINAL_OUTPUT_FILE, 'w') as f:
        # Dump the 'profile_results' dict, which now contains *both*
        # the original stats and the new AI-generated keys.
        json.dump(profile_results, f, indent=2)
    print(f"✅ Successfully wrote final enriched metadata to {FINAL_OUTPUT_FILE}")
except Exception as e:
    print(f"❌ Error writing final JSON file: {e}")

