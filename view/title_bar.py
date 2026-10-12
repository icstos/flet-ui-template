"""自定义标题栏（无边框窗口）。

包含应用图标、标签页栏与窗口控制按钮。窗口的最小化 / 最大化 / 关闭
属于操作系统交互，在此就地执行；界面状态（最大化标记、悬停按钮）
来自 :class:`~viewmodel.title_bar.TitleBarViewModel`。
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import flet as ft

from view.contexts import use_container
from view.hooks import use_view_model
from view.tab_bar import TabBar
from viewmodel import TabData

_BTN_HOVER_BG = "#2d3344"
_BTN_CLOSE_HOVER_BG = "#e81123"


@ft.component
def TitleBar(
    tabs: tuple[TabData, ...],
    active_route: str,
    on_select: Callable[[str], None],
    on_close: Callable[[str], None],
):
    """标题栏。

    Args:
        tabs: 标签集合。
        active_route: 当前激活路由。
        on_select: 标签选中回调。
        on_close: 标签关闭回调。

    Returns:
        标题栏容器。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.title_bar)

    def _apply_window() -> None:
        """把窗口属性推送到客户端。"""
        ft.context.page.window.update()

    def on_window_event(event: ft.WindowEvent) -> None:
        """同步窗口最大化状态。"""
        match event.type:
            case ft.WindowEventType.MAXIMIZE:
                view_model.sync_maximized(True)
            case ft.WindowEventType.UNMAXIMIZE:
                view_model.sync_maximized(False)

    def setup_event() -> Callable[[], None]:
        """挂载时注册窗口事件监听，返回卸载清理函数。"""
        window = ft.context.page.window
        window.on_event = on_window_event
        view_model.sync_maximized(window.maximized)

        def cleanup() -> None:
            window.on_event = None

        return cleanup

    ft.use_effect(setup_event)

    def on_minimize(_: ft.ControlEvent) -> None:
        """最小化窗口。"""
        window = ft.context.page.window
        window.minimized = True
        _apply_window()

    def on_toggle_maximize(_: ft.ControlEvent | None = None) -> None:
        """在最大化与还原之间切换。"""
        window = ft.context.page.window
        window.maximized = not window.maximized
        view_model.sync_maximized(window.maximized)
        _apply_window()

    def on_close_window(_: ft.ControlEvent) -> None:
        """关闭窗口。"""
        asyncio.create_task(ft.context.page.window.close())

    def _window_btn(
        button_id: str,
        icon: ft.IconData,
        on_click: Callable[[ft.ControlEvent], None],
        *,
        is_close: bool = False,
    ) -> ft.Container:
        """构建窗口控制按钮（含悬停配色）。"""
        is_hovered = view_model.is_hovered(button_id)
        if is_close and is_hovered:
            bg_color, icon_color = _BTN_CLOSE_HOVER_BG, "#ffffff"
        elif is_hovered:
            bg_color, icon_color = _BTN_HOVER_BG, theme.colors.window_btn_icon
        else:
            bg_color, icon_color = None, theme.colors.window_btn_icon

        return ft.Container(
            width=46,
            height=theme.layout.title_bar_h,
            alignment=ft.Alignment.CENTER,
            border_radius=0,
            bgcolor=bg_color,
            ink=False,
            on_click=on_click,
            on_hover=lambda event, bid=button_id: view_model.set_hover(
                bid, event.data == "true"
            ),
            content=ft.Icon(icon, size=16 if is_close else 14, color=icon_color),
        )

    maximize_icon = (
        ft.Icons.FILTER_NONE if view_model.maximized else ft.Icons.CROP_SQUARE
    )

    return ft.Container(
        height=theme.layout.title_bar_h,
        bgcolor=theme.colors.title_bar,
        content=ft.Row(
            controls=[
                ft.WindowDragArea(
                    expand=True,
                    maximizable=True,
                    content=ft.GestureDetector(
                        on_double_tap=on_toggle_maximize,
                        content=ft.Row(
                            [
                                ft.Container(
                                    padding=ft.Padding.only(left=12, right=8),
                                    content=ft.Icon(
                                        ft.Icons.APPS,
                                        size=16,
                                        color=theme.colors.accent,
                                    ),
                                ),
                                TabBar(
                                    tabs=tabs,
                                    active_route=active_route,
                                    on_select=on_select,
                                    on_close=on_close,
                                ),
                            ],
                            spacing=0,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ),
                _window_btn("min", ft.Icons.REMOVE, on_minimize),
                _window_btn("max", maximize_icon, on_toggle_maximize),
                _window_btn("close", ft.Icons.CLOSE, on_close_window, is_close=True),
            ],
            spacing=0,
        ),
    )
