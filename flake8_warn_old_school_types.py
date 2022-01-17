import importlib.metadata
from _ast import ImportFrom, AnnAssign
from ast import NodeVisitor, AST
from typing import Generator, Any


OLD_SCHOOL_TYPES = ["List", "Tuple", "Dict"]


def _old_school(type_name: str) -> bool:
    return type_name in OLD_SCHOOL_TYPES


class Visitor(NodeVisitor):

    def __init__(self):
        self.problems_001: list[tuple[int, int, str]] = []
        self.problems_002: list[tuple[int, int, str]] = []

    def visit_ImportFrom(self, node: ImportFrom) -> None:
        for name in node.names:
            if _old_school(name.name):
                self.problems_001.append((node.lineno, node.col_offset, name.name))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        type_name = node.annotation.value.attr
        if _old_school(type_name):
            self.problems_002.append((node.lineno, node.col_offset, type_name))


class Plugin:
    name = __name__
    version =  importlib.metadata.version(__name__)

    def __init__(self, tree: AST) -> None:
        self._tree = tree

    def _report(self, visitor: Visitor) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        for line, col, old_type in visitor.problems_001:
            yield line, col, f"WOT001 don't import type {old_type}", type(self)
        for line, col, old_type in visitor.problems_002:
            yield line, col, f"WOT002 don't use type typing.{old_type}", type(self)

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        return self._report(visitor)


