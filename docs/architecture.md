# Architecture Overview

```
[Source .pas/.c] 
      |
      v
[parser/] --------> AST -> IR (FunctionNode, VariableNode, CallNode)
      |
      v
[dependency_graph/] -> NetworkX DiGraph (call graph)
      |
      v
[llm_orchestration/] -> Prompt (source + IR + graph context) -> LLM -> Generated C++
      |                                                              |
      v                                                              v
   [validator]  <----------------------------------------------- syntax + hallucination check
      |
      v
[backend/] -> API layer tying it all together
      |
      v
[frontend/] -> Upload UI, graph view, diff view
```

## Module ownership
See root README.md for the current role assignments.
