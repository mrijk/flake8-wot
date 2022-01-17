import ast

from flake8_warn_old_school_types import Plugin


def _results(s: str) -> set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {f"{line}:{col + 1} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case():
    assert _results("") == set()


def test_has_old_school_list():
    assert _results("from typing import List") == {"1:1 WOT001 don't import type List"}


def test_has_old_school_dict():
    assert _results("from typing import Dict") == {"1:1 WOT001 don't import type Dict"}


def test_has_old_school_tuple():
    assert _results("from typing import Tuple") == {"1:1 WOT001 don't import type Tuple"}


def test_has_multiple_wot_types():
    assert _results("from typing import Tuple, Dict") == {"1:1 WOT001 don't import type Tuple",
                                                          "1:1 WOT001 don't import type Dict"}


def test_generic_import_with_class_decl():
    code = """
import typing

class Foo:
    l: typing.List[int]
"""

    assert _results(code) == {"5:5 WOT002 don't use type typing.List"}


def test_generic_import_with_class_assign():
    code = """
import typing

foo = typing.List
"""

    assert _results(code) == {"4:1 WOT002 don't use type typing.List"}


def test_generic_import_with_function_decl_return():
    code = """
import typing

def foo() -> typing.List:
    return []
"""

    assert _results(code) == {"4:1 WOT002 don't use type typing.List"}


def test_generic_import_with_function_decl_args():
    code = """
import typing


def foo(l: typing.List):
    return l
"""

    assert _results(code) == {"5:1 WOT002 don't use type typing.List"}


def test_generic_import_with_function_call():
    code = """
import typing

print(typing.List)
"""

    assert _results(code) == {"4:1 WOT002 don't use type typing.List"}