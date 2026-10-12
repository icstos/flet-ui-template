"""应用外壳布局：标题栏 + 导航栏 + 内容区 + 全局搜索。"""

from __future__ import annotations

import flet as ft

from view.contexts import use_container
from view.hooks import use_view_model
from view.nav_rail import NavRail
from view.search_overlay import SearchOverlay
from view.title_bar import TitleBar

_SEARCH_KEY = "F"


@ft.component
def ShellLayout():
    """主应用骨架。

    Returns:
        外壳布局容器。
    """
    container = use_container()
    shell = use_view_model(container.shell)
    search = use_view_model(container.search_overlay)

    location = ft.use_route_location()

    def sync_route() -> None:
        """同步标签页，并在未登录时跳转登录页。"""
        target = shell.sync_location(location)
        if target:
            ft.context.page.navigate(target)

    ft.use_effect(sync_route, dependencies=[location])

    def setup_keyboard():
        """注册全局快捷键，返回卸载清理函数。"""
        page = ft.context.page

        def on_keyboard(event: ft.KeyboardEvent) -> None:
            if event.ctrl and event.shift and event.key == _SEARCH_KEY:
                search.open()
            elif event.key == "Escape":
                search.close()

        page.on_keyboard_event = on_keyboard

        def cleanup() -> None:
            page.on_keyboard_event = None

        return cleanup

    ft.use_effect(setup_keyboard, dependencies=[])

    def select_tab(route: str) -> None:
        """切换到指定标签。"""
        ft.context.page.navigate(route)

    def close_tab(route: str) -> None:
        """关闭标签，必要时跳到相邻标签。"""
        target = shell.close_tab(route)
        if target:
            ft.context.page.navigate(target)

    outlet = ft.use_route_outlet()

    return ft.Column(
        [
            TitleBar(
                tabs=shell.tabs,
                active_route=location,
                on_select=select_tab,
                on_close=close_tab,
            ),
            ft.Row(
                [NavRail(), ft.Container(content=outlet, expand=True)],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            SearchOverlay(),
        ],
        expand=True,
        spacing=0,
    )
