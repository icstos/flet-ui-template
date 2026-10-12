"""详情面板骨架。

头部（头像 + 标题 / 副标题 + 操作按钮）+ 内容主体。
纯展示组件：配色由调用方传入，不自行读取状态。
"""

from __future__ import annotations

from typing import Any

import flet as ft

from models import ColorSettings, Item
from view.widgets.avatar import avatar_circle

HEADER_HEIGHT = 56
"""头部栏高度。"""


def detail_panel(
    item: Item,
    subtitle: str,
    body: Any,
    colors: ColorSettings,
) -> ft.Container:
    """构建详情面板。

    Args:
        item: 条目数据。
        subtitle: 副标题文本。
        body: 内容主体控件。
        colors: 当前配色。

    Returns:
        详情面板容器。
    """
    header = ft.Container(
        height=HEADER_HEIGHT,
        bgcolor="#ffffff",
        border=ft.Border.only(bottom=ft.BorderSide(1, colors.border)),
        padding=ft.Padding.symmetric(horizontal=20),
        content=ft.Row(
            [
                avatar_circle(item.name, item.color, 36),
                ft.Column(
                    [
                        ft.Text(
                            item.name,
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=colors.text,
                        ),
                        ft.Text(subtitle, size=12, color=colors.text_sec),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    ft.Icons.VIDEOCAM_OUTLINED,
                    icon_size=20,
                    icon_color=colors.text_sec,
                ),
                ft.IconButton(
                    ft.Icons.MORE_VERT, icon_size=20, icon_color=colors.text_sec
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return ft.Container(
        expand=True,
        bgcolor=colors.content_bg,
        content=ft.Column([header, body], expand=True, spacing=0),
    )


def empty_detail_panel(colors: ColorSettings) -> ft.Container:
    """条目不存在时的占位面板。

    Args:
        colors: 当前配色。

    Returns:
        空白容器。
    """
    return ft.Container(expand=True, bgcolor=colors.content_bg)


__all__ = ["HEADER_HEIGHT", "detail_panel", "empty_detail_panel"]
