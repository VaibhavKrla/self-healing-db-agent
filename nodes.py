from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState, SQLQueryOutput
from db_tools import execute_sql

def generate_sql(state: AgentState) -> dict:
    """
    Generates a new SQL query or fixes an existing one based on execution errors.
    Returns a dict with state updates for 'generated_sql' and 'retry_count'.
    """
    # Initialize the LLM (using gemini-1.5-flash for speed and cost efficiency)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # Bind to our Pydantic model to enforce structured output
    structured_llm = llm.with_structured_output(SQLQueryOutput)
    
    user_query = state.get("user_query", "")
    current_sql = state.get("generated_sql", "")
    execution_error = state.get("execution_error", "")
    retry_count = state.get("retry_count", 0)
    
    # Construct the prompt based on the presence of an execution error
    if not execution_error:
        prompt = (
            f"You are an expert PostgreSQL database engineer.\n"
            f"Generate a valid PostgreSQL query to answer the following user request:\n"
            f"<request>\n{user_query}\n</request>\n"
            f"Return the query and a brief explanation using the requested structured format."
        )
    else:
        prompt = (
            f"You are an expert PostgreSQL database engineer.\n"
            f"You need to fix a failing SQL query.\n"
            f"Original Request: {user_query}\n"
            f"Failing Query: {current_sql}\n"
            f"Error Message: {execution_error}\n"
            f"Analyze the error, fix the SQL query, and return the corrected query "
            f"along with an explanation of your fix."
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
    except Exception as e:
        # Handle potential LLM invocation or parsing errors gracefully
        print(f"Error during LLM generation: {e}")
        return {
            "execution_error": f"ERROR: Failed to generate SQL - {str(e)}",
            "retry_count": retry_count + 1
        }
        
    return {
        "generated_sql": new_sql,
        "retry_count": retry_count + 1
    }

def run_sql(state: AgentState) -> dict:
    """
    Executes the current SQL query and updates the state based on success or failure.
    Returns a dict with state updates for 'execution_error'.
    """
    generated_sql = state.get("generated_sql", "")
    
    if not generated_sql:
        return {"execution_error": "ERROR: No SQL query provided to execute."}
        
    try:
        # Call our database tool
        result = execute_sql(generated_sql)
        
        # Check if the execution returned an error string
        if result.startswith("ERROR:"):
            return {"execution_error": result}
        else:
            # Print the successful results to the terminal for visibility
            print("\n" + "="*40)
            print("SQL EXECUTION SUCCESS")
            print("="*40)
            print(f"Query: {generated_sql}")
            print("-" * 40)
            print("Results:")
            print(result)
            print("="*40 + "\n")
            
            # Clear the error state on success
            return {"execution_error": ""}
            
    except Exception as e:
        # Catch unexpected errors from the execution environment
        return {"execution_error": f"ERROR: Unexpected exception during execution - {str(e)}"}
