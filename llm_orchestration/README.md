# LLM Orchestration Module

Handles prompt construction, chunking of code + AST/graph context, calling the LLM
to generate modern C++, and validating the generated output for syntax correctness
and structural fidelity to the original logic.

## Files
- `prompt_builder.py` — builds prompts combining source code, extracted IR, and
  dependency-graph context.
- `llm_client.py` — wraps the LLM API call.
- `validator.py` — syntax-checks generated C++ and flags hallucinated symbols
  (variables/functions that don't exist in the original source).

## TODO
- [ ] Design chunking strategy for large source files
- [ ] Build prompt template (source + IR + graph context -> C++ output)
- [ ] Wire up LLM API call
- [ ] Implement syntax validation (e.g. via a C++ parser/compiler dry-run)
- [ ] Implement "no hallucinated symbols" check against original IR
- [ ] Retry/repair loop for failed validations
