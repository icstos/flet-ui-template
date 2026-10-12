"""全局搜索弹窗（Ctrl+Shift+F 唤起）。"""

from __future__ import annotations

import flet as ft

from models import Item
from view.contexts import use_container
from view.hooks import use_view_model
from view.widgets.avatar import avatar_circle

DIALOG_WIDTH = 560
DIALOG_HEIGHT = 420


@ft.component
def SearchOverlay():
    """跨模块搜索弹窗。

    显隐由 :class:`~viewmodel.search_overlay.SearchOverlayViewModel` 持有，
    快捷键处理位于外壳视图，这里只负责渲染与事件分发。

    Returns:
        占位容器（弹窗通过 ``use_dialog`` 挂载到页面浮层）。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.search_overlay)
    colors = theme.colors

    def navigate_to(item: Item) -> None:
        """跳转到选中条目并关闭弹窗。"""
        ft.context.page.navigate(f"/{item.module_id}/{item.id}")
        view_model.close()

    def build_result(item: Item) -> ft.Container:
        """构建单条搜索结果。"""
        return ft.Container(
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            on_click=lambda _, target=item: navigate_to(target),
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
                                        color=colors.text,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        expand=True,
                                    ),
                                    ft.Text(
                                        view_model.module_labels.get(
                                            item.module_id, ""
                                        ),
                                        size=11,
                                        color=colors.text_sec,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                item.preview,
                                size=12,
                                color=colors.text_sec,
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

    results = [build_result(item) for item in view_model.results]

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=colors.list_bg,
        barrier_color="#80000000",
        inset_padding=ft.Padding.only(top=80, left=200, right=200, bottom=80),
        content=ft.Container(
            width=DIALOG_WIDTH,
            height=DIALOG_HEIGHT,
            content=ft.Column(
                [
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                        border=ft.Border.only(bottom=ft.BorderSide(1, colors.border)),
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.SEARCH, size=22, color=colors.text_sec
                                ),
                                ft.TextField(
                                    value=view_model.query,
                                    hint_text="搜索条目…",
                                    border=ft.NoInputBorder(),
                                    autofocus=True,
                                    expand=True,
                                    on_change=lambda event: view_model.set_query(
                                        event.control.value
                                    ),
                                ),
                                ft.Text("Esc", size=12, color=colors.text_sec),
                            ],
                            spacing=12,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        content=(
                            ft.ListView(results, spacing=2, expand=True)
                            if results
                            else ft.Container(
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    (
                                        "无搜索结果"
                                        if view_model.query.strip()
                                        else "开始输入以搜索"
                                    ),
                                    size=14,
                                    color=colors.text_sec,
                                ),
                            )
                        ),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        ),
        on_dismiss=lambda _: view_model.close(),
    )

    ft.use_dialog(dialog if view_model.is_open else None)
    return ft.Container()
