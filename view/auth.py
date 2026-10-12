"""认证视图：登录、注册、修改密码。

视图只做两件事：把状态渲染成控件、把交互转成视图模型调用。
表单校验与业务判定全部位于视图模型与业务服务。
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from models import ColorSettings
from view.contexts import use_container
from view.hooks import use_view_model

_CARD_WIDTH = 400
_INPUT_WIDTH = 320
_ERROR_COLOR = "#e74c3c"
_SUCCESS_COLOR = "#50c878"


def _auth_input(
    label: str,
    value: str,
    on_change: Callable[[ft.ControlEvent], None],
    *,
    password: bool = False,
    colors: ColorSettings,
) -> ft.TextField:
    """构建认证表单输入框。"""
    return ft.TextField(
        label=label,
        value=value,
        password=password,
        can_reveal_password=password,
        width=_INPUT_WIDTH,
        border_color=colors.border,
        focused_border_color=colors.accent,
        bgcolor=colors.input_bg,
        on_change=on_change,
    )


def _auth_card(content_controls: list[ft.Control], colors: ColorSettings) -> ft.Container:
    """构建居中卡片布局。"""
    return ft.Container(
        expand=True,
        bgcolor=colors.content_bg,
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=_CARD_WIDTH,
            padding=40,
            border_radius=12,
            bgcolor=colors.list_bg,
            border=ft.Border.all(1, colors.border),
            content=ft.Column(
                content_controls,
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
    )


@ft.component
def LoginView():
    """登录页。

    Returns:
        登录卡片。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.login)
    colors = theme.colors

    def submit(_: ft.ControlEvent) -> None:
        target = view_model.submit()
        if target:
            ft.context.page.navigate(target)

    return _auth_card(
        [
            ft.Icon(ft.Icons.LOCK_OUTLINE, size=48, color=colors.accent),
            ft.Text(
                "CSTOS 登录",
                size=24,
                weight=ft.FontWeight.W_700,
                color=colors.text,
            ),
            _auth_input(
                "用户名",
                view_model.username,
                lambda event: view_model.set_username(event.control.value or ""),
                colors=colors,
            ),
            _auth_input(
                "密码",
                view_model.password,
                lambda event: view_model.set_password(event.control.value or ""),
                password=True,
                colors=colors,
            ),
            _error_text(view_model.error),
            ft.Button(
                "登录",
                on_click=submit,
                width=_INPUT_WIDTH,
                height=42,
                bgcolor=colors.accent,
                color="#ffffff",
            ),
            ft.Row(
                [
                    ft.Text("还没有账号？", size=13, color=colors.text_sec),
                    ft.TextButton(
                        "注册",
                        on_click=lambda _: ft.context.page.navigate("/register"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        colors,
    )


@ft.component
def RegisterView():
    """注册页。

    Returns:
        注册卡片。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.register)
    colors = theme.colors

    def submit(_: ft.ControlEvent) -> None:
        target = view_model.submit()
        if target:
            ft.context.page.navigate(target)

    return _auth_card(
        [
            ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=48, color=colors.accent),
            ft.Text(
                "注册账号",
                size=24,
                weight=ft.FontWeight.W_700,
                color=colors.text,
            ),
            _auth_input(
                "用户名",
                view_model.username,
                lambda event: view_model.set_username(event.control.value or ""),
                colors=colors,
            ),
            _auth_input(
                "密码",
                view_model.password,
                lambda event: view_model.set_password(event.control.value or ""),
                password=True,
                colors=colors,
            ),
            _auth_input(
                "确认密码",
                view_model.confirm,
                lambda event: view_model.set_confirm(event.control.value or ""),
                password=True,
                colors=colors,
            ),
            _error_text(view_model.error),
            ft.Button(
                "注册",
                on_click=submit,
                width=_INPUT_WIDTH,
                height=42,
                bgcolor=colors.accent,
                color="#ffffff",
            ),
            ft.Row(
                [
                    ft.Text("已有账号？", size=13, color=colors.text_sec),
                    ft.TextButton(
                        "登录",
                        on_click=lambda _: ft.context.page.navigate("/login"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        colors,
    )


@ft.component
def ChangePasswordView():
    """修改密码表单（嵌入设置页）。

    Returns:
        表单列。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.change_password)
    colors = theme.colors

    def submit(_: ft.ControlEvent) -> None:
        view_model.submit()

    return ft.Column(
        [
            ft.Text(
                "修改密码",
                weight=ft.FontWeight.W_600,
                color=colors.text,
            ),
            _auth_input(
                "旧密码",
                view_model.old_password,
                lambda event: view_model.set_old_password(event.control.value or ""),
                password=True,
                colors=colors,
            ),
            _auth_input(
                "新密码",
                view_model.new_password,
                lambda event: view_model.set_new_password(event.control.value or ""),
                password=True,
                colors=colors,
            ),
            _auth_input(
                "确认新密码",
                view_model.confirm,
                lambda event: view_model.set_confirm(event.control.value or ""),
                password=True,
                colors=colors,
            ),
            _error_text(view_model.error),
            _success_text(view_model.message),
            ft.Button(
                "确认修改",
                on_click=submit,
                bgcolor=colors.accent,
                color="#ffffff",
            ),
        ],
        spacing=12,
    )


def _error_text(message: str) -> ft.Control:
    """错误提示；无内容时用零高占位，保持布局稳定。"""
    if not message:
        return ft.Container(height=0)
    return ft.Text(message, size=13, color=_ERROR_COLOR)


def _success_text(message: str) -> ft.Control:
    """成功提示；无内容时用零高占位。"""
    if not message:
        return ft.Container(height=0)
    return ft.Text(message, size=13, color=_SUCCESS_COLOR)
