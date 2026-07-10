"""用户认证视图模块。

提供登录、注册、修改密码三个页面组件。
登录和注册页面为全屏居中卡片布局，不包含侧边栏和标题栏。
修改密码页面嵌入设置页面中。
"""

import flet as ft

from my_utils.auth_storage import clear_auth, load_auth, save_auth
from services.repository import (
    authenticate,
    change_password,
    get_default_item_id,
    register_user,
)
import theme


def _auth_input(
    label: str,
    password: bool = False,
    value: str = "",
    on_change=None,
) -> ft.TextField:
    """构建认证表单输入框。

    Args:
        label: 输入框标签。
        password: 是否为密码输入框。
        value: 初始值。
        on_change: 值变化回调。

    Returns:
        TextField 组件。
    """
    return ft.TextField(
        label=label,
        value=value,
        password=password,
        can_reveal_password=password,
        width=320,
        border_color=theme.C_BORDER,
        focused_border_color=theme.C_ACCENT,
        bgcolor=theme.C_INPUT_BG,
    )


def _auth_card(content_controls: list) -> ft.Container:
    """构建认证页面居中卡片容器。

    Args:
        content_controls: 卡片内容控件列表。

    Returns:
        居中卡片容器。
    """
    return ft.Container(
        expand=True,
        bgcolor=theme.C_CONTENT_BG,
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=400,
            padding=40,
            border_radius=12,
            bgcolor=theme.C_LIST_BG,
            border=ft.Border.all(1, theme.C_BORDER),
            content=ft.Column(
                content_controls,
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
    )


@ft.component
def LoginView():
    """登录页面组件。

    提供用户名和密码输入，登录成功后跳转到主页面。
    底部提供注册页面链接。
    """
    error, set_error = ft.use_state("")

    def do_login(_):
        username = username_field.value or ""
        password = password_field.value or ""
        user = authenticate(username, password)
        if not user:
            set_error("用户名或密码错误")
            return
        save_auth(user.id, user.username, user.avatar_color)
        default = get_default_item_id("chat")
        ft.context.page.navigate(f"/chat/{default}")

    username_field = _auth_input("用户名")
    password_field = _auth_input("密码", password=True)

    return _auth_card(
        [
            ft.Icon(ft.Icons.LOCK_OUTLINE, size=48, color=theme.C_ACCENT),
            ft.Text(
                "CSTOS 登录",
                size=24,
                weight=ft.FontWeight.W_700,
                color=theme.C_TEXT,
            ),
            username_field,
            password_field,
            ft.Text(error, size=13, color="#e74c3c") if error else ft.Container(height=0),
            ft.ElevatedButton(
                "登录",
                on_click=do_login,
                width=320,
                height=42,
                bgcolor=theme.C_ACCENT,
                color="#ffffff",
            ),
            ft.Row(
                [
                    ft.Text("还没有账号？", size=13, color=theme.C_TEXT_SEC),
                    ft.TextButton(
                        "注册",
                        on_click=lambda _: ft.context.page.navigate("/register"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )


@ft.component
def RegisterView():
    """注册页面组件。

    提供用户名、密码、确认密码输入，注册成功后自动登录并跳转。
    底部提供登录页面链接。
    """
    error, set_error = ft.use_state("")

    def do_register(_):
        username = (username_field.value or "").strip()
        password = password_field.value or ""
        confirm = confirm_field.value or ""

        if not username or not password:
            set_error("用户名和密码不能为空")
            return
        if password != confirm:
            set_error("两次输入的密码不一致")
            return

        user = register_user(username, password)
        if not user:
            set_error("用户名已存在")
            return

        save_auth(user.id, user.username, user.avatar_color)
        default = get_default_item_id("chat")
        ft.context.page.navigate(f"/chat/{default}")

    username_field = _auth_input("用户名")
    password_field = _auth_input("密码", password=True)
    confirm_field = _auth_input("确认密码", password=True)

    return _auth_card(
        [
            ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=48, color=theme.C_ACCENT),
            ft.Text(
                "注册账号",
                size=24,
                weight=ft.FontWeight.W_700,
                color=theme.C_TEXT,
            ),
            username_field,
            password_field,
            confirm_field,
            ft.Text(error, size=13, color="#e74c3c") if error else ft.Container(height=0),
            ft.ElevatedButton(
                "注册",
                on_click=do_register,
                width=320,
                height=42,
                bgcolor=theme.C_ACCENT,
                color="#ffffff",
            ),
            ft.Row(
                [
                    ft.Text("已有账号？", size=13, color=theme.C_TEXT_SEC),
                    ft.TextButton(
                        "登录",
                        on_click=lambda _: ft.context.page.navigate("/login"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]
    )


@ft.component
def ChangePasswordView():
    """修改密码页面组件。

    嵌入设置页面中，提供旧密码、新密码、确认新密码输入。
    """
    error, set_error = ft.use_state("")
    success, set_success = ft.use_state("")

    def do_change(_):
        old = old_field.value or ""
        new = new_field.value or ""
        confirm = confirm_field.value or ""

        if not old or not new:
            set_error("密码不能为空")
            set_success("")
            return
        if new != confirm:
            set_error("两次输入的新密码不一致")
            set_success("")
            return

        auth = load_auth()
        user_id = auth["user_id"] if auth else None
        if not user_id:
            set_error("请先登录")
            set_success("")
            return

        if change_password(user_id, old, new):
            set_success("密码修改成功")
            set_error("")
            old_field.value = ""
            new_field.value = ""
            confirm_field.value = ""
            ft.context.page.update()
        else:
            set_error("旧密码错误")
            set_success("")

    old_field = _auth_input("旧密码", password=True)
    new_field = _auth_input("新密码", password=True)
    confirm_field = _auth_input("确认新密码", password=True)

    return ft.Column(
        [
            ft.Text(
                "修改密码",
                weight=ft.FontWeight.W_600,
                color=theme.C_TEXT,
            ),
            old_field,
            new_field,
            confirm_field,
            ft.Text(error, size=13, color="#e74c3c") if error else ft.Container(height=0),
            ft.Text(success, size=13, color="#50c878") if success else ft.Container(height=0),
            ft.ElevatedButton(
                "确认修改",
                on_click=do_change,
                bgcolor=theme.C_ACCENT,
                color="#ffffff",
            ),
        ],
        spacing=12,
    )
