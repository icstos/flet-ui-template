"""圆形头像控件。

纯展示组件：不读取任何状态，全部输入经由参数传入。
"""

from __future__ import annotations

import flet as ft


def avatar_circle(name: str, color: str, size: int = 40) -> ft.Container:
    """构建圆形文字头像。

    Args:
        name: 名称，取首字作为头像文字。
        color: 头像底色。
        size: 头像边长。

    Returns:
        圆形头像容器。
    """
    initial = name[0] if name else "?"
    return ft.Container(
        width=size,
        height=size,
        border_radius=size // 2,
        bgcolor=color,
        alignment=ft.Alignment.CENTER,
        content=ft.Text(
            initial,
            size=size // 2.2,
            weight=ft.FontWeight.W_600,
            color="#ffffff",
        ),
    )
