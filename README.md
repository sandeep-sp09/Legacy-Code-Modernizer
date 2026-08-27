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
See each module's own README for setup instructions.

## Team & Roles
| Module | Owner |
|---|---|
| Parser / AST | Tanish |
| LLM Orchestration | Tanish |
| Dependency Graph | Ajay / Abhijeet (TBD) |
| Backend (FastAPI) | Abhijeet / Abhishek (TBD) |
| Frontend / UI | Sandeep |
| Testing / Documentation | Ajay |
