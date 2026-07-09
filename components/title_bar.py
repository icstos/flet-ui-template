"""自定义标题栏组件模块。

提供无边框窗口的自定义标题栏，包括：
- 应用图标 + 多标签页栏（与窗口控制按钮同行）
- 最小化、最大化、关闭按钮
- 双击标题栏切换最大化
- 拖动标题栏空白区域移动窗口
"""

import asyncio

import flet as ft

from views.tab_bar import Tab, TabBar
import theme

# 窗口按钮悬停背景色
_BTN_HOVER_BG = "#2d3344"
_BTN_CLOSE_HOVER_BG = "#e81123"


@ft.component
def TitleBar(
    tabs: list[Tab],
    active_route: str,
    on_select,
    on_close,
):
    """自定义标题栏组件。

    将多标签页栏嵌入标题栏，与窗口控制按钮在同一行。
    管理窗口状态（最大化/还原），提供窗口控制按钮。

    Args:
        tabs: 标签列表。
        active_route: 当前激活的路由路径。
        on_select: 选中标签的回调。
        on_close: 关闭标签的回调。

    Returns:
        标题栏容器。
    """
    maximized, set_maximized = ft.use_state(False)
    hovered_btn, set_hovered_btn = ft.use_state("")

    def _apply_window() -> None:
        """应用窗口属性变更。"""
        ft.context.page.window.update()

    def on_window_event(e: ft.WindowEvent) -> None:
        """处理窗口事件，同步最大化状态。

        Args:
            e: 窗口事件对象。
        """
        match e.type:
            case ft.WindowEventType.MAXIMIZE:
                set_maximized(True)
            case ft.WindowEventType.UNMAXIMIZE:
                set_maximized(False)

    def setup_event() -> None:
        """组件挂载时注册窗口事件监听。"""
        page = ft.context.page
        page.window.on_event = on_window_event
        set_maximized(page.window.maximized)

    def cleanup_event() -> None:
        """组件卸载时清除窗口事件监听。"""
        ft.context.page.window.on_event = None

    ft.use_effect(setup_event, cleanup=cleanup_event)

    def on_minimize(_) -> None:
        """最小化窗口。"""
        w = ft.context.page.window
        w.minimized = True
        _apply_window()

    def on_toggle_maximize(_) -> None:
        """切换窗口最大化/还原状态。"""
        w = ft.context.page.window
        w.maximized = not w.maximized
        set_maximized(w.maximized)
        _apply_window()

    def on_double_tap(_) -> None:
        """双击标题栏切换最大化状态。"""
        on_toggle_maximize(_)

    def on_close_window(_) -> None:
        """关闭窗口。"""
        asyncio.create_task(ft.context.page.window.close())

    def _window_btn(
        btn_id: str, icon: str, on_click, *, is_close: bool = False
    ) -> ft.Container:
        """构建窗口控制按钮。

        Args:
            btn_id: 按钮标识符，用于悬停状态跟踪。
            icon: 图标名称。
            on_click: 点击回调。
            is_close: 是否为关闭按钮（特殊悬停样式）。

        Returns:
            窗口按钮容器。
        """
        is_hovered = hovered_btn == btn_id
        if is_close and is_hovered:
            bg_color = _BTN_CLOSE_HOVER_BG
            icon_color = "#ffffff"
        elif is_hovered:
            bg_color = _BTN_HOVER_BG
            icon_color = theme.C_WINDOW_BTN
        else:
            bg_color = None
            icon_color = theme.C_WINDOW_BTN

        return ft.Container(
            width=46,
            height=theme.TITLE_BAR_H,
            alignment=ft.Alignment.CENTER,
            border_radius=0,
            bgcolor=bg_color,
            ink=False,
            on_click=on_click,
            on_hover=lambda e, bid=btn_id: set_hovered_btn(
                bid if e.data == "true" else ""
            ),
            content=ft.Icon(icon, size=16 if is_close else 14, color=icon_color),
        )

    # 根据最大化状态选择图标
    maximize_icon = ft.Icons.FILTER_NONE if maximized else ft.Icons.CROP_SQUARE

    return ft.Container(
        height=theme.TITLE_BAR_H,
        bgcolor=theme.C_TITLE_BAR,
        content=ft.Row(
            controls=[
                # 可拖动区域（图标 + 标签栏 + 空白拖动区）
                ft.WindowDragArea(
                    expand=True,
                    maximizable=True,
                    content=ft.GestureDetector(
                        on_double_tap=on_double_tap,
                        content=ft.Row(
                            [
                                # 应用图标
                                ft.Container(
                                    padding=ft.Padding.only(left=12, right=8),
                                    content=ft.Icon(
                                        ft.Icons.APPS,
                                        size=16,
                                        color=theme.C_ACCENT,
                                    ),
                                ),
                                # 标签栏
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
                # 右侧：窗口控制按钮
                _window_btn("min", ft.Icons.REMOVE, on_minimize),
                _window_btn("max", maximize_icon, on_toggle_maximize),
                _window_btn("close", ft.Icons.CLOSE, on_close_window, is_close=True),
            ],
            spacing=0,
        ),
    )
