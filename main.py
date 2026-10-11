"""CSTOS 应用入口模块。

负责初始化配置、数据库，并启动 Flet 桌面应用。
"""

import flet as ft

from config import get_config, load_config
from database import init_db
from views.app import App


def setup_window(page: ft.Page) -> None:
    """应用启动前的初始化工作。

    加载配置文件、初始化数据库，并根据配置设置窗口属性。

    Args:
        page: Flet 页面对象。
    """
    load_config()
    init_db()

    cfg = get_config()
    win = cfg.window
    colors = cfg.colors

    page.title = win.title

    page.fonts = {
        "AlibabaPuHuiTi": "assets/fonts/AlibabaPuHuiTi-3-55-Regular.otf",
    }
    page.theme = ft.Theme(font_family="AlibabaPuHuiTi")

    page.window.width = win.width
    page.window.height = win.height
    page.window.min_width = win.min_width
    page.window.min_height = win.min_height
    page.window.bgcolor = colors.content_bg

    if win.frameless:
        page.window.frameless = True
        page.window.title_bar_hidden = True


@ft.component
def RootView():
    """应用根视图。

    Flet 1.x 起 ``page.padding`` / ``page.spacing`` / ``page.bgcolor``
    已不再是 Page 的属性，直接赋值不报错但也不生效，
    因此页面级背景色改由这一层 Container 承载。

    Returns:
        应用根容器。
    """
    colors = get_config().colors

    return ft.Container(
        content=App(),
        expand=True,
        bgcolor=colors.content_bg,
        padding=0,
    )


def build_app(page: ft.Page) -> None:
    """渲染应用根视图。

    注意：``@ft.component`` 组件不能在普通函数里直接调用 —— 必须经由
    ``page.render(...)``，它会建立 Renderer 渲染上下文；否则会抛
    ``RuntimeError: No current renderer is set``。
    ``page.render`` 接受的是组件函数本身，而不是已实例化的控件。

    Args:
        page: Flet 页面对象。
    """
    page.render(RootView)


if __name__ == "__main__":
    ft.run(build_app, before_main=setup_window)
