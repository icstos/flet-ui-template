"""图标名到 Flet 图标常量的解析。

数据库中的模块以字符串保存图标名（如 ``CHAT_BUBBLE_OUTLINE``），
在此集中转换为 Flet 常量；名称不存在时回退为帮助图标。
"""

from __future__ import annotations

import flet as ft

_FALLBACK = ft.Icons.HELP_OUTLINE


def resolve_icon(name: str) -> ft.IconData:
    """把图标名解析为 Flet 图标常量。

    Args:
        name: :class:`flet.Icons` 的属性名。

    Returns:
        对应的图标常量；未知名返回回退图标。
    """
    return getattr(ft.Icons, name, _FALLBACK)
