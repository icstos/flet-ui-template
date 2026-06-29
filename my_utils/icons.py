"""图标工具模块。

提供图标名称到 Flet 图标常量的映射，支持动态获取图标。
"""

import flet as ft


def icon(name: str) -> str:
    """根据图标名称获取 Flet 图标常量。

    如果名称不存在，返回默认的帮助图标。

    Args:
        name: 图标名称（对应 ft.Icons 的属性名）。

    Returns:
        Flet 图标常量值。
    """
    return getattr(ft.Icons, name, ft.Icons.HELP_OUTLINE)
