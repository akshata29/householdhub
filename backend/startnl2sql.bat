set PYTHONPATH=%cd%
python -m uvicorn nl2sql_agent.main:app --host 0.0.0.0 --port 9001 --reload  --log-level debug