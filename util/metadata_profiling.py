import sqlite3
import os
import json  # <-- Import the json library

DB_PATH = 'cloud_costs.db'

# --- 1. Check for DB ---
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

# --- 2. Create a dictionary to hold all results ---
profile_results = {
    "aws_cost_usage": {},
    "azure_cost_usage": {}
}

def profile_column(table_name, column_name):
    print(f"\n--- Profiling {table_name}.{column_name} ---")
    
    # This will hold results for this single column
    column_stats = {}
    
    try:
        # 1. Get 5 random sample values
        query_sample = f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL ORDER BY RANDOM() LIMIT 5"
        cursor.execute(query_sample)
        samples = [row[0] for row in cursor.fetchall()]
        print(f"Sample Values: {samples}")
        column_stats["sample_values"] = samples
        
        # 2. Get Null Percentage
        query_nulls = f"SELECT CAST(COUNT(*) - COUNT({column_name}) AS REAL) / COUNT(*) * 100 FROM {table_name}"
        cursor.execute(query_nulls)
        null_pct = cursor.fetchone()[0]
        if null_pct is None: null_pct = 0.0
        print(f"Null Percentage: {null_pct:.2f}%")
        column_stats["null_percentage"] = f"{null_pct:.2f}%"
        
        # 3. Get Distinct Value Count
        query_distinct = f"SELECT COUNT(DISTINCT {column_name}) FROM {table_name}"
        cursor.execute(query_distinct)
        distinct_count = cursor.fetchone()[0]
        print(f"Distinct Values: {distinct_count}")
        column_stats["distinct_values"] = distinct_count
        
        # Store this column's stats in the main dictionary
        profile_results[table_name][column_name] = column_stats
        
    except sqlite3.OperationalError as e:
        print(f"!!! ERROR profiling {table_name}.{column_name}: {e} !!!")
        profile_results[table_name][column_name] = {"error": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        profile_results[table_name][column_name] = {"error": str(e)}

# --- 3. Run Profiling (same as before) ---
print("=== PROFILING AWS TABLE ===")
profile_column('aws_cost_usage', 'ServiceName')
profile_column('aws_cost_usage', 'RegionName')
profile_column('aws_cost_usage', 'EffectiveCost')
profile_column('aws_cost_usage', 'BillingPeriodStart')

print("\n=== PROFILING AZURE TABLE ===")
profile_column('azure_cost_usage', 'ServiceName')
profile_column('azure_cost_usage', 'RegionName')
profile_column('azure_cost_usage', 'EffectiveCost')
profile_column('azure_cost_usage', 'BillingPeriodStart')

conn.close()

# --- 4. Write the results to a JSON file ---
OUTPUT_FILE = "semantic_metadata.json"
try:
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(profile_results, f, indent=2)
    print(f"\n✅ Successfully wrote profiling results to {OUTPUT_FILE}")
except Exception as e:
    print(f"\n❌ Error writing JSON file: {e}")