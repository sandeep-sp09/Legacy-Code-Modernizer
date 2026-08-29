# Legacy Code Modernizer

A tool that parses legacy Pascal/C source code into an AST, builds a dependency graph,
and uses an LLM (grounded in the extracted structure) to generate idiomatic, modern C++.

## Pipeline
1. **parser/** — Tree-sitter based AST extraction from Pascal/C source.
2. **dependency_graph/** — NetworkX-based control-flow and call-dependency graph, built from the AST.
3. **llm_orchestration/** — Prompt construction, AST/code chunking, and syntax-validation loop for the LLM-generated C++.
4. **backend/** — FastAPI service wiring the pipeline together (upload → parse → graph → generate → return).
5. **frontend/** — UI for uploading source, viewing the dependency graph, and reviewing the code diff.

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows cmd

# Install dependencies
pip install -r requirements.txt
pip install tree-sitter-cpp   # optional, for C++ syntax validation
```

## LLM Setup
```bash
ollama pull qwen2.5-coder:3b
ollama serve
```
Model: **Qwen2.5-Coder-3B-Instruct** (Q4_K_M) — runs on RTX 4060 (8GB) and RTX 3050 (6GB).

## Usage

### Run tests
```bash
python -m pytest tests/ -v
```

### Start backend
```bash
cd backend
uvicorn app.main:app --reload
```
API available at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`.

### API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a `.pas` or `.c` source file |
| `POST` | `/process/{file_id}` | Run the full conversion pipeline |
| `GET` | `/result/{file_id}` | Retrieve generated C++ and dependency graph |
