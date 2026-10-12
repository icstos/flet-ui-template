"""通用详情页（通讯录 / 邮箱）：可滚动正文。"""

from __future__ import annotations

import flet as ft

from view.contexts import use_container
from view.hooks import use_view_model
from view.widgets.detail_panel import detail_panel, empty_detail_panel


@ft.component
def GenericDetail():
    """展示条目的详情正文，缺失时降级为预览文本。

    Returns:
        通用详情面板。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.generic_detail)

    params = ft.use_route_params()
    item_id = params.get("item_id", "")

    ft.use_effect(lambda: view_model.load(item_id), dependencies=[item_id])

    colors = theme.colors
    item = view_model.item
    if item is None:
        return empty_detail_panel(colors)

    body = ft.Container(
        expand=True,
        padding=24,
        content=ft.Column(
            [
                ft.Text(
                    view_model.body,
                    size=14,
                    color=colors.text,
                    selectable=True,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    return detail_panel(item, item.subtitle, body, colors)
