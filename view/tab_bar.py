"""标签页栏（嵌入标题栏使用）。"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from models import ColorSettings
from view.contexts import use_container
from view.hooks import use_view_model
from viewmodel import TabData


def _build_tab(
    tab: TabData,
    is_active: bool,
    on_select: Callable[[str], None],
    on_close: Callable[[str], None],
    colors: ColorSettings,
) -> ft.Container:
    """构建单个标签。

    Args:
        tab: 标签数据。
        is_active: 是否为当前激活标签。
        on_select: 选中回调，接收路由。
        on_close: 关闭回调，接收路由。
        colors: 当前配色。

    Returns:
        标签容器。
    """
    return ft.Container(
        height=30,
        bgcolor=colors.content_bg if is_active else "transparent",
        border_radius=ft.BorderRadius.only(top_left=6, top_right=6),
        padding=ft.Padding.only(left=12, right=4, top=2, bottom=2),
        ink=True,
        on_click=lambda _: on_select(tab.route),
        content=ft.Row(
            [
                ft.Text(
                    tab.title,
                    size=13,
                    weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                    color=colors.text if is_active else colors.text_sec,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(
                    width=18,
                    height=18,
                    border_radius=4,
                    alignment=ft.Alignment.CENTER,
                    ink=True,
                    on_click=lambda _, route=tab.route: on_close(route),
                    content=ft.Icon(
                        ft.Icons.CLOSE, size=13, color=colors.text_sec
                    ),
                ),
            ],
            spacing=4,
            tight=True,
        ),
    )


@ft.component
def TabBar(
    tabs: tuple[TabData, ...],
    active_route: str,
    on_select: Callable[[str], None],
    on_close: Callable[[str], None],
):
    """水平排列全部标签，末尾留出窗口拖动区。

    Args:
        tabs: 标签集合。
        active_route: 当前激活路由。
        on_select: 选中回调。
        on_close: 关闭回调。

    Returns:
        标签栏控件。
    """
    theme = use_view_model(use_container().theme)

    if not tabs:
        return ft.Container(expand=True)

    return ft.Row(
        [
            *(
                _build_tab(tab, tab.route == active_route, on_select, on_close, theme.colors)
                for tab in tabs
            ),
            ft.Container(expand=True),
        ],
        spacing=2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )
