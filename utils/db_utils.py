# dashboard_project/utils/db_connector.py
import pandas as pd
import psycopg2 # For PostgreSQL connection
import os
from dotenv import load_dotenv # Optional: for loading .env files

# Optional: Load environment variables from a .env file in your project root
load_dotenv()

# --- Database Connection Details ---
# It's highly recommended to use environment variables for sensitive information
DB_NAME = os.getenv("DB_NAME", "dashboard")
DB_USER = os.getenv("DB_USER", "your_postgres_user") # Replace with your actual user if not using env var
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_postgres_password") # Replace if not using env var
DB_HOST = os.getenv("DB_HOST", "localhost") # Or your DB host
DB_PORT = os.getenv("DB_PORT", "5432") # Default PostgreSQL port

_db_connection = None

def get_db_connection():
    """
    Establishes and returns a psycopg2 database connection.
    Uses environment variables for connection parameters.
    If a connection already exists and is open, it will be reused (simple reuse).
    For production, consider a proper connection pool.
    """
    global _db_connection
    try:
        # Check if connection exists and is still open
        if _db_connection and not _db_connection.closed:
            # You might want to check if the connection is usable, e.g., _db_connection.status == psycopg2.extensions.STATUS_READY
            # For simplicity, we assume it's fine if not closed.
            return _db_connection

        # print(f"Attempting to connect to PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
        _db_connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # print("Database connection established successfully.")
        return _db_connection
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        _db_connection = None # Reset connection on error
        return None

def fetch_data(query: str, params=None) -> pd.DataFrame:
    """
    Fetches data from the PostgreSQL database using the given query.

    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters to pass to the SQL query. Defaults to None.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the query results.
                      Returns an empty DataFrame if an error occurs or no data.
    """
    conn = get_db_connection()
    if conn:
        try:
            # print(f"Executing query: {query}")
            # if params:
            #     print(f"With parameters: {params}")
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except (Exception, psycopg2.Error) as e:
            print(f"Error fetching data with psycopg2: {e}")
            # Optional: you might want to rollback if it was part of a transaction
            # conn.rollback()
            return pd.DataFrame() # Return empty DataFrame on error
        # For simple use, we might not close the connection here if we plan to reuse it via get_db_connection.
        # If using a connection per query:
        # finally:
        #     if conn and not conn.closed:
        #         conn.close()
    else:
        print("Database connection not established. Cannot fetch data.")
        return pd.DataFrame()

def close_db_resources():
    """
    Closes any open database resources. Call this when the application shuts down.
    """
    global _db_connection
    if _db_connection and not _db_connection.closed:
        try:
            _db_connection.close()
            print("PostgreSQL connection closed.")
        except Exception as e:
            print(f"Error closing PostgreSQL connection: {e}")
    _db_connection = None

# Optional: Register the cleanup function to be called on application exit
# import atexit
# atexit.register(close_db_resources)

# Example usage (for testing this file directly):
if __name__ == '__main__':
    print("Testing database connection...")
    # Ensure your environment variables are set or update placeholders above
    # Example: os.environ['DB_USER'] = 'myuser'
    #          os.environ['DB_PASSWORD'] = 'mypass'

    test_conn = get_db_connection()
    if test_conn:
        print("Connection successful!")
        sample_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5;"
        df_tables = fetch_data(sample_query)
        if not df_tables.empty:
            print("Fetched public tables (limit 5):")
            print(df_tables)
        else:
            print("Could not fetch tables or no tables found.")
        close_db_resources()
    else:
        print("Connection failed. Check credentials and DB server.")