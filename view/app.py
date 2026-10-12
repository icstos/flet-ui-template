"""路由树与应用根视图。

路由结构：
    * ``/login``、``/register`` —— 独立全屏页（无外壳）；
    * 其余路由挂在外壳下：``/`` 重定向、``/settings`` 设置页，
      以及 ``chat`` / ``contacts`` / ``email`` 三个工作区；
    * 未匹配路由回落到根重定向。
"""

from __future__ import annotations

import flet as ft

from view.auth import LoginView, RegisterView
from view.contexts import provide_container, use_container
from view.detail_chat import ChatDetail
from view.detail_generic import GenericDetail
from view.hooks import use_view_model
from view.settings import SettingsView
from view.shell import ShellLayout
from view.workspace import WorkspaceLayout


@ft.component
def IndexRedirect():
    """根路径重定向到默认会话。

    未登录时不做跳转——登录守卫由外壳统一处理，避免两处跳转相互竞争。

    Returns:
        空容器。
    """
    shell = use_view_model(use_container().shell)

    def redirect() -> None:
        if not shell.is_authenticated:
            return
        ft.context.page.navigate(shell.default_route())

    ft.use_effect(redirect, dependencies=[])
    return ft.Container()


@ft.component
def App():
    """应用路由树。

    Returns:
        路由器控件。
    """
    return ft.Router(
        [
            ft.Route(path="login", component=LoginView),
            ft.Route(path="register", component=RegisterView),
            ft.Route(
                component=ShellLayout,
                children=[
                    ft.Route(index=True, component=IndexRedirect),
                    ft.Route(path="settings", component=SettingsView),
                    ft.Route(
                        path="chat",
                        component=WorkspaceLayout,
                        children=[ft.Route(path=":item_id", component=ChatDetail)],
                    ),
                    ft.Route(
                        path="contacts",
                        component=WorkspaceLayout,
                        children=[
                            ft.Route(path=":item_id", component=GenericDetail)
                        ],
                    ),
                    ft.Route(
                        path="email",
                        component=WorkspaceLayout,
                        children=[
                            ft.Route(path=":item_id", component=GenericDetail)
                        ],
                    ),
                ],
            ),
        ],
        not_found=IndexRedirect,
    )


@ft.component
def RootView():
    """应用根视图。

    Flet 1.x 中 ``page.bgcolor`` 已不属于 ``Page``，页面级背景改由此处承载。

    Returns:
        根容器。
    """
    theme = use_view_model(use_container().theme)
    return ft.Container(
        content=App(),
        expand=True,
        bgcolor=theme.colors.content_bg,
        padding=0,
    )


@ft.component
def RootWithContainer(container):
    """把应用容器注入组件树。

    Args:
        container: 组合根装配出的应用容器。

    Returns:
        根视图。
    """
    return provide_container(container, lambda: RootView())


__all__ = ["App", "IndexRedirect", "RootView", "RootWithContainer"]
