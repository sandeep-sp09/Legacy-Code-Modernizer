"""
FastAPI application entrypoint.

Wires the full pipeline: upload source -> parse -> build dependency graph
-> generate C++ via LLM -> validate -> return results.
"""

import difflib
import os
import sys
import uuid
import tempfile
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ensure the project root is on sys.path so we can import parser, dependency_graph, etc.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from parser.ast_builder import parse_source, load_source
from parser.ast_extractor import extract_functions
from dependency_graph.graph_builder import build_call_graph, get_graph_context
from dependency_graph.graph_export import to_json
from llm_orchestration.prompt_builder import SYSTEM_PROMPT, build_full_file_prompt
from llm_orchestration.llm_client import generate_cpp

from .schemas import UploadResponse, ProcessResponse, ErrorResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Legacy Code Modernizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for uploaded files and processing results
# In production, use a database or object store.
_UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "legacy_modernizer_uploads")
os.makedirs(_UPLOAD_DIR, exist_ok=True)

_file_registry: dict[str, dict] = {}    # file_id -> {path, filename, language}
_result_registry: dict[str, dict] = {}  # file_id -> {generated_cpp, graph_json, diff, ...}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Accept a Pascal/C source file for processing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    lang_map = {".c": "c", ".h": "c", ".pas": "pascal", ".pp": "pascal",
                ".dpr": "pascal", ".lpr": "pascal"}

    language = lang_map.get(ext)
    if language is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Supported: {list(lang_map.keys())}",
        )

    file_id = str(uuid.uuid4())
    save_path = os.path.join(_UPLOAD_DIR, f"{file_id}{ext}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    _file_registry[file_id] = {
        "path": save_path,
        "filename": file.filename,
        "language": language,
    }

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        language=language,
    )


@app.post("/process/{file_id}", response_model=ProcessResponse)
async def process_file(file_id: str):
    """
    Run the full pipeline: parse -> dependency graph -> LLM generation -> validation.
    """
    if file_id not in _file_registry:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")

    file_info = _file_registry[file_id]
    file_path = file_info["path"]
    language = file_info["language"]

    try:
        # Step 1: Parse
        tree, lang = parse_source(file_path, language)
        source_code = load_source(file_path)
        functions = extract_functions(tree, lang, source_code)

        if not functions:
            raise HTTPException(
                status_code=400,
                detail="No functions found in the source file. Is the file empty or malformed?",
            )

        # Step 2: Build dependency graph
        graph = build_call_graph(functions)
        graph_json = to_json(graph)

        # Step 3: Build combined graph context
        context_parts = []
        for fn in functions:
            context_parts.append(get_graph_context(graph, fn.name))
        full_context = "\n".join(context_parts)

        # Step 4: Generate C++ via LLM
        prompt = build_full_file_prompt(source_code, functions, full_context, language)
        generated_cpp = generate_cpp(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            original_ir=functions,
        )

        # Step 5: Compute diff
        original_lines = source_code.splitlines(keepends=True)
        generated_lines = generated_cpp.splitlines(keepends=True)
        diff = "".join(difflib.unified_diff(
            original_lines, generated_lines,
            fromfile=file_info["filename"],
            tofile=file_info["filename"].rsplit(".", 1)[0] + ".cpp",
        ))

        # Store results
        result = {
            "generated_cpp": generated_cpp,
            "graph_json": graph_json,
            "diff": diff,
            "functions_found": len(functions),
            "edges_found": graph.number_of_edges(),
        }
        _result_registry[file_id] = result

        return ProcessResponse(
            file_id=file_id,
            status="completed",
            generated_cpp=generated_cpp,
            dependency_graph_json=graph_json,
            diff=diff,
            functions_found=len(functions),
            edges_found=graph.number_of_edges(),
        )

    except RuntimeError as e:
        # LLM connection errors, timeouts, etc.
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error processing file %s", file_id)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@app.get("/result/{file_id}", response_model=ProcessResponse)
async def get_result(file_id: str):
    """
    Return the generated C++ code, dependency graph JSON, and diff for a processed file.
    """
    if file_id not in _file_registry:
        raise HTTPException(status_code=404, detail=f"File '{file_id}' not found")

    if file_id not in _result_registry:
        raise HTTPException(
            status_code=404,
            detail=f"File '{file_id}' has not been processed yet. Call POST /process/{file_id} first.",
        )

    result = _result_registry[file_id]
    return ProcessResponse(
        file_id=file_id,
        status="completed",
        generated_cpp=result["generated_cpp"],
        dependency_graph_json=result["graph_json"],
        diff=result["diff"],
        functions_found=result["functions_found"],
        edges_found=result["edges_found"],
    )
