# this script is responsible to load_the dataset to sqlite as cloud_costs.db
import pandas as pd
import sqlite3
import os

# --- Configuration ---
AWS_CSV_PATH = 'aws_cost_usage.csv'
AZURE_CSV_PATH = 'azure_cost_usage.csv'
# Main database
DB_PATH = 'cloud_costs.db' 
AWS_TABLE_NAME = 'aws_cost_usage'
AZURE_TABLE_NAME = 'azure_cost_usage'


def load_csv_to_sqlite(csv_path, table_name, db_path):
    """Loads a CSV file into a specific table in an SQLite database."""
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run create_mock_data.py first.")
        return

    try:
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(db_path)
        
        # Use if_exists='replace' to easily re-run the script
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"Successfully loaded {len(df)} rows from {csv_path} into table '{table_name}' in {DB_PATH}.")
    
    except Exception as e:
        print(f"An error occurred while loading {csv_path}: {e}")

# --- Main execution ---
if __name__ == "__main__":
    # Ensure a clean start by deleting the old DB if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed old database: {DB_PATH}")

    print("Starting data loading process...")
    
    load_csv_to_sqlite(AWS_CSV_PATH, AWS_TABLE_NAME, DB_PATH)
    load_csv_to_sqlite(AZURE_CSV_PATH, AZURE_TABLE_NAME, DB_PATH)
    
    print(f"\nData loading complete. Your database '{DB_PATH}' is ready.")