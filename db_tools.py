import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

def execute_sql(sql_query: str) -> str:
    """
    Executes a SQL query against a PostgreSQL database.
    Returns up to 5 rows as a formatted string on success,
    or an error message on failure.
    """
    # Load environment variables from .env file
    load_dotenv()
    
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
            results = cursor.fetchmany(5)
            
            if not results:
                return "Query executed successfully. No rows returned."
                
            # Format the results into a string
            formatted_results = "\n".join([str(row) for row in results])
            return formatted_results
        else:
            # Commit the transaction for data manipulation queries (INSERT, UPDATE, DELETE)
            connection.commit()
            return "Query executed successfully. No data to return."
            
    except Error as e:
        # Rollback the transaction on error to clear the aborted state
        if connection:
            connection.rollback()
        # Return the exact error string format requested
        return f"ERROR: {str(e).strip()}"
        
    finally:
        # Ensure database resources are cleanly closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()
