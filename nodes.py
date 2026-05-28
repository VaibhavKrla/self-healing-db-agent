import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
from langchain_mistralai import ChatMistralAI
from state import AgentState, SQLQueryOutput
from db_tools import execute_sql

def generate_sql(state: AgentState) -> dict:
    """
    Generates a new SQL query or fixes an existing one based on execution errors.
    Returns a dict with state updates for 'generated_sql' and 'retry_count'.
    """
    telemetry = state.get("telemetry", [])
    retry_count = state.get("retry_count", 0)
    
    if retry_count > 0:
        telemetry.append(f"[WARN] Self-Healing Initiated (Attempt {retry_count}). Analyzing Traceback...")
    else:
        telemetry.append("[OK] Intent Parsed. Generating SQL...")

    # Initialize the LLM (using mistral-small-latest to conserve API credits)
    llm = ChatMistralAI(model="mistral-small-latest", temperature=0)
    
    # Bind to our Pydantic model to enforce structured output
    structured_llm = llm.with_structured_output(SQLQueryOutput)
    
    user_query = state.get("user_query", "")
    current_sql = state.get("generated_sql", "")
    execution_error = state.get("execution_error", "")
    
    # Define the schema to provide context to the LLM upon failure
    schema_context = (
        "Table: users\n"
        "- id (SERIAL PRIMARY KEY)\n"
        "- name (VARCHAR)\n"
        "- email (VARCHAR UNIQUE)\n"
        "- role (VARCHAR)\n"
        "- department (VARCHAR)\n"
        "- account_status (VARCHAR, default 'ACTIVE')\n"
        "- signup_date (DATE)\n"
        "- last_login (TIMESTAMP)\n"
    )
    
    # Construct the prompt based on the presence of an execution error
    # NOTE: Schema is intentionally omitted in the initial prompt to demonstrate self-healing!
    if not execution_error:
        prompt = (
            f"You are an expert PostgreSQL database engineer.\n"
            f"Generate a valid PostgreSQL query to answer the following user request:\n"
            f"<request>\n{user_query}\n</request>\n"
            f"Assume table 'users'. If a column name fails, you will be given the error to correct it.\n"
            f"Return the query and a brief explanation using the requested structured format."
        )
    else:
        prompt = (
            f"You are an expert PostgreSQL database engineer.\n"
            f"You need to fix a failing SQL query.\n"
            f"Here is the actual database schema for your reference:\n{schema_context}\n"
            f"Original Request: {user_query}\n"
            f"Failing Query: {current_sql}\n"
            f"Error Message: {execution_error}\n"
            f"Analyze the Postgres error against the schema, fix the SQL query, "
            f"and return the corrected query along with an explanation of your fix."
        )
        
    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(),
        retry=retry_if_exception_type(ResourceExhausted)
    )
    def invoke_llm():
        return structured_llm.invoke(prompt)
        
    try:
        # Invoke the structured LLM using the tenacity retrying helper
        response: SQLQueryOutput = invoke_llm()
        new_sql = response.sql_query
        telemetry.append("[OK] SQL Generated.")
    except Exception as e:
        # Handle potential LLM invocation or parsing errors gracefully
        print(f"Error during LLM generation: {e}")
        telemetry.append(f"[FAIL] LLM Generation Error: {str(e)}")
        return {
            "execution_error": f"ERROR: Failed to generate SQL - {str(e)}",
            "retry_count": retry_count + 1,
            "telemetry": telemetry
        }
        
    return {
        "generated_sql": new_sql,
        "retry_count": retry_count + 1,
        "telemetry": telemetry
    }

def run_sql(state: AgentState) -> dict:
    """
    Executes the current SQL query and updates the state based on success or failure.
    Returns a dict with state updates for 'execution_error'.
    """
    generated_sql = state.get("generated_sql", "")
    telemetry = state.get("telemetry", [])
    
    if not generated_sql:
        telemetry.append("[FAIL] No SQL query provided to execute.")
        return {"execution_error": "ERROR: No SQL query provided to execute.", "telemetry": telemetry}
        
    start_time = time.time()
    try:
        # Call our database tool
        result = execute_sql(generated_sql)
        end_time = time.time()
        exec_time_ms = round((end_time - start_time) * 1000, 2)
        
        # Check if the execution returned an error dictionary
        if result.get("status") == "error":
            error_msg = result["message"]
            brief_error = error_msg.split("LINE")[0].strip()[:100] + "..." if len(error_msg) > 100 else error_msg
            telemetry.append(f"[FAIL] Execution Failed: {brief_error}")
            return {
                "execution_error": error_msg,
                "execution_time_ms": exec_time_ms,
                "telemetry": telemetry
            }
        else:
            telemetry.append(f"[OK] Execution Successful ({exec_time_ms}ms).")
            # Clear the error state on success and return data
            return {
                "execution_error": "",
                "results": result.get("rows", []),
                "columns": result.get("columns", []),
                "execution_time_ms": exec_time_ms,
                "telemetry": telemetry
            }
            
    except Exception as e:
        # Catch unexpected errors from the execution environment
        telemetry.append(f"[FAIL] Unexpected Execution Error: {str(e)}")
        return {
            "execution_error": f"ERROR: Unexpected exception during execution - {str(e)}",
            "telemetry": telemetry
        }
