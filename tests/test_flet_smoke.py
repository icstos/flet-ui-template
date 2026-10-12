"""组件渲染冒烟测试：离线执行全部组件的函数体，捕获运行期错误。

三个关键点（否则会产生**假阴性**）：
    1. ``@ft.component`` 装饰后直接调用只返回包装节点，**不执行函数体**，
       必须调用 ``fn.__component_impl__()``；
    2. 组件内的 ``use_state`` / ``use_effect`` 等 Hook 需要
       ``renderer._render_stack`` 中存在「正在渲染的组件」；
    3. 组件通过 ``use_container()`` 取依赖，因此必须用
       ``provide_container`` 把容器压入渲染上下文。

该测试能在秒级发现问题，但**不能**替代真机验证：
Flutter 侧的渲染失败（灰块）只有截图才能发现。
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import flet as ft
from flet.components.component import Component, Renderer


class _FakeSession:
    """最小会话替身：use_dialog 会向其调度更新。"""

    components_mode = False

    def schedule_update(self, *args: object, **kwargs: object) -> None:
        return None

    def patch_control(self, *args: object, **kwargs: object) -> None:
        return None


class FakePage:
    """最小 Page 替身，供组件渲染期读取路由、弹窗等属性。"""

    def __init__(self) -> None:
        # use_dialog 会要求 _dialogs 是可被弱引用的控件（而非普通 list）
        from flet.controls.base_page import Dialogs

        self.route = "/chat/zhang"
        self.title = "test"
        self.fonts: dict[str, str] = {}
        self.theme = ft.Theme()
        self.window = MagicMock()
        self.session = _FakeSession()
        self.controls: list[ft.Control] = []
        self.views: list[object] = []
        self._dialogs = Dialogs()
        self._overlay: list[ft.Control] = []
        self._services: dict[str, object] = {}
        self._values: dict[str, object] = {}

    def update(self) -> None:
        pass

    def navigate(self, route: str) -> None:
        self.route = route

    def run_task(self, *args: object, **kwargs: object) -> None:
        pass

    def _prepare_dialog(self, dialog: ft.Control) -> None:
        """真实 Page 会在此设置弹窗父级并包装 on_dismiss。

        离线冒烟只关心「弹窗控件树能否构造成功」，因此留空。
        """


@pytest.fixture(autouse=True)
def fake_page() -> FakePage:
    """把 ft.context 使用的 ContextVar 指向替身页面。"""
    import flet.controls.context as context_module

    page = FakePage()
    context_module._context_page.set(page)
    return page


def render(container, fn, *args):
    """在「容器上下文 + 组件渲染栈」中真正执行组件函数体。

    Flet 的 ``use_context`` 是沿组件节点的 ``_contexts`` **快照**回溯查找的，
    因此组件节点必须在「容器上下文已生效」之后创建，
    否则快照里没有容器，``use_container()`` 会拿到默认值。
    """
    from view.contexts import provide_container

    impl = getattr(fn, "__component_impl__", fn)
    renderer = Renderer()
    result: object = None

    def build() -> object:
        nonlocal result
        node = Component(fn=fn, args=args, kwargs={})
        node._contexts = renderer._snapshot_contexts()
        renderer._render_stack.append(node)
        try:
            result = impl(*args)
        finally:
            renderer._render_stack.pop()
        return result

    with renderer.with_context():
        provide_container(container, build)
    return result


def test_container_assembly(container) -> None:
    """容器装配后核心依赖齐备。"""
    assert container.theme.colors.accent
    assert len(container.workspace_service.list_modules()) == 3
    assert container.shell.tabs == ()


def test_all_components_render(container) -> None:
    """逐个渲染全部组件，任何异常都视为失败。"""
    from view.app import App, IndexRedirect, RootView
    from view.auth import ChangePasswordView, LoginView, RegisterView
    from view.detail_chat import ChatDetail
    from view.detail_generic import GenericDetail
    from view.list_panel import ListPanel
    from view.nav_rail import NavRail
    from view.search_overlay import SearchOverlay
    from view.settings import SettingsView
    from view.shell import ShellLayout
    from view.title_bar import TitleBar
    from view.widgets.avatar import avatar_circle
    from view.widgets.detail_panel import detail_panel
    from view.workspace import WorkspaceLayout

    # 准备工作区与详情状态，让组件有真实数据可渲染
    container.list_panel.sync_route("/chat/zhang")
    container.chat_detail.load("zhang")
    container.generic_detail.load("dept_rd")
    item = container.workspace_service.get_item("zhang")
    assert item is not None

    cases: list[tuple[str, object, tuple]] = [
        ("avatar_circle", avatar_circle, ("张", "#3b7cff", 40)),
        (
            "detail_panel",
            detail_panel,
            (item, "副标题", ft.Text("body"), container.theme.colors),
        ),
        (
            "TitleBar(无标签)",
            TitleBar,
            ((), "/chat/zhang", lambda r: None, lambda r: None),
        ),
        ("NavRail", NavRail, ()),
        ("ListPanel", ListPanel, ()),
        ("WorkspaceLayout", WorkspaceLayout, ()),
        ("ChatDetail", ChatDetail, ()),
        ("GenericDetail", GenericDetail, ()),
        ("SearchOverlay", SearchOverlay, ()),
        ("LoginView", LoginView, ()),
        ("RegisterView", RegisterView, ()),
        ("ChangePasswordView", ChangePasswordView, ()),
        ("SettingsView", SettingsView, ()),
        ("ShellLayout", ShellLayout, ()),
        ("IndexRedirect", IndexRedirect, ()),
        ("App", App, ()),
        ("RootView", RootView, ()),
    ]

    failures: list[str] = []
    for label, fn, args in cases:
        try:
            render(container, fn, *args)
        except Exception as error:  # noqa: BLE001 - 汇总所有失败
            failures.append(
                f"{label}: {type(error).__name__}: {error}\n"
                + "\n".join(traceback.format_exc().splitlines()[-4:])
            )

    assert not failures, "以下组件渲染失败:\n\n" + "\n\n".join(failures)


def test_title_bar_with_tabs(container) -> None:
    """有标签时标题栏可渲染（覆盖 TabBar 非空分支）。"""
    from view.title_bar import TitleBar
    from viewmodel import LoginViewModel

    login = LoginViewModel(container.auth_service, container.workspace_service)
    login.set_username("admin")
    login.set_password("123456")
    login.submit()

    container.shell.sync_location("/chat/zhang")
    assert len(container.shell.tabs) == 1

    render(
        container,
        TitleBar,
        container.shell.tabs,
        "/chat/zhang",
        lambda r: None,
        lambda r: None,
    )


def test_search_overlay_with_results(container) -> None:
    """弹窗打开且有结果时可渲染（覆盖结果列表分支）。"""
    from view.search_overlay import SearchOverlay

    container.search_overlay.open()
    container.search_overlay.set_query("张三")
    assert container.search_overlay.results

    render(container, SearchOverlay)


def test_chat_detail_without_item_renders_placeholder(container) -> None:
    """条目不存在时渲染占位面板（覆盖空分支）。"""
    from view.detail_chat import ChatDetail

    render(container, ChatDetail)
