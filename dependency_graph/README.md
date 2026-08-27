# Dependency Graph Module

Builds a NetworkX graph representing function call relationships and control-flow
dependencies, using the IR produced by the parser module.

## Files
- `graph_builder.py` — converts a list of FunctionNode IR objects into a NetworkX DiGraph.
- `graph_export.py` — export/visualization helpers (e.g. to PNG/JSON for the frontend).

## TODO
- [ ] Build call graph (function -> function edges)
- [ ] Build control-flow graph within a function (optional, phase 2)
- [ ] Export graph as JSON for frontend rendering
- [ ] Export graph as PNG for the report
