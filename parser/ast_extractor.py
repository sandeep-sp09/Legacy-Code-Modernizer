"""
Walks the raw Tree-sitter AST and extracts a simplified intermediate
representation (IR) that downstream modules (dependency graph, LLM
orchestration) can consume without needing to know Tree-sitter internals.

Supports both Pascal and C grammars.
"""

from .models import FunctionNode, VariableNode, CallNode, ControlFlowNode


def extract_functions(tree, language: str, source_code: str = "") -> list[FunctionNode]:
    """
    Walk the AST and return a list of FunctionNode objects representing
    every function/procedure defined in the source file.

    Args:
        tree: tree_sitter.Tree from ast_builder.parse_source()
        language: "pascal" or "c"
        source_code: the original source text (used to populate raw_source)

    Returns:
        list[FunctionNode]
    """
    language = language.lower()
    if language == "pascal":
        return _extract_pascal(tree, source_code)
    elif language == "c":
        return _extract_c(tree, source_code)
    else:
        raise ValueError(f"Unsupported language for extraction: '{language}'")


# ---------------------------------------------------------------------------
# Pascal extraction
# ---------------------------------------------------------------------------

def _extract_pascal(tree, source_code: str) -> list[FunctionNode]:
    """Extract functions/procedures and the main block from a Pascal AST."""
    root = tree.root_node
    functions: list[FunctionNode] = []
    source_lines = source_code.encode("utf-8") if source_code else b""

    for node in _walk(root):
        # defProc contains: declProc (signature) + block (body)
        if node.type == "defProc":
            fn = _extract_pascal_function(node, source_lines)
            if fn:
                functions.append(fn)

    # Also extract the program's main block (the top-level begin..end.)
    for node in root.children:
        if node.type == "program":
            main_fn = _extract_pascal_main_block(node, source_lines)
            if main_fn:
                functions.append(main_fn)

    return functions


def _extract_pascal_function(node, source_bytes: bytes) -> FunctionNode | None:
    """Extract a single Pascal function/procedure from a defProc node."""
    decl = _find_child(node, "declProc")
    if decl is None:
        return None

    # Function name
    name_node = _find_child(decl, "identifier")
    if name_node is None:
        return None
    name = name_node.text.decode()

    # Parameters
    params: list[VariableNode] = []
    args_node = _find_child(decl, "declArgs")
    if args_node:
        for arg in _children_of_type(args_node, "declArg"):
            param_type = ""
            type_node = _find_child(arg, "type")
            if type_node:
                param_type = type_node.text.decode()
            for ident in _children_of_type(arg, "identifier"):
                params.append(VariableNode(name=ident.text.decode(), var_type=param_type))

    # Body block
    block = _find_child(node, "block")

    # Local variables (look for declVars inside the defProc, before the block)
    local_vars: list[VariableNode] = []
    for child in node.children:
        if child.type == "declVars":
            local_vars.extend(_extract_pascal_vars(child))

    # Function calls inside body
    calls: list[CallNode] = []
    if block:
        calls = _extract_calls_pascal(block)

    # Control flow inside body
    control_flow: list[ControlFlowNode] = []
    if block:
        control_flow = _extract_control_flow_pascal(block)

    raw = node.text.decode() if node.text else ""

    return FunctionNode(
        name=name,
        parameters=params,
        local_variables=local_vars,
        calls=calls,
        control_flow=control_flow,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        raw_source=raw,
        language="pascal",
    )


def _extract_pascal_main_block(program_node, source_bytes: bytes) -> FunctionNode | None:
    """Extract the main begin..end. block as a __main__ pseudo-function."""
    # The main block is the last 'block' child of the program node
    blocks = [c for c in program_node.children if c.type == "block"]
    if not blocks:
        return None
    block = blocks[-1]

    # Top-level variables
    local_vars: list[VariableNode] = []
    for child in program_node.children:
        if child.type == "declVars":
            local_vars.extend(_extract_pascal_vars(child))

    calls = _extract_calls_pascal(block)
    control_flow = _extract_control_flow_pascal(block)

    return FunctionNode(
        name="__main__",
        parameters=[],
        local_variables=local_vars,
        calls=calls,
        control_flow=control_flow,
        start_line=block.start_point[0] + 1,
        end_line=block.end_point[0] + 1,
        raw_source=block.text.decode() if block.text else "",
        language="pascal",
    )


def _extract_pascal_vars(decl_vars_node) -> list[VariableNode]:
    """Extract variables from a declVars node."""
    variables: list[VariableNode] = []
    for var_decl in _children_of_type(decl_vars_node, "declVar"):
        var_type = ""
        type_node = _find_child(var_decl, "type")
        if type_node:
            var_type = type_node.text.decode()
        for ident in _children_of_type(var_decl, "identifier"):
            variables.append(VariableNode(name=ident.text.decode(), var_type=var_type))
    return variables


def _extract_calls_pascal(node) -> list[CallNode]:
    """Recursively find all exprCall nodes inside a Pascal block."""
    calls: list[CallNode] = []
    for child in _walk(node):
        if child.type == "exprCall":
            name_node = _find_child(child, "identifier")
            if name_node:
                calls.append(CallNode(
                    callee_name=name_node.text.decode(),
                    line=child.start_point[0] + 1,
                ))
    return calls


def _extract_control_flow_pascal(node) -> list[ControlFlowNode]:
    """Recursively find control-flow constructs in a Pascal block."""
    cf_types = {"ifStatement": "if", "whileStatement": "while",
                "forStatement": "for", "repeatStatement": "repeat"}
    result: list[ControlFlowNode] = []
    for child in _walk(node):
        if child.type in cf_types:
            result.append(ControlFlowNode(
                kind=cf_types[child.type],
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
            ))
    return result


# ---------------------------------------------------------------------------
# C extraction
# ---------------------------------------------------------------------------

def _extract_c(tree, source_code: str) -> list[FunctionNode]:
    """Extract functions from a C AST."""
    root = tree.root_node
    functions: list[FunctionNode] = []

    for node in root.children:
        if node.type == "function_definition":
            fn = _extract_c_function(node, source_code)
            if fn:
                functions.append(fn)

    return functions


def _extract_c_function(node, source_code: str) -> FunctionNode | None:
    """Extract a single C function from a function_definition node."""
    # Function name — inside function_declarator > identifier
    declarator = _find_child(node, "function_declarator")
    if declarator is None:
        return None

    name_node = _find_child(declarator, "identifier")
    if name_node is None:
        return None
    name = name_node.text.decode()

    # Parameters
    params: list[VariableNode] = []
    param_list = _find_child(declarator, "parameter_list")
    if param_list:
        for param_decl in _children_of_type(param_list, "parameter_declaration"):
            param_type = ""
            param_name = ""
            for child in param_decl.children:
                if child.type in ("primitive_type", "type_identifier", "sized_type_specifier"):
                    param_type = child.text.decode()
                elif child.type == "identifier":
                    param_name = child.text.decode()
                elif child.type == "pointer_declarator":
                    ident = _find_child(child, "identifier")
                    if ident:
                        param_name = ident.text.decode()
                    param_type += "*"
            if param_name:
                params.append(VariableNode(name=param_name, var_type=param_type))

    # Body
    body = _find_child(node, "compound_statement")

    # Local variables
    local_vars: list[VariableNode] = []
    if body:
        local_vars = _extract_c_local_vars(body)

    # Function calls
    calls: list[CallNode] = []
    if body:
        calls = _extract_calls_c(body)

    # Control flow
    control_flow: list[ControlFlowNode] = []
    if body:
        control_flow = _extract_control_flow_c(body)

    raw = node.text.decode() if node.text else ""

    return FunctionNode(
        name=name,
        parameters=params,
        local_variables=local_vars,
        calls=calls,
        control_flow=control_flow,
        start_line=node.start_point[0] + 1,
        end_line=node.end_point[0] + 1,
        raw_source=raw,
        language="c",
    )


def _extract_c_local_vars(body_node) -> list[VariableNode]:
    """Extract local variable declarations from a C compound_statement."""
    variables: list[VariableNode] = []
    for child in body_node.children:
        if child.type == "declaration":
            var_type = ""
            for sub in child.children:
                if sub.type in ("primitive_type", "type_identifier", "sized_type_specifier"):
                    var_type = sub.text.decode()
                elif sub.type == "init_declarator":
                    ident = _find_child(sub, "identifier")
                    if ident:
                        variables.append(VariableNode(
                            name=ident.text.decode(), var_type=var_type
                        ))
                elif sub.type == "identifier":
                    # Plain declaration without initializer
                    variables.append(VariableNode(
                        name=sub.text.decode(), var_type=var_type
                    ))
    return variables


def _extract_calls_c(node) -> list[CallNode]:
    """Recursively find all call_expression nodes inside a C body."""
    calls: list[CallNode] = []
    for child in _walk(node):
        if child.type == "call_expression":
            func_node = child.children[0] if child.children else None
            if func_node and func_node.type == "identifier":
                calls.append(CallNode(
                    callee_name=func_node.text.decode(),
                    line=child.start_point[0] + 1,
                ))
    return calls


def _extract_control_flow_c(node) -> list[ControlFlowNode]:
    """Recursively find control-flow constructs in a C body."""
    cf_types = {"if_statement": "if", "while_statement": "while",
                "for_statement": "for", "do_statement": "do-while",
                "switch_statement": "switch"}
    result: list[ControlFlowNode] = []
    for child in _walk(node):
        if child.type in cf_types:
            result.append(ControlFlowNode(
                kind=cf_types[child.type],
                start_line=child.start_point[0] + 1,
                end_line=child.end_point[0] + 1,
            ))
    return result


# ---------------------------------------------------------------------------
# Tree-sitter helpers
# ---------------------------------------------------------------------------

def _walk(node):
    """Depth-first walk yielding every node in the subtree."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _find_child(node, type_name: str):
    """Return the first direct child of the given type, or None."""
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _children_of_type(node, type_name: str):
    """Return all direct children of the given type."""
    return [c for c in node.children if c.type == type_name]
