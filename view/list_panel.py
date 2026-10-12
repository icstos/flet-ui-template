"""列表面板：条目列表 + 搜索 + 右键菜单 + 宽度调整。"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from models import Item
from view.contexts import use_container
from view.hooks import use_view_model
from view.widgets.avatar import avatar_circle
from viewmodel import ListPanelViewModel

_PINNED_BG = "#f0f5ff"
"""置顶条目的淡底色。"""


@ft.component
def ListPanel():
    """当前模块的条目列表。

    Returns:
        列表面板容器。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.list_panel)
    location = ft.use_route_location()

    def sync_route() -> None:
        """路由变化时重载列表，必要时跳到首个条目。"""
        target = view_model.sync_route(location)
        if target:
            ft.context.page.navigate(target)

    ft.use_effect(sync_route, dependencies=[location])

    colors = theme.colors

    def navigate(route: str) -> None:
        ft.context.page.navigate(route)

    def select_item(item_id: str) -> Callable[[ft.ControlEvent], None]:
        """生成条目的点击处理函数。"""

        def handler(_: ft.ControlEvent) -> None:
            navigate(view_model.item_route(item_id))

        return handler

    def run_action(action: str, item_id: str) -> Callable[[ft.ControlEvent], None]:
        """生成右键菜单动作的处理函数。"""

        def handler(_: ft.ControlEvent) -> None:
            target = view_model.activate(action, item_id)
            if target:
                navigate(target)

        return handler

    def on_divider_drag(event: ft.DragUpdateEvent) -> None:
        """拖动分隔条调整列表宽度。"""
        delta = event.local_delta.x if event.local_delta else 0
        view_model.resize_by(delta)

    def build_menu_items(item: Item) -> list[ft.PopupMenuItem]:
        """构建条目的右键菜单。"""
        return [
            ft.PopupMenuItem(
                content="标记为未读",
                icon=ft.Icons.MARK_AS_UNREAD,
                on_click=run_action("mark_unread", item.id),
            ),
            ft.PopupMenuItem(
                content="取消置顶" if item.is_pinned else "置顶",
                icon=(
                    ft.Icons.PUSH_PIN if item.is_pinned else ft.Icons.PUSH_PIN_OUTLINED
                ),
                on_click=run_action("toggle_pin", item.id),
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                content="隐藏",
                icon=ft.Icons.HIDE_SOURCE_OUTLINED,
                on_click=run_action("hide", item.id),
            ),
            ft.PopupMenuItem(
                content="删除",
                icon=ft.Icons.DELETE_OUTLINED,
                on_click=run_action("delete", item.id),
            ),
        ]

    def build_list_item(item: Item) -> ft.ContextMenu:
        """构建单个列表条目。"""
        is_selected = view_model.is_selected(item.id)

        row_content = ft.Row(
            [
                avatar_circle(item.name, item.color, 44),
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    item.name,
                                    size=14,
                                    weight=(
                                        ft.FontWeight.W_600
                                        if is_selected
                                        else ft.FontWeight.W_500
                                    ),
                                    color=colors.text,
                                    expand=True,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(item.time, size=11, color=colors.text_sec),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            item.preview,
                            size=12,
                            color=colors.accent if is_selected else colors.text_sec,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ],
            spacing=12,
        )

        return ft.ContextMenu(
            secondary_items=build_menu_items(item),
            secondary_trigger=ft.ContextMenuTrigger.DOWN,
            content=ft.Container(
                bgcolor=(
                    colors.accent_soft
                    if is_selected
                    else _PINNED_BG
                    if item.is_pinned
                    else None
                ),
                border=ft.Border.only(
                    left=ft.BorderSide(
                        3, colors.accent if is_selected else "transparent"
                    )
                ),
                padding=ft.Padding.only(left=13, right=14, top=10, bottom=10),
                ink=True,
                on_click=select_item(item.id),
                content=row_content,
            ),
        )

    return ft.Row(
        [
            ft.Container(
                width=view_model.width,
                bgcolor=colors.list_bg,
                border=ft.Border.only(right=ft.BorderSide(1, colors.border)),
                content=ft.Column(
                    [
                        ft.Container(
                            padding=ft.Padding.only(
                                left=16, right=16, top=14, bottom=10
                            ),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        view_model.module_label,
                                        size=18,
                                        weight=ft.FontWeight.W_700,
                                        color=colors.text,
                                    ),
                                    ft.TextField(
                                        value=view_model.query,
                                        on_change=lambda event: view_model.set_query(
                                            event.control.value or ""
                                        ),
                                        hint_text="搜索",
                                        prefix_icon=ft.Icons.SEARCH,
                                        height=36,
                                        text_size=13,
                                        border_radius=8,
                                        bgcolor=colors.search_bg,
                                        border_color="transparent",
                                        focused_border_color=colors.accent,
                                        content_padding=ft.Padding.symmetric(
                                            horizontal=4, vertical=2
                                        ),
                                        dense=True,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.ListView(
                                [build_list_item(item) for item in view_model.items],
                                spacing=0,
                                padding=0,
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
            ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
                drag_interval=8,
                on_horizontal_drag_update=on_divider_drag,
                content=ft.Container(
                    width=5,
                    bgcolor="transparent",
                    content=ft.Container(
                        width=1,
                        bgcolor=colors.border,
                        margin=ft.Margin.symmetric(vertical=48),
                    ),
                ),
            ),
        ],
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )


__all__ = ["ListPanel", "ListPanelViewModel"]
