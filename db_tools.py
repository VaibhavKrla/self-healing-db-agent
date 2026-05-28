import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

def execute_sql(sql_query: str) -> dict:
    """
    Executes a SQL query against a PostgreSQL database.
    Returns a dictionary with status, columns, and rows.
    """
    # Load environment variables from .env file (override existing to ensure fresh creds)
    load_dotenv(override=True)
    
    # Retrieve database credentials
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    connection = None
    cursor = None
    
    try:
        # Establish the database connection
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = connection.cursor()
        
        # Execute the provided query
        cursor.execute(sql_query)
        
        # Fetch results if the query returns data (e.g., SELECT)
        if cursor.description is not None:
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchmany(50) # Return up to 50 rows for the UI
            
            if not results:
                return {"status": "success", "columns": [], "rows": [], "message": "Query executed successfully. No rows returned."}
                
            # Convert row tuples to lists for JSON serialization
            formatted_results = [list(row) for row in results]
            return {"status": "success", "columns": columns, "rows": formatted_results}
        else:
            # Commit the transaction for data manipulation queries (INSERT, UPDATE, DELETE)
            connection.commit()
            return {"status": "success", "columns": [], "rows": [], "message": "Query executed successfully. No data to return."}
            
    except Error as e:
        # Rollback the transaction on error to clear the aborted state
        if connection:
            connection.rollback()
        # Return the exact error string format requested
        return {"status": "error", "message": f"ERROR: {str(e).strip()}"}
        
    finally:
        # Ensure database resources are cleanly closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()
