"""侧边导航栏组件模块。

提供应用左侧的垂直导航栏，包含各功能模块入口和底部的用户头像、设置按钮。
"""

import flet as ft

from components.avatar import avatar_circle
from my_utils.icons import icon
from services.repository import get_modules
import theme


@ft.component
def NavRail():
    """侧边导航栏组件。

    垂直布局：
    - 顶部：各功能模块导航按钮
    - 底部：用户头像 + 设置按钮

    根据当前路由高亮对应的模块按钮。

    Returns:
        导航栏容器。
    """
    modules = get_modules()
    location = ft.use_route_location()

    def nav_to(module_id: str):
        """生成导航到指定模块的点击处理函数。

        Args:
            module_id: 目标模块 ID。

        Returns:
            点击事件处理函数。
        """

        def handler(_):
            ft.context.page.navigate(f"/{module_id}")

        return handler

    # 构建模块导航按钮列表
    nav_buttons = []
    for mod in modules:
        is_active = location.startswith(f"/{mod.id}")
        nav_buttons.append(
            ft.Container(
                width=52,
                height=52,
                border_radius=12,
                bgcolor=theme.C_SIDEBAR_ACTIVE if is_active else None,
                alignment=ft.Alignment.CENTER,
                ink=True,
                tooltip=mod.label,
                on_click=nav_to(mod.id),
                content=ft.Icon(
                    icon(mod.icon_filled if is_active else mod.icon),
                    size=24,
                    color=theme.C_ACCENT if is_active else theme.C_ICON_INACTIVE,
                ),
            )
        )

    return ft.Container(
        width=theme.NAV_WIDTH,
        bgcolor=theme.C_SIDEBAR,
        padding=ft.Padding.symmetric(vertical=12, horizontal=8),
        content=ft.Column(
            [
                # 顶部：功能模块按钮
                ft.Column(
                    nav_buttons,
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                # 弹性空白区域
                ft.Container(expand=True),
                # 底部：用户头像 + 设置
                ft.Container(
                    padding=ft.Padding.only(bottom=8),
                    content=ft.Column(
                        [
                            avatar_circle("我", theme.C_ACCENT, 36),
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=10,
                                alignment=ft.Alignment.CENTER,
                                ink=True,
                                tooltip="设置",
                                on_click=lambda _: ft.context.page.navigate(
                                    "/settings"
                                ),
                                content=ft.Icon(
                                    ft.Icons.SETTINGS_OUTLINED,
                                    size=22,
                                    color=theme.C_ICON_INACTIVE,
                                ),
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            expand=True,
        ),
    )
