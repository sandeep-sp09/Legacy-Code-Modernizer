"""
Pydantic models for API request/response bodies.
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    language: str
    message: str = "File uploaded successfully"


class ProcessResponse(BaseModel):
    file_id: str
    status: str
    generated_cpp: str
    dependency_graph_json: str
    diff: str
    functions_found: int
    edges_found: int


class ErrorResponse(BaseModel):
    detail: str


class ProcessResult(BaseModel):
    file_id: str
    generated_cpp: str
    dependency_graph_json: str
    diff: str
