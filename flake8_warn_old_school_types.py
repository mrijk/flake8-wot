import importlib.metadata
from _ast import ImportFrom
from ast import NodeVisitor, AST
from typing import Generator, Any


OLD_SCHOOL_TYPES = ["List", "Tuple", "Dict"]


class Visitor(NodeVisitor):

    def __init__(self):
        self.problems: list[tuple[int, int, str]] = []

    def visit_ImportFrom(self, node: ImportFrom) -> None:
        for name in node.names:
            if name.name in OLD_SCHOOL_TYPES:
                self.problems.append((node.lineno, node.col_offset, name.name))
        self.generic_visit(node)


class Plugin:
    name = __name__
    version =  importlib.metadata.version(__name__)

    def __init__(self, tree: AST) -> None:
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, old_type in visitor.problems:
            yield line, col, f"WOT001 don't import type {old_type}", type(self)

