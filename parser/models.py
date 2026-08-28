"""
Simple data classes representing the extracted intermediate representation (IR)
of the source code, independent of Tree-sitter's raw tree format.
"""

from dataclasses import dataclass, field


@dataclass
class VariableNode:
    name: str
    var_type: str


@dataclass
class CallNode:
    callee_name: str
    line: int


@dataclass
class ControlFlowNode:
    """Represents a control-flow construct (if, while, for, repeat)."""
    kind: str          # "if", "while", "for", "repeat"
    start_line: int
    end_line: int


@dataclass
class FunctionNode:
    name: str
    parameters: list[VariableNode] = field(default_factory=list)
    local_variables: list[VariableNode] = field(default_factory=list)
    calls: list[CallNode] = field(default_factory=list)
    control_flow: list[ControlFlowNode] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    raw_source: str = ""
    language: str = ""   # "pascal" or "c"
