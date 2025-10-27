import sqlite3

DB_PATH = 'cloud_costs.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def profile_column(table_name, column_name):
    print(f"\n--- Profiling {table_name}.{column_name} ---")
    
    # 1. Get 5 random sample values
    query_sample = f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL ORDER BY RANDOM() LIMIT 5"
    cursor.execute(query_sample)
    samples = [row[0] for row in cursor.fetchall()]
    print(f"Sample Values: {samples}")
    
    # 2. Get Null Percentage
    query_nulls = f"SELECT CAST(COUNT(*) - COUNT({column_name}) AS REAL) / COUNT(*) * 100 FROM {table_name}"
    cursor.execute(query_nulls)
    null_pct = cursor.fetchone()[0]
    print(f"Null Percentage: {null_pct:.2f}%")
    
    # 3. Get Distinct Value Count
    query_distinct = f"SELECT COUNT(DISTINCT {column_name}) FROM {table_name}"
    cursor.execute(query_distinct)
    distinct_count = cursor.fetchone()[0]
    print(f"Distinct Values: {distinct_count}")

# --- Run Profiling ---
print("=== PROFILING AWS TABLE ===")
profile_column('aws_cost_usage', 'ServiceName')
profile_column('aws_cost_usage', 'RegionName')
profile_column('aws_cost_usage', 'EffectiveCost')
profile_column('aws_cost_usage', 'BillingPeriodStart')

print("\n=== PROFILING AZURE TABLE ===")
profile_column('azure_cost_usage', 'ServiceName')
profile_column('azure_cost_usage', 'ResourceLocation')
profile_column('azure_cost_usage', 'EffectiveCost')
profile_column('azure_cost_usage', 'UsageDateTime')

conn.close()