"""多标签页栏组件模块。

提供类似浏览器的标签页栏，支持打开、切换、关闭标签。
每个标签对应一个路由路径，点击标签切换到对应页面。
标签栏嵌入标题栏中，与窗口控制按钮同行。
"""

from dataclasses import dataclass

import flet as ft

import theme


@dataclass
class Tab:
    """标签页数据结构。

    Attributes:
        route: 路由路径，作为标签唯一标识。
        title: 标签显示标题。
        module_id: 所属模块 ID。
        item_id: 条目 ID。
    """

    route: str
    title: str
    module_id: str
    item_id: str


def _build_tab(
    tab: Tab,
    is_active: bool,
    on_select,
    on_close,
) -> ft.Container:
    """构建单个标签控件。

    Args:
        tab: 标签数据。
        is_active: 是否为当前激活标签。
        on_select: 选中标签的回调。
        on_close: 关闭标签的回调。

    Returns:
        标签容器控件。
    """
    return ft.Container(
        height=30,
        bgcolor=theme.C_CONTENT_BG if is_active else "transparent",
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
                    color=theme.C_TEXT if is_active else theme.C_TEXT_SEC,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(
                    width=18,
                    height=18,
                    border_radius=4,
                    alignment=ft.Alignment.CENTER,
                    ink=True,
                    on_click=lambda _, r=tab.route: on_close(r),
                    content=ft.Icon(
                        ft.Icons.CLOSE,
                        size=13,
                        color=theme.C_TEXT_SEC,
                    ),
                ),
            ],
            spacing=4,
            tight=True,
        ),
    )


@ft.component
def TabBar(
    tabs: list[Tab],
    active_route: str,
    on_select,
    on_close,
):
    """标签页栏组件。

    水平排列所有标签，末尾填充空白区域用于窗口拖动。
    设计为嵌入标题栏使用，无自身背景色和边框。

    Args:
        tabs: 标签列表。
        active_route: 当前激活的路由路径。
        on_select: 选中标签的回调，接收 route 参数。
        on_close: 关闭标签的回调，接收 route 参数。

    Returns:
        标签栏 Row 控件。
    """
    if not tabs:
        return ft.Container(expand=True)

    tab_controls = [
        _build_tab(tab, tab.route == active_route, on_select, on_close)
        for tab in tabs
    ]

    return ft.Row(
        tab_controls + [ft.Container(expand=True)],
        spacing=2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )
