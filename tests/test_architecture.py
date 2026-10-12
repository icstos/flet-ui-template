"""架构约束测试：验证分层与依赖方向。

规则（来自需求）：
    * 单向依赖 View -> ViewModel -> Service -> Infra；
    * 所有层可依赖 Models；
    * 禁止跨层调用与反向依赖；
    * ViewModel 不依赖任何 Flet UI 组件。

实现方式：静态解析各层的 import 语句，断言不存在违规依赖。
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# 层 -> 允许直接导入的顶层包
ALLOWED_IMPORTS: dict[str, frozenset[str]] = {
    "models": frozenset({"models"}),
    "infra": frozenset({"models", "infra"}),
    "service": frozenset({"models", "infra", "service"}),
    "viewmodel": frozenset({"models", "service", "viewmodel"}),
    "view": frozenset({"models", "viewmodel", "view"}),
}

# 组合根与入口可以引用任意层
ROOT_MODULES: frozenset[str] = frozenset({"container", "main"})

# 禁止出现在 viewmodel 中的外部库
FORBIDDEN_IN_VIEWMODEL: frozenset[str] = frozenset({"flet"})

LAYERS = tuple(ALLOWED_IMPORTS)


def _python_files(package: str) -> list[Path]:
    return sorted((ROOT / package).rglob("*.py"))


def _imported_roots(path: Path) -> set[str]:
    """返回文件顶层 import 的第一个包名。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # 相对导入，忽略
                continue
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots


def _stdlib_and_third_party() -> frozenset[str]:
    """本项目的层名之外的包名视为标准库/第三方，不参与分层断言。"""
    return frozenset(sys.stdlib_module_names)


@pytest.mark.parametrize("layer", LAYERS)
def test_layer_dependency_direction(layer: str) -> None:
    """每层只能依赖自身与更低层（或 models）。"""
    allowed = ALLOWED_IMPORTS[layer]
    other_layers = {name for name in LAYERS if name != layer}
    violations: list[str] = []

    for path in _python_files(layer):
        for root in _imported_roots(path):
            if root in other_layers and root not in allowed:
                violations.append(f"{path.relative_to(ROOT)} 导入了 {root}")

    assert not violations, "违反依赖方向:\n" + "\n".join(violations)


def test_viewmodel_has_no_flet_dependency() -> None:
    """视图模型层必须是纯 Python，不得触碰任何 UI 组件库。"""
    violations: list[str] = []
    for path in _python_files("viewmodel"):
        forbidden = _imported_roots(path) & FORBIDDEN_IN_VIEWMODEL
        if forbidden:
            violations.append(f"{path.relative_to(ROOT)} 导入了 {sorted(forbidden)}")
    assert not violations, "视图模型层不得依赖 Flet:\n" + "\n".join(violations)


def test_service_does_not_import_concrete_infra() -> None:
    """业务层只能依赖抽象接口，不得引用基础设施的具体实现模块。"""
    concrete = {
        "config_store",
        "database",
        "auth_store",
        "password_hasher",
        "user_repository",
        "workspace_repository",
        "seed",
    }
    violations: list[str] = []
    for path in _python_files("service"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[0] == "infra" and len(parts) > 1 and parts[1] in concrete:
                    violations.append(
                        f"{path.relative_to(ROOT)} 导入了具体实现 {node.module}"
                    )
    assert not violations, "业务层不得依赖具体技术实现:\n" + "\n".join(violations)


def test_models_is_dependency_free() -> None:
    """模型层不得依赖任何其它业务层。"""
    violations: list[str] = []
    consumers = {"infra", "service", "viewmodel", "view"}
    for path in _python_files("models"):
        for root in _imported_roots(path):
            if root in consumers:
                violations.append(f"{path.relative_to(ROOT)} 导入了 {root}")
    assert not violations, "模型层必须保持无依赖:\n" + "\n".join(violations)


def test_view_layer_exists_and_is_only_layer_touching_flet() -> None:
    """只有视图层（与入口）允许依赖 Flet。"""
    offenders: list[str] = []
    for layer in ("models", "infra", "service", "viewmodel"):
        for path in _python_files(layer):
            if "flet" in _imported_roots(path):
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, "仅视图层可使用 Flet，违规文件:\n" + "\n".join(offenders)
