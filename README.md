# Self-Healing Database Operations Agent

## Overview
This project implements a full-stack, self-healing, neuro-symbolic database operations agent. Designed for complex operational environments, the system translates natural language operational queries into executable SQL, runs them against a local PostgreSQL database, and autonomously detects and heals syntax or semantic anomalies without human intervention. It features a decoupled architectural design with a FastAPI backend and a sleek, terminal-inspired React frontend.

## The Core Problem Solved
Traditional AI data extraction tools often function as brittle wrappers around large language models, breaking silently or explicitly when faced with nuanced schema requirements or edge cases. This agent discards the "chatbot demo" paradigm in favor of a robust state machine capable of operating reliably in production. By decoupling the reasoning engine from execution and treating database errors as deterministic feedback, the agent systematically debugs its own logic, ensuring continuous operation even when initial hypotheses fail.

## System Architecture
The application is strictly decoupled into a high-performance backend API and a modern frontend UI.

### 1. Backend Engine (Python, FastAPI, LangGraph)
- **FastAPI (`api.py`)**: A high-performance REST API that exposes the LangGraph agent and manages cross-origin resource sharing (CORS).
- **State Machine (`main.py`)**: Orchestrates the control flow utilizing `LangGraph`, defining the transition matrices between generation, execution, and self-healing loops.
- **Structured Operational Memory (`state.py`)**: Utilizes `Pydantic` and typed dictionaries to maintain strict state integrity across graph transitions, tracking user intent, generated artifacts, execution context, latency, and telemetry.
- **Resilient Execution Tools (`db_tools.py`)**: Implements strict transaction boundaries using `psycopg2`, returning structured JSON data (columns and rows) rather than string blocks. Ensures deterministic rollbacks on failure to prevent database state corruption.
- **Reasoning Nodes (`nodes.py`)**: Leverages `mistral-small-latest` (via `langchain-mistralai`) bound to strict structured output schemas. It dynamically omits the database schema on the first attempt to force autonomous reasoning, but intelligently injects it during retry loops to guarantee successful self-healing.

### 2. Frontend Interface (React, TypeScript, Tailwind CSS)
- **Terminal-Style UI (`App.tsx`)**: A custom dark-mode interface built with Vite and Tailwind CSS.
- **Dynamic Schema Sidebar**: Provides operators with immediate visual context of the database structure.
- **Tabular Data Rendering**: Beautifully formats successful PostgreSQL JSON responses into scrollable, responsive HTML tables.
- **Agent Telemetry & Latency**: Visually maps the agent's internal "thoughts" (e.g., `[OK] Intent Parsed`, `[WARN] Self-Healing Initiated`) and tracks database execution latency in milliseconds.

## Reliability & Resilience
Reliability is prioritized at both the network and execution layers:
- **API Fault Tolerance**: Integrates the `tenacity` library to implement exponential backoff mechanisms, ensuring the system survives upstream API rate limits (e.g., `ResourceExhausted` exceptions) during high-throughput operational spikes.
- **Autonomous Healing Loop**: The system implements a cyclic routing logic (`should_retry`) that intercepts `psycopg2` exceptions. Instead of aborting, it feeds the raw deterministic database error back into the reasoning node alongside the true schema structure. The agent rewrites the failing query and attempts execution again, bounding the self-healing cycle to a maximum of 3 retries to prevent infinite loops.

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js & npm (for frontend)
- Local PostgreSQL instance

### 1. Backend Setup
1. **Initialize Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn langgraph langchain-mistralai psycopg2-binary python-dotenv pydantic tenacity google-api-core
   ```

3. **Configuration**
   Create a `.env` file in the root directory. **Do not commit this file to version control.**
   ```env
   # .env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_db_password
   MISTRAL_API_KEY=your_mistral_api_key
   ```

4. **Run the API Server**
   ```bash
   python api.py
   # Runs on http://0.0.0.0:8000
   ```

### 2. Frontend Setup
1. **Navigate to the Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start the Development Server**
   ```bash
   npm run dev -- --port 5173
   # Open http://localhost:5173 in your browser
   ```
