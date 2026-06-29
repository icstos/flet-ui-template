"""自定义标题栏组件模块。

提供无边框窗口的自定义标题栏，包括：
- 窗口图标和标题
- 最小化、最大化、关闭按钮
- 双击标题栏切换最大化
- 拖动标题栏移动窗口
"""

import asyncio

import flet as ft

from config import get_config
import theme

# 窗口按钮悬停背景色
_BTN_HOVER_BG = "#2d3344"
_BTN_CLOSE_HOVER_BG = "#e81123"


@ft.component
def TitleBar():
    """自定义标题栏组件。

    管理窗口状态（最大化/还原），提供窗口控制按钮。

    Returns:
        标题栏容器。
    """
    win = get_config().window
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

    def on_close(_) -> None:
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
                # 左侧：可拖动区域（图标 + 标题）
                ft.WindowDragArea(
                    expand=True,
                    maximizable=True,
                    content=ft.GestureDetector(
                        on_double_tap=on_double_tap,
                        content=ft.Container(
                            padding=ft.Padding.only(left=12),
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.APPS, size=16, color=theme.C_ACCENT
                                    ),
                                    ft.Text(
                                        win.title,
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=theme.C_TITLE_TEXT,
                                    ),
                                    ft.Text(
                                        f"· {win.subtitle}",
                                        size=12,
                                        color=theme.C_TITLE_SUB,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ),
                    ),
                ),
                # 右侧：窗口控制按钮
                _window_btn("min", ft.Icons.REMOVE, on_minimize),
                _window_btn("max", maximize_icon, on_toggle_maximize),
                _window_btn("close", ft.Icons.CLOSE, on_close, is_close=True),
            ],
            spacing=0,
        ),
    )
