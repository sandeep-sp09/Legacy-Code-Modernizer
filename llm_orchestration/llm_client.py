"""
Thin wrapper around the LLM API call used for code generation.
"""


def generate_cpp(system_prompt: str, user_prompt: str) -> str:
    """
    Calls the LLM and returns the generated C++ code as a string.
    """
    # TODO: wire up actual API call (e.g. Anthropic Messages API)
    raise NotImplementedError
