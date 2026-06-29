"""列表面板组件模块。

显示当前模块的条目列表，支持：
- 点击条目切换详情页
- 拖动分隔条调整列表宽度
- 搜索框（UI 占位）
"""

import flet as ft

from components.avatar import avatar_circle
from my_utils.route import parse_workspace
from services.repository import get_items, get_modules
import theme


@ft.component
def ListPanel():
    """列表面板组件。

    布局结构：
    - 顶部：模块标题 + 搜索框
    - 中部：可滚动的条目列表
    - 右侧：可拖动的宽度调整分隔条

    Returns:
        列表面板容器。
    """
    module_id, item_id = parse_workspace(ft.use_route_location())

    list_width, set_list_width = ft.use_state(theme.LIST_DEFAULT)
    items = get_items(module_id)
    module_label = next((m.label for m in get_modules() if m.id == module_id), "")

    # 无选中项时自动跳转到第一个条目
    if not item_id and items:
        ft.context.page.navigate(f"/{module_id}/{items[0].id}")
        return ft.Container()

    def select_item(iid: str):
        """生成选择指定条目的点击处理函数。

        Args:
            iid: 条目 ID。

        Returns:
            点击事件处理函数。
        """

        def handler(_):
            ft.context.page.navigate(f"/{module_id}/{iid}")

        return handler

    def on_divider_drag(e: ft.DragUpdateEvent):
        """处理分隔条拖动事件，调整列表面板宽度。

        Args:
            e: 拖动更新事件对象。
        """
        delta = e.local_delta.x if e.local_delta else 0
        new_width = max(theme.LIST_MIN, min(theme.LIST_MAX, list_width + delta))
        set_list_width(new_width)

    def _build_list_item(item) -> ft.Container:
        """构建单个列表条目组件。

        Args:
            item: 条目数据对象。

        Returns:
            列表条目容器。
        """
        is_selected = item.id == item_id
        return ft.Container(
            bgcolor=theme.C_ACCENT_SOFT if is_selected else None,
            border=ft.Border.only(
                left=ft.BorderSide(3, theme.C_ACCENT if is_selected else "transparent")
            ),
            padding=ft.Padding.only(left=13, right=14, top=10, bottom=10),
            ink=True,
            on_click=select_item(item.id),
            content=ft.Row(
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
                                        color=theme.C_TEXT,
                                        expand=True,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(item.time, size=11, color=theme.C_TEXT_SEC),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                item.preview,
                                size=12,
                                color=(
                                    theme.C_ACCENT if is_selected else theme.C_TEXT_SEC
                                ),
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                ],
                spacing=12,
            ),
        )

    # 构建所有列表条目
    list_items = [_build_list_item(item) for item in items]

    return ft.Row(
        [
            # 列表面板主体
            ft.Container(
                width=list_width,
                bgcolor=theme.C_LIST_BG,
                border=ft.Border.only(right=ft.BorderSide(1, theme.C_BORDER)),
                content=ft.Column(
                    [
                        # 顶部标题 + 搜索框
                        ft.Container(
                            padding=ft.Padding.only(
                                left=16, right=16, top=14, bottom=10
                            ),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        module_label,
                                        size=18,
                                        weight=ft.FontWeight.W_700,
                                        color=theme.C_TEXT,
                                    ),
                                    ft.Container(
                                        height=36,
                                        border_radius=8,
                                        bgcolor=theme.C_SEARCH_BG,
                                        padding=ft.Padding.symmetric(horizontal=12),
                                        content=ft.Row(
                                            [
                                                ft.Icon(
                                                    ft.Icons.SEARCH,
                                                    size=18,
                                                    color=theme.C_TEXT_SEC,
                                                ),
                                                ft.Text(
                                                    "搜索",
                                                    size=13,
                                                    color=theme.C_TEXT_SEC,
                                                ),
                                            ],
                                            spacing=8,
                                        ),
                                    ),
                                ],
                                spacing=10,
                            ),
                        ),
                        # 可滚动的条目列表
                        ft.Container(
                            expand=True,
                            content=ft.ListView(
                                list_items, spacing=0, padding=0, expand=True
                            ),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
            # 宽度调整分隔条
            ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
                drag_interval=8,
                on_horizontal_drag_update=on_divider_drag,
                content=ft.Container(
                    width=5,
                    bgcolor="transparent",
                    content=ft.Container(
                        width=1,
                        bgcolor=theme.C_BORDER,
                        margin=ft.Margin.symmetric(vertical=48),
                    ),
                ),
            ),
        ],
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
