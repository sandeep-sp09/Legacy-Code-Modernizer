"""
Builds prompts for the LLM by combining:
  - the original source chunk
  - the extracted IR (functions, variables, calls) from the parser module
  - relevant dependency-graph context (what this function calls / is called by)
"""


SYSTEM_PROMPT = """You are a code modernization assistant. You convert legacy
Pascal/C source code into idiomatic, modern C++. You must preserve the exact
logic and behavior of the original code. Do not invent variables, functions,
or behavior that is not present in the original source or its stated context."""


def build_prompt(source_chunk: str, function_ir, graph_context: str) -> str:
    """
    Args:
        source_chunk: the raw original source code for this function/chunk.
        function_ir: parser.models.FunctionNode for this chunk.
        graph_context: short text description of related functions from the
            dependency graph (callers/callees).

    Returns:
        A fully-formed user prompt string to send to the LLM.
    """
    # TODO: implement templated prompt construction
    raise NotImplementedError
