# Backend (FastAPI)

Wires the full pipeline together behind a simple HTTP API:
upload source -> parse -> build dependency graph -> generate C++ -> return results.

## Run locally
```bash
cd backend
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

## Endpoints (planned)
- `POST /upload` — upload a Pascal/C source file
- `POST /process/{file_id}` — run the full pipeline on an uploaded file
- `GET /result/{file_id}` — get generated C++ + dependency graph JSON + diff

## TODO
- [ ] File upload endpoint + temp storage
- [ ] Pipeline orchestration endpoint (calls parser -> dependency_graph -> llm_orchestration)
- [ ] Result retrieval endpoint
- [ ] Error handling / status codes
- [ ] CORS setup for frontend
