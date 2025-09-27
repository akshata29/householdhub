# Individual service startup commands

# 1. Start Orchestrator Service (Port 8000)
cd orchestrator
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 2. Start NL2SQL Agent (Port 8001)  
cd nl2sql_agent
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# 3. Start Vector Agent (Port 8002)
cd vector_agent  
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# 4. Start API Agent (Port 8003)
cd api_agent
python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload