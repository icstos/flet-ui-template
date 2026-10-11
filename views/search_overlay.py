"""全局搜索弹窗组件模块。

提供类似 Spotlight 的全局搜索弹窗，支持跨所有模块搜索条目，
通过快捷键 Ctrl+Shift+F 触发。
"""

import flet as ft

from components.avatar import avatar_circle
from services.repository import get_modules, search_items
import theme


@ft.component
def SearchOverlay(show: bool, on_close):
    """全局搜索弹窗组件。

    使用 AlertDialog 实现居顶搜索弹窗，包含搜索输入框和结果列表。
    点击搜索结果可跳转到对应条目页面。

    Args:
        show: 是否显示弹窗。
        on_close: 关闭弹窗的回调函数。

    Returns:
        空容器（弹窗通过 use_dialog 挂载到页面 overlay）。
    """
    query, set_query = ft.use_state("")
    results = search_items(query) if show else []
    modules = get_modules()
    module_labels = {m.id: m.label for m in modules}

    def _navigate_to(item_id: str, module_id: str):
        """跳转到指定条目页面并关闭弹窗。

        Args:
            item_id: 条目 ID。
            module_id: 模块 ID。
        """
        ft.context.page.navigate(f"/{module_id}/{item_id}")
        on_close()

    def _build_result(item) -> ft.Container:
        """构建单个搜索结果条目。

        Args:
            item: 条目数据对象。

        Returns:
            搜索结果容器。
        """
        return ft.Container(
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            on_click=lambda _, i=item: _navigate_to(i.id, i.module_id),
            content=ft.Row(
                [
                    avatar_circle(item.name, item.color, 36),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        item.name,
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color=theme.C_TEXT,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        expand=True,
                                    ),
                                    ft.Text(
                                        module_labels.get(item.module_id, ""),
                                        size=11,
                                        color=theme.C_TEXT_SEC,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                item.preview,
                                size=12,
                                color=theme.C_TEXT_SEC,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
        )

    result_controls = [_build_result(item) for item in results]

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
                    # 搜索输入框
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                        border=ft.Border.only(
                            bottom=ft.BorderSide(1, theme.C_BORDER)
                        ),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.SEARCH,
                                    size=22,
                                    color=theme.C_TEXT_SEC,
                                ),
                                ft.TextField(
                                    value=query,
                                    hint_text="搜索条目…",
                                    border=ft.NoInputBorder(),
                                    autofocus=True,
                                    expand=True,
                                    on_change=lambda e: set_query(
                                        e.control.value
                                    ),
                                ),
                                ft.Text(
                                    "Esc",
                                    size=12,
                                    color=theme.C_TEXT_SEC,
                                ),
                            ],
                            spacing=12,
                        ),
                    ),
                    # 搜索结果列表
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        content=ft.ListView(
                            result_controls,
                            spacing=2,
                            expand=True,
                        )
                        if result_controls
                        else ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                "无搜索结果" if query.strip() else "开始输入以搜索",
                                size=14,
                                color=theme.C_TEXT_SEC,
                            ),
                        ),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        ),
        on_dismiss=lambda _: on_close(),
    )

    ft.use_dialog(dialog if show else None)
    return ft.Container()
