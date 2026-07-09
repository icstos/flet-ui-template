"""应用外壳布局模块。

提供应用的最外层布局结构：标题栏 + 侧边导航栏 + 内容区域。
同时注册全局快捷键 Ctrl+Shift+F 触发全局搜索弹窗。
"""

import flet as ft

from components.title_bar import TitleBar
from views.nav_rail import NavRail
from views.search_overlay import SearchOverlay


@ft.component
def ShellLayout():
    """应用外壳布局组件。

    垂直布局：
    - 顶部：标题栏（TitleBar）
    - 下方：水平排列的侧边导航栏 + 路由内容区

    通过 use_effect 注册全局键盘事件监听，
    检测 Ctrl+Shift+F 时打开全局搜索弹窗。

    Returns:
        外壳布局容器。
    """
    show_search, set_show_search = ft.use_state(False)

    def setup_keyboard():
        """注册全局键盘快捷键监听。"""
        page = ft.context.page

        def on_keyboard(e: ft.KeyboardEvent):
            if e.ctrl and e.shift and e.key == "F":
                set_show_search(True)
            elif e.key == "Escape":
                set_show_search(False)

        page.on_keyboard_event = on_keyboard

        def cleanup():
            page.on_keyboard_event = None

        return cleanup

    ft.use_effect(setup_keyboard, dependencies=[])

    outlet = ft.use_route_outlet()
    return ft.Column(
        [
            TitleBar(),
            ft.Row(
                [NavRail(), ft.Container(content=outlet, expand=True)],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            SearchOverlay(show_search, lambda: set_show_search(False)),
        ],
        expand=True,
        spacing=0,
    )
