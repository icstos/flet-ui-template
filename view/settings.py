"""设置页：主题配色自定义 + 账号操作。"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from models import ColorSettings
from view.auth import ChangePasswordView
from view.contexts import use_container
from view.hooks import use_view_model
from viewmodel import SettingsViewModel

_SWATCH_SIZE = 28


def _color_preview_box(value: str) -> ft.Container:
    """颜色预览小方块。"""
    return ft.Container(
        width=_SWATCH_SIZE,
        height=_SWATCH_SIZE,
        border_radius=4,
        bgcolor=value,
        border=ft.Border.all(1, "#ddd"),
    )


def _color_input_row(
    label: str,
    value: str,
    on_change: Callable[[ft.ControlEvent], None],
    colors: ColorSettings,
) -> ft.Row:
    """一行「标签 + 输入框 + 预览」。"""
    return ft.Row(
        [
            ft.Text(label, width=80, color=colors.text),
            ft.TextField(value=value, width=160, on_change=on_change),
            _color_preview_box(value),
        ],
        spacing=8,
    )


@ft.component
def SettingsView():
    """设置页。

    Returns:
        设置页容器。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.settings)
    colors = theme.colors

    def navigate(route: str) -> None:
        ft.context.page.navigate(route)

    def go_back(_: ft.ControlEvent) -> None:
        navigate(view_model.back_route)

    def logout(_: ft.ControlEvent) -> None:
        target = view_model.logout()
        if target:
            navigate(target)

    def preset_swatch(value: str) -> ft.Container:
        """常用颜色预设圆点。"""
        return ft.Container(
            width=_SWATCH_SIZE,
            height=_SWATCH_SIZE,
            border_radius=_SWATCH_SIZE // 2,
            bgcolor=value,
            on_click=lambda _, color=value: view_model.set_accent(color),
        )

    return ft.Container(
        expand=True,
        bgcolor=colors.content_bg,
        padding=32,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            icon_size=20,
                            on_click=go_back,
                        ),
                        ft.Text(
                            "设置",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=colors.text,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Text("应用偏好与账号管理", size=14, color=colors.text_sec),
                ft.Divider(),
                ChangePasswordView(),
                ft.Divider(),
                ft.Text("账号操作", weight=ft.FontWeight.W_600, color=colors.text),
                ft.Button(
                    "退出登录",
                    on_click=logout,
                    bgcolor="#e74c3c",
                    color="#ffffff",
                ),
                ft.Divider(),
                ft.Text("主题色", weight=ft.FontWeight.W_600, color=colors.text),
                ft.Row(
                    [
                        ft.Column(
                            [
                                _color_input_row(
                                    "主颜色",
                                    view_model.accent,
                                    lambda event: view_model.set_accent(
                                        event.control.value or ""
                                    ),
                                    colors,
                                ),
                                _color_input_row(
                                    "侧栏色",
                                    view_model.sidebar,
                                    lambda event: view_model.set_sidebar(
                                        event.control.value or ""
                                    ),
                                    colors,
                                ),
                                _color_input_row(
                                    "内容背景",
                                    view_model.content_bg,
                                    lambda event: view_model.set_content_bg(
                                        event.control.value or ""
                                    ),
                                    colors,
                                ),
                                _color_input_row(
                                    "文字色",
                                    view_model.text_color,
                                    lambda event: view_model.set_text_color(
                                        event.control.value or ""
                                    ),
                                    colors,
                                ),
                            ]
                        ),
                        ft.Container(width=24),
                        ft.Column(
                            [
                                ft.Text("常用颜色", color=colors.text),
                                ft.Row(
                                    [
                                        preset_swatch(value)
                                        for value in view_model.presets
                                    ],
                                    spacing=6,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=24,
                ),
                ft.Row(
                    [
                        ft.Button(
                            "保存",
                            on_click=lambda _: view_model.apply_and_save(),
                            bgcolor=colors.accent,
                            color="#ffffff",
                        ),
                        ft.TextButton(
                            "恢复为默认",
                            on_click=lambda _: view_model.restore_defaults(),
                        ),
                    ],
                    spacing=12,
                ),
            ],
            spacing=16,
        ),
    )


__all__ = ["SettingsView", "SettingsViewModel"]
