import importlib.metadata
from ast import NodeVisitor, AST, ImportFrom, AnnAssign, Assign, FunctionDef, Call
from typing import Generator, Any


OLD_SCHOOL_TYPES = ["Dict", "FrozenSet", "List", "Set", "Tuple"]


def _old_school(type_name: str) -> bool:
    return type_name in OLD_SCHOOL_TYPES


class Visitor(NodeVisitor):

    def __init__(self):
        self.problems: dict[str, list[tuple[int, int, str]]] = {
            "WOT001": [],
            "WOT002": [],
        }

    def _report_problem(self, key: str, node: AST, type_name: str):
        self.problems[key].append((node.lineno, node.col_offset, type_name))

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        if annotation := node.annotation:
            if value := getattr(annotation, "value", False):
                if type_name := getattr(value, "attr", False):
                    if _old_school(type_name):
                        self._report_problem("WOT002", node, type_name)

    def visit_Assign(self, node: Assign) -> Any:
        if not isinstance(node.value, Call):
            if type_name := getattr(node.value, "attr", False):
                if _old_school(type_name):
                    self._report_problem("WOT002", node, type_name)

    def visit_Call(self, node: Call) -> Any:
        for arg in node.args:
            if type_name := getattr(arg, "attr", False):
                if _old_school(type_name):
                    self._report_problem("WOT002", node, type_name)

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        if returns := node.returns:
            if type_name := getattr(returns, "attr", False):
                if _old_school(type_name):
                    self._report_problem("WOT002", node, type_name)

        if args := node.args.args:
            for arg in args:
                if type_name := getattr(arg.annotation, "attr", False):
                    if _old_school(type_name):
                        self._report_problem("WOT002", node, type_name)

    def visit_ImportFrom(self, node: ImportFrom) -> None:
        for name in node.names:
            type_name = name.name
            if _old_school(type_name):
                self._report_problem("WOT001", node, type_name)
        self.generic_visit(node)


class Plugin:
    name = __name__
    version =  importlib.metadata.version(__name__)

    def __init__(self, tree: AST) -> None:
        self._tree = tree

    def _report(self, visitor: Visitor) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        for line, col, old_type in visitor.problems["WOT001"]:
            yield line, col, f"WOT001 don't import type {old_type}", type(self)
        for line, col, old_type in visitor.problems["WOT002"]:
            yield line, col, f"WOT002 don't use type typing.{old_type}", type(self)

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        return self._report(visitor)


