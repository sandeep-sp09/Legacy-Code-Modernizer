# Parser / AST Module

Responsible for turning raw Pascal/C source files into an Abstract Syntax Tree (AST)
using Tree-sitter, and exposing a clean structured representation (functions, loops,
conditionals, variables) for the dependency graph and LLM orchestration modules to consume.

## Files
- `ast_builder.py` — loads the Tree-sitter grammar and parses source into a raw AST.
- `ast_extractor.py` — walks the raw AST and extracts structured facts (function defs,
  calls, control-flow nodes) into a simpler intermediate representation (IR).
- `models.py` — data classes for the extracted IR (FunctionNode, LoopNode, etc).

## TODO
- [ ] Load Tree-sitter Pascal grammar
- [ ] Load Tree-sitter C grammar
- [ ] Implement extraction for function definitions
- [ ] Implement extraction for control-flow (if/while/for)
- [ ] Implement extraction for variable declarations
- [ ] Unit tests against sample files in /samples
