# Dev server for ivr-intent-router
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
