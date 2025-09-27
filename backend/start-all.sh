#!/bin/bash
# Start all WealthOps backend services locally

echo "Starting WealthOps Backend Services..."
echo "=================================="

# Activate virtual environment
source venv/Scripts/activate

# Set environment variables
export ENVIRONMENT=development
export DEBUG=true
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start services in separate terminal windows
echo "Starting Orchestrator on port 9000..."
start "Orchestrator" cmd /k "cd orchestrator && python -m uvicorn main:app --host 0.0.0.0 --port 9000 --reload"

sleep 2

echo "Starting NL2SQL Agent on port 9001..."
start "NL2SQL Agent" cmd /k "cd nl2sql_agent && python -m uvicorn main:app --host 0.0.0.0 --port 9001 --reload"

sleep 2

echo "Starting Vector Agent on port 9002..."
start "Vector Agent" cmd /k "cd vector_agent && python -m uvicorn main:app --host 0.0.0.0 --port 9002 --reload"

sleep 2

echo "Starting API Agent on port 9003..."
start "API Agent" cmd /k "cd api_agent && python -m uvicorn main:app --host 0.0.0.0 --port 9003 --reload"

echo ""
echo "All services started!"
echo "Orchestrator: http://localhost:9000/docs"
echo "NL2SQL Agent: http://localhost:9001/docs"
echo "Vector Agent: http://localhost:9002/docs"
echo "API Agent: http://localhost:9003/docs"