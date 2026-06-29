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
    page.padding = 0
    page.spacing = 0
    page.bgcolor = colors.content_bg

    page.window.width = win.width
    page.window.height = win.height
    page.window.min_width = win.min_width
    page.window.min_height = win.min_height
    page.window.bgcolor = colors.content_bg

    if win.frameless:
        page.window.frameless = True
        page.window.title_bar_hidden = True


if __name__ == "__main__":
    ft.run(lambda page: page.render(App), before_main=setup_window)
