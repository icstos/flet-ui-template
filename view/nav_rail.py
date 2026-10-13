"""侧边导航栏。

导航栏是一条「窄图标轨」。尺寸全部集中在 :data:`RAIL_*` 常量中调整，
保持按钮/图标/头像三者的比例协调——收窄栏宽时它们一起等比收缩，
而不是单独把栏宽改小、留下过大的控件。
"""

from __future__ import annotations

import flet as ft

from models import SETTINGS_ROUTE
from view.contexts import use_container
from view.hooks import use_view_model
from view.icons import resolve_icon
from view.widgets.avatar import avatar_circle

RAIL_PADDING_V = 10
"""垂直内边距。

注意：Flet 1.x 中 ``Container.width`` 指的是**内容宽度**，水平 padding 会在
其之外再撑大占位（例如 width=54 + 左右各 5 实际占 64）。因此这里不设水平
padding，左右留白改由 Column 的居中对齐自然形成。
"""

RAIL_BUTTON_SIZE = 44
"""模块按钮边长（桌面端 44 仍是舒适的点击目标）。"""

RAIL_BUTTON_RADIUS = 10
RAIL_ICON_SIZE = 22
AVATAR_SIZE = 32
SETTINGS_BUTTON_SIZE = 36
SETTINGS_BUTTON_RADIUS = 9
SETTINGS_ICON_SIZE = 20
BUTTON_SPACING = 4
"""模块按钮之间的间距。"""

BOTTOM_SPACING = 8
"""头像与设置按钮之间的间距。"""


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

    def build_module_button(module) -> ft.Container:
        """构建单个模块按钮，选中态用实心图标 + 强调色。"""
        is_active = view_model.is_module_active(module.id, location)
        return ft.Container(
            width=RAIL_BUTTON_SIZE,
            height=RAIL_BUTTON_SIZE,
            border_radius=RAIL_BUTTON_RADIUS,
            bgcolor=colors.sidebar_active if is_active else None,
            alignment=ft.Alignment.CENTER,
            ink=True,
            tooltip=module.label,
            on_click=nav_to(module.id),
            content=ft.Icon(
                resolve_icon(module.icon_filled if is_active else module.icon),
                size=RAIL_ICON_SIZE,
                color=colors.accent if is_active else colors.icon_inactive,
            ),
        )

    session = view_model.session
    avatar_color = session.avatar_color if session else colors.accent

    return ft.Container(
        width=theme.layout.nav_width,
        bgcolor=colors.sidebar,
        padding=ft.Padding.only(top=RAIL_PADDING_V, bottom=RAIL_PADDING_V),
        content=ft.Column(
            [
                ft.Column(
                    [build_module_button(module) for module in view_model.modules],
                    spacing=BUTTON_SPACING,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                ft.Container(
                    padding=ft.Padding.only(bottom=6),
                    content=ft.Column(
                        [
                            avatar_circle(
                                view_model.display_name[:1] or "我",
                                avatar_color,
                                AVATAR_SIZE,
                            ),
                            ft.Container(
                                width=SETTINGS_BUTTON_SIZE,
                                height=SETTINGS_BUTTON_SIZE,
                                border_radius=SETTINGS_BUTTON_RADIUS,
                                alignment=ft.Alignment.CENTER,
                                ink=True,
                                tooltip="设置",
                                on_click=open_settings,
                                content=ft.Icon(
                                    ft.Icons.SETTINGS_OUTLINED,
                                    size=SETTINGS_ICON_SIZE,
                                    color=colors.icon_inactive,
                                ),
                            ),
                        ],
                        spacing=BOTTOM_SPACING,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ],
            expand=True,
            # 关键：外层 Column 必须显式居中，否则其子列（按钮列、底部列）
            # 会按各自内容宽度左对齐，导致整组控件贴左缘而非栏内居中。
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
