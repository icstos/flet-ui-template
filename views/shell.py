"""应用外壳布局模块。

提供应用的最外层布局结构：标题栏 + 侧边导航栏 + 标签栏 + 内容区域。
同时注册全局快捷键 Ctrl+Shift+F 触发全局搜索弹窗。
标签页随路由变化自动同步，支持点击切换和关闭。
"""

import flet as ft

from components.title_bar import TitleBar
from my_utils.route import parse_workspace
from services.repository import get_default_item_id, get_item
from views.nav_rail import NavRail
from views.search_overlay import SearchOverlay
from views.tab_bar import Tab


@ft.component
def ShellLayout():
    """应用外壳布局组件。

    垂直布局：
    - 顶部：标题栏（TitleBar）
    - 下方：水平排列的侧边导航栏 + 内容区
    - 内容区内部：标签栏 + 路由内容

    通过 use_effect 注册全局键盘事件监听，
    检测 Ctrl+Shift+F 时打开全局搜索弹窗。
    通过 use_effect 监听路由变化自动同步标签页。

    Returns:
        外壳布局容器。
    """
    show_search, set_show_search = ft.use_state(False)
    tabs, set_tabs = ft.use_state([])
    location = ft.use_route_location()

    def check_auth():
        """检查登录状态，未登录时跳转到登录页。"""
        from my_utils.auth_storage import load_auth

        if not load_auth():
            ft.context.page.navigate("/login")

    ft.use_effect(check_auth, dependencies=[location])

    def setup_keyboard():
        """注册全局键盘快捷键监听。"""
        page = ft.context.page

        def on_keyboard(e: ft.KeyboardEvent):
            if e.ctrl and e.shift and e.key == "F":
                set_show_search(True)
            elif e.key == "Escape":
                set_show_search(False)

        page.on_keyboard_event = on_keyboard

        def cleanup():
            page.on_keyboard_event = None

        return cleanup

    ft.use_effect(setup_keyboard, dependencies=[])

    def sync_tabs():
        """路由变化时自动同步标签页。

        为当前路由创建标签（如果不存在），并标记为激活。
        根路径和无效路由不创建标签。
        """
        if not location or location == "/":
            return

        module_id, item_id = parse_workspace(location)

        # 设置页面
        if module_id == "settings":
            route = "/settings"
            title = "设置"
        elif not item_id:
            return  # 模块根路径（如 /chat），不创建标签
        else:
            route = f"/{module_id}/{item_id}"
            item = get_item(item_id)
            if not item:
                return
            title = item.name

        # 使用函数式更新避免闭包过时
        def updater(prev: list[Tab]) -> list[Tab]:
            if any(t.route == route for t in prev):
                return prev
            return prev + [
                Tab(route=route, title=title, module_id=module_id, item_id=item_id)
            ]

        set_tabs(updater)

    ft.use_effect(sync_tabs, dependencies=[location])

    def select_tab(route: str):
        """切换到指定标签页。"""
        ft.context.page.navigate(route)

    def close_tab(route: str):
        """关闭指定标签页。

        如果关闭的是当前激活标签，自动切换到相邻标签。
        """
        idx = next((i for i, t in enumerate(tabs) if t.route == route), -1)
        if idx < 0:
            return

        new_tabs = [t for t in tabs if t.route != route]
        set_tabs(new_tabs)

        # 如果关闭的是当前标签，导航到相邻标签
        if route == location:
            if new_tabs:
                new_idx = min(idx, len(new_tabs) - 1)
                ft.context.page.navigate(new_tabs[new_idx].route)
            else:
                default_id = get_default_item_id("chat")
                ft.context.page.navigate(f"/chat/{default_id}")

    outlet = ft.use_route_outlet()
    return ft.Column(
        [
            TitleBar(
                tabs=tabs,
                active_route=location,
                on_select=select_tab,
                on_close=close_tab,
            ),
            ft.Row(
                [NavRail(), ft.Container(content=outlet, expand=True)],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            SearchOverlay(show_search, lambda: set_show_search(False)),
        ],
        expand=True,
        spacing=0,
    )
