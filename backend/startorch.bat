set PYTHONPATH=%cd%
python -m uvicorn orchestrator.main:app --host 0.0.0.0 --port 9000 --reload  --log-level debug