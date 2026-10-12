"""侧边导航栏。"""

from __future__ import annotations

import flet as ft

from models import SETTINGS_ROUTE
from view.contexts import use_container
from view.hooks import use_view_model
from view.icons import resolve_icon
from view.widgets.avatar import avatar_circle


@ft.component
def NavRail():
    """左侧垂直导航栏：模块入口 + 用户头像 + 设置入口。

    Returns:
        导航栏容器。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.nav_rail)

    location = ft.use_route_location()

    # 登录 / 登出后刷新用户名与头像色
    ft.use_effect(lambda: view_model.refresh(), dependencies=[location])

    def nav_to(module_id: str):
        """生成导航到指定模块的点击处理函数。"""

        def handler(_: ft.ControlEvent) -> None:
            ft.context.page.navigate(f"/{module_id}")

        return handler

    def open_settings(_: ft.ControlEvent) -> None:
        """打开设置页。"""
        ft.context.page.navigate(SETTINGS_ROUTE)

    colors = theme.colors
    nav_buttons = [
        ft.Container(
            width=52,
            height=52,
            border_radius=12,
            bgcolor=(
                colors.sidebar_active
                if view_model.is_module_active(module.id, location)
                else None
            ),
            alignment=ft.Alignment.CENTER,
            ink=True,
            tooltip=module.label,
            on_click=nav_to(module.id),
            content=ft.Icon(
                resolve_icon(
                    module.icon_filled
                    if view_model.is_module_active(module.id, location)
                    else module.icon
                ),
                size=24,
                color=(
                    colors.accent
                    if view_model.is_module_active(module.id, location)
                    else colors.icon_inactive
                ),
            ),
        )
        for module in view_model.modules
    ]

    session = view_model.session
    avatar_color = session.avatar_color if session else colors.accent

    return ft.Container(
        width=theme.layout.nav_width,
        bgcolor=colors.sidebar,
        padding=ft.Padding.symmetric(vertical=12, horizontal=8),
        content=ft.Column(
            [
                ft.Column(
                    nav_buttons,
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.Padding.only(bottom=8),
                    content=ft.Column(
                        [
                            avatar_circle(
                                view_model.display_name[:1] or "我", avatar_color, 36
                            ),
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=10,
                                alignment=ft.Alignment.CENTER,
                                ink=True,
                                tooltip="设置",
                                on_click=open_settings,
                                content=ft.Icon(
                                    ft.Icons.SETTINGS_OUTLINED,
                                    size=22,
                                    color=colors.icon_inactive,
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
