"""
A minimal, local LangGraph-like SDK for building simple agentic flows.
This is intentionally small and local so the flow can run without an external
`langgraph` package. Use the classes here to compose nodes and run them.
"""
from typing import Any, Callable, Dict


class Node:
    def __init__(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.func = func

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        out = self.func(context)
        if not isinstance(out, dict):
            raise TypeError(
                f"Node {self.name} must return a dict, got {type(out)}")
        context.update(out)
        return out


class Flow:
    def __init__(self, name: str):
        self.name = name
        self.nodes = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def run(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        ctx = {} if initial_context is None else dict(initial_context)
        for node in self.nodes:
            node.run(ctx)
        return ctx


def node(name: str):
    def decorator(func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        return Node(name, func)
    return decorator
