"""详情面板组件模块。

提供带头部的详情页布局，包括头像、标题、操作按钮和内容区。
"""

import flet as ft

from components.avatar import avatar_circle
from models import Item
import theme


def detail_panel(item: Item, subtitle: str, body) -> ft.Container:
    """构建详情面板。

    垂直布局：
    - 顶部：头部栏（头像 + 标题/副标题 + 操作按钮）
    - 下部：内容主体

    Args:
        item: 条目数据对象。
        subtitle: 副标题文本。
        body: 内容主体组件。

    Returns:
        详情面板容器。
    """
    # 头部栏
    header = ft.Container(
        height=56,
        bgcolor="#ffffff",
        border=ft.Border.only(bottom=ft.BorderSide(1, theme.C_BORDER)),
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
                            color=theme.C_TEXT,
                        ),
                        ft.Text(subtitle, size=12, color=theme.C_TEXT_SEC),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    ft.Icons.VIDEOCAM_OUTLINED,
                    icon_size=20,
                    icon_color=theme.C_TEXT_SEC,
                ),
                ft.IconButton(
                    ft.Icons.MORE_VERT, icon_size=20, icon_color=theme.C_TEXT_SEC
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return ft.Container(
        expand=True,
        bgcolor=theme.C_CONTENT_BG,
        content=ft.Column([header, body], expand=True, spacing=0),
    )
