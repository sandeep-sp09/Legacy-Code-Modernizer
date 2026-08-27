"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Legacy Code Modernizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accept a Pascal/C source file for processing.
    """
    # TODO: save file, return a file_id
    raise NotImplementedError


@app.post("/process/{file_id}")
async def process_file(file_id: str):
    """
    Run the full pipeline: parse -> dependency graph -> LLM generation -> validation.
    """
    # TODO: call parser, dependency_graph, llm_orchestration modules in sequence
    raise NotImplementedError


@app.get("/result/{file_id}")
async def get_result(file_id: str):
    """
    Return the generated C++ code, dependency graph JSON, and diff for a processed file.
    """
    # TODO: fetch stored results
    raise NotImplementedError
