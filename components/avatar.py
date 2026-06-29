"""头像组件模块。

提供圆形头像组件，使用名称首字母作为头像内容。
"""

import flet as ft


def avatar_circle(name: str, color: str, size: int = 40) -> ft.Container:
    """创建圆形头像组件。

    使用名称的第一个字符作为头像文字，背景色为指定颜色。

    Args:
        name: 名称，取首字作为头像文字。
        color: 头像背景色。
        size: 头像尺寸，默认 40px。

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
            initial, size=size // 2.2, weight=ft.FontWeight.W_600, color="#ffffff"
        ),
    )
