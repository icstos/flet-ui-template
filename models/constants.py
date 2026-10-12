"""领域常量。

集中存放跨层共享的固定取值，避免在各层重复书写字面量。
"""

from __future__ import annotations

COLOR_PRESETS: tuple[str, ...] = (
    "#3b7cff",  # 蓝
    "#50c878",  # 绿
    "#e6a23c",  # 橙
    "#9b59b6",  # 紫
    "#e74c3c",  # 红
    "#4a90d9",  # 天蓝
)
"""设置页「常用颜色」预设。"""

SETTINGS_ROUTE = "/settings"
"""设置页路由。"""

LOGIN_ROUTE = "/login"
REGISTER_ROUTE = "/register"
ROOT_ROUTE = "/"
"""认证与根路由。"""

FONT_FAMILY = "AlibabaPuHuiTi"
"""全局字族名（需与字体注册键一致）。"""

FONT_ASSET_PATH = "assets/fonts/AlibabaPuHuiTi-3-55-Regular.otf"
"""字体资源路径。"""
