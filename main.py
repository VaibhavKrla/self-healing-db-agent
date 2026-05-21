import json

from langgraph.graph import END, START, StateGraph

from nodes import generate_sql, run_sql
from state import AgentState


def should_retry(state: AgentState) -> str:
    """
    Determines whether to retry SQL generation or end the graph execution.
    Returns 'generate_sql' if there is an error and retries are under the limit,
    otherwise returns END.
    """
    execution_error = state.get("execution_error", "")
    retry_count = state.get("retry_count", 0)

    if execution_error and retry_count < 3:
        return "generate_sql"

    return END


# Initialize the state graph
workflow = StateGraph(AgentState)

# Add nodes to the graph
workflow.add_node("generate_sql", generate_sql)
workflow.add_node("run_sql", run_sql)

# Define the basic execution flow
workflow.add_edge(START, "generate_sql")
workflow.add_edge("generate_sql", "run_sql")

# Add the conditional edge for the self-healing retry loop
workflow.add_conditional_edges("run_sql", should_retry)

# Compile the graph into an executable application
app = workflow.compile()

if __name__ == "__main__":
    # ==========================================
    # EXORD SYSTEMS: PRODUCTION REASONING TESTS
    # ==========================================

    # Test 1: Filtering and Date Math
    test_1 = "Find all active users in the AI Systems department who signed up in the last 30 days."

    # Test 2: Aggregation
    test_2 = "Count how many users are in each department."

    # Test 3: Complex OR Conditions & Time Logic
    test_3 = "Show me the names and emails of everyone in Healthcare Ops or Compliance who hasn't logged in today."

    # Initialize the starting state (Swap test_1 to test_2 or test_3 here)
    initial_state = {
        "user_query": test_3,
        "generated_sql": "",
        "execution_error": "",
        "retry_count": 0,
    }

    print("Starting LangGraph Text-to-SQL Agent...")
    print(f"User Query: '{initial_state['user_query']}'\n")

    # Execute the graph
    final_state = app.invoke(initial_state)

    # Nicely format and print the final state
    print("\n" + "=" * 50)
    print("FINAL AGENT STATE")
    print("=" * 50)
    print(json.dumps(final_state, indent=2))
    print("=" * 50)
