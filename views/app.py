"""应用路由配置模块。

定义整个应用的路由结构，包括：
- 根路径重定向
- 设置页面
- 聊天、通讯录、邮箱等工作区页面
"""

import flet as ft

from services.repository import get_default_item_id
from views.detail_chat import ChatDetail
from views.detail_generic import GenericDetail
from views.settings import SettingsView
from views.shell import ShellLayout
from views.workspace import WorkspaceLayout


@ft.component
def IndexRedirect():
    """根路径重定向组件。

    将访问根路径的用户自动跳转到默认聊天会话页面。
    """
    default = get_default_item_id("chat")
    ft.context.page.navigate(f"/chat/{default}")
    return ft.Container()


@ft.component
def App():
    """应用根组件。

    配置完整的路由树：
    - ShellLayout 作为外层布局（标题栏 + 导航栏）
    - 各功能模块使用 WorkspaceLayout（列表 + 详情）
    - 未匹配路由统一重定向到默认页面
    """
    return ft.Router(
        [
            ft.Route(
                component=ShellLayout,
                children=[
                    # 根路径重定向
                    ft.Route(index=True, component=IndexRedirect),
                    # 设置页面
                    ft.Route(path="settings", component=SettingsView),
                    # 聊天模块
                    ft.Route(
                        path="chat",
                        component=WorkspaceLayout,
                        children=[ft.Route(path=":item_id", component=ChatDetail)],
                    ),
                    # 通讯录模块
                    ft.Route(
                        path="contacts",
                        component=WorkspaceLayout,
                        children=[ft.Route(path=":item_id", component=GenericDetail)],
                    ),
                    # 邮箱模块
                    ft.Route(
                        path="email",
                        component=WorkspaceLayout,
                        children=[ft.Route(path=":item_id", component=GenericDetail)],
                    ),
                ],
            ),
        ],
        not_found=IndexRedirect,
    )
