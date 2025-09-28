set PYTHONPATH=%cd%
python -m uvicorn vector_agent.main:app --host 0.0.0.0 --port 9002 --reload  --log-level debug