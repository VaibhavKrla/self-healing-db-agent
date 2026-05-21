# Self-Healing Database Operations Agent

## Overview
This project implements a self-healing, neuro-symbolic database operations agent. Designed for complex operational environments, the system translates natural language operational queries into executable SQL, runs them against a local PostgreSQL database, and autonomously detects and heals syntax or semantic anomalies without human intervention.

## The Core Problem Solved
Traditional AI data extraction tools often function as brittle wrappers around large language models, breaking silently or explicitly when faced with nuanced schema requirements or edge cases. This agent discards the "chatbot demo" paradigm in favor of a robust state machine capable of operating reliably in production. By decoupling the reasoning engine from execution and treating database errors as deterministic feedback, the agent systematically debugs its own logic, ensuring continuous operation even when initial hypotheses fail.

## System Architecture
The agent is built on a directed, cyclic graph architecture utilizing `LangGraph`:
- **State Machine (`main.py`)**: Orchestrates the control flow, defining the transition matrices between generation, execution, and validation.
- **Structured Operational Memory (`state.py`)**: Utilizes `Pydantic` and typed dictionaries to maintain strict state integrity across graph transitions, tracking user intent, generated artifacts, execution context, and retry states.
- **Resilient Execution Tools (`db_tools.py`)**: Implements strict transaction boundaries using `psycopg2`, ensuring deterministic rollbacks on failure and preventing database state corruption.
- **Reasoning Nodes (`nodes.py`)**: Leverages `gemini-2.5-flash` bound to strict structured output schemas to enforce deterministic payload generation for both initial query synthesis and error correction.

## Reliability & Resilience
Reliability is prioritized at both the network and execution layers:
- **API Fault Tolerance**: Integrates the `tenacity` library to implement exponential backoff mechanisms, ensuring the system survives upstream API rate limits (e.g., `ResourceExhausted` exceptions) during high-throughput operational spikes.
- **Autonomous Healing Loop**: The system implements a cyclic routing logic (`should_retry`) that intercepts `psycopg2` exceptions. Instead of aborting, it feeds the raw deterministic database error back into the reasoning node. The agent rewrites the failing query and attempts execution again, safely bounding the self-healing cycle to a maximum of 3 retries to prevent infinite loops and resource exhaustion.

## Quick Start

### Prerequisites
- Python 3.10+
- Local PostgreSQL instance

### Setup

1. **Initialize Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install Dependencies**
   ```bash
   pip install langgraph langchain-google-genai psycopg2-binary python-dotenv pydantic tenacity google-api-core
   ```

3. **Configuration**
   Create a `.env` file in the root directory. **Do not commit this file to version control.**
   ```env
   # .env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   GOOGLE_API_KEY=your_gemini_api_key
   ```

4. **Execution**
   ```bash
   python main.py
   ```
