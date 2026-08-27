"""
Pydantic models for API request/response bodies.
"""

from pydantic import BaseModel


class ProcessResult(BaseModel):
    file_id: str
    generated_cpp: str
    dependency_graph_json: str
    diff: str
