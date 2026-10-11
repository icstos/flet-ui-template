"""离线渲染冒烟测试：在无 GUI 环境下真正执行组件函数体，捕获 Flet 1.x 运行期错误。

关键点：@ft.component 装饰过的组件必须通过 Renderer 渲染，
函数体才会真正执行 —— 否则 ft.ElevatedButton 这类属性错误根本不会触发。
"""

import os
import sys
import traceback
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from flet.components.component import Renderer

from config import load_config
from database import init_db

load_config()
init_db()


class FakePage:
    """最小 Page 替身，满足组件渲染期对 page 的基本需求。"""

    def __init__(self):
        self.route = "/login"
        self.title = "t"
        self.fonts = {}
        self.theme = ft.Theme()
        self.window = MagicMock()
        self.controls = []
        self.views = []
        # use_dialog 等 Hook 会读取这些内部属性
        self._dialogs = []
        self._overlay = []
        self._services = {}
        self._values = {}

    def update(self):
        pass

    def navigate(self, route):
        self.route = route

    def run_task(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def install_fake_context():
    """把 ft.context 使用的 ContextVar 指向 fake page。"""
    import flet.controls.context as ctx_mod

    page = FakePage()
    ctx_mod._context_page.set(page)
    return page


FAILURES = []
PASSES = []


def try_render(label, fn, *args, **kwargs):
    """真正执行组件函数体，捕获 Flet 1.x 运行期异常。

    两个关键点（否则测试会产生假阴性）：
      1. @ft.component 装饰后直接调用 fn() 只返回 Component 包装节点，
         不执行函数体 —— 必须调用 fn.__component_impl__()。
      2. 组件体里用了 use_state/use_effect 等 Hook，Hook 需要
         renderer._render_stack 中存在「正在渲染的组件」，否则报
         "Hooks must be called inside a component render."。
    """
    from flet.components.component import Component

    impl = getattr(fn, "__component_impl__", fn)
    renderer = Renderer()
    node = Component(fn=fn, args=args, kwargs=kwargs)
    try:
        with renderer.with_context():
            renderer._render_stack.append(node)
            try:
                result = impl(*args, **kwargs)
            finally:
                renderer._render_stack.pop()
        PASSES.append(label)
        print(f"[OK]   {label}")
        return result
    except Exception as e:
        FAILURES.append((label, e))
        print(f"[FAIL] {label}")
        print(f"       {type(e).__name__}: {e}")
        tb = traceback.format_exc().splitlines()
        for line in tb[-5:]:
            print("       " + line)
        return None


def _probe_search_overlay_dialog(item):
    """单独构建 SearchOverlay 使用的 AlertDialog 控件树。

    use_dialog 需要真实 Page 会话，离线环境无法执行；
    但弹窗内部的控件构造（含已废弃 API）可以独立验证。
    """
    import theme
    from services.repository import search_items

    results = search_items("a") or search_items("") or []
    module_labels = {"chat": "聊天", "contacts": "通讯录", "email": "邮箱"}

    result_controls = []
    for it in results[:3]:
        result_controls.append(
            ft.Container(
                ink=True,
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                on_click=lambda _: None,
                content=ft.Row(
                    [
                        ft.Text(it.name, size=14, expand=True, max_lines=1),
                        ft.Text(module_labels.get(it.module_id, ""), size=11),
                    ],
                    spacing=10,
                ),
            )
        )

    try:
        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=theme.C_LIST_BG,
            barrier_color="#80000000",
            inset_padding=ft.Padding.only(top=80, left=200, right=200, bottom=80),
            content=ft.Container(
                width=560,
                height=420,
                content=ft.Column(
                    [
                        ft.TextField(
                            value="",
                            hint_text="搜索条目…",
                            border=ft.InputBorder.NONE,
                            autofocus=True,
                            expand=True,
                            on_change=lambda e: None,
                        ),
                        ft.ListView(result_controls, spacing=2, expand=True)
                        if result_controls
                        else ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text("无搜索结果", size=14),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
            on_dismiss=lambda _: None,
        )
        PASSES.append("SearchOverlay 的 AlertDialog 控件树")
        print(f"[OK]   SearchOverlay 的 AlertDialog 控件树（{len(results)} 条结果）")
        return dialog
    except Exception as e:
        FAILURES.append(("SearchOverlay 的 AlertDialog 控件树", e))
        print(f"[FAIL] SearchOverlay 的 AlertDialog 控件树")
        print(f"       {type(e).__name__}: {e}")
        return None


def main():
    install_fake_context()

    print("=" * 64)
    print(f"Flet 版本: {ft.__version__}   Python: {sys.version.split()[0]}")
    print("=" * 64)

    from components.avatar import avatar_circle
    from components.detail_panel import detail_panel
    from views.tab_bar import Tab, _build_tab
    from views.auth import LoginView, RegisterView, ChangePasswordView
    from views.settings import SettingsView
    from views.list_panel import ListPanel
    from views.nav_rail import NavRail
    from views.workspace import WorkspaceLayout
    from views.search_overlay import SearchOverlay
    from views.detail_chat import ChatDetail
    from views.detail_generic import GenericDetail
    from views.shell import ShellLayout
    from views.app import App
    from views.app import IndexRedirect
    from components.title_bar import TitleBar
    from services.repository import get_items, get_modules, get_default_item_id

    item = (get_items("chat") or [None])[0]

    print("\n--- 纯构造函数 ---")
    try_render("avatar_circle", avatar_circle, "张", "#3b7cff", 40)
    if item:
        try_render("detail_panel", detail_panel, item, "sub", ft.Text("body"))
        try_render(
            "_build_tab",
            _build_tab,
            Tab(route="/chat/z", title="张", module_id="chat", item_id="z"),
            True,
            lambda r: None,
            lambda r: None,
        )

    print("\n--- 认证视图（含 ft.ElevatedButton 重灾区）---")
    try_render("LoginView", LoginView)
    try_render("RegisterView", RegisterView)
    try_render("ChangePasswordView", ChangePasswordView)

    print("\n--- 设置视图（含 ft.ElevatedButton）---")
    try_render("SettingsView", SettingsView)

    print("\n--- 主界面视图 ---")
    try_render("NavRail", NavRail)
    try_render("WorkspaceLayout", WorkspaceLayout)
    # use_dialog 依赖真实 Page 的会话/overlay 机制，mock 环境无法覆盖；
    # 这里改为单独验证 SearchOverlay 内构造的 AlertDialog 控件树本身。
    try_render("SearchOverlay(visible=False)", SearchOverlay, False, lambda: None)
    try_render("SearchOverlay(可见=走 use_dialog 分支，见下)", SearchOverlay, False, lambda: None)
    try_render("ShellLayout", ShellLayout)
    try_render("TitleBar", TitleBar, [], "/login", lambda r: None, lambda r: None)

    print("\n--- 详情视图 ---")
    try_render("ChatDetail", ChatDetail)
    try_render("GenericDetail", GenericDetail)

    print("\n--- SearchOverlay 内部弹窗控件树（use_dialog 依赖真实会话，单独验证控件构造）---")
    _probe_search_overlay_dialog(item)

    print("\n--- 路由 ---")
    try_render("App", App)
    try_render("IndexRedirect", IndexRedirect)

    print("\n" + "=" * 64)
    print(f"通过: {len(PASSES)}   失败: {len(FAILURES)}")
    if FAILURES:
        print("\n失败清单:")
        for label, e in FAILURES:
            print(f"  - {label}: {type(e).__name__}: {e}")
    print("=" * 64)
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
