"""CSTOS 应用入口。

职责仅有两项：
    1. 通过组合根装配依赖（:func:`container.build_container`）；
    2. 把根视图交付给 Flet 运行时。

界面完全由状态派生，因此 ``build_app`` 只需一行 ``page.render``。
"""

from __future__ import annotations

import flet as ft

from container import AppContainer, build_container
from models import FONT_ASSET_PATH, FONT_FAMILY, WindowSettings
from view.app import RootWithContainer


def apply_window_settings(
    page: ft.Page, window: WindowSettings, content_bg: str
) -> None:
    """把窗口配置应用到页面。

    Flet 1.x 中 ``page.padding`` / ``page.spacing`` / ``page.bgcolor``
    已不是 ``Page`` 的属性，直接赋值不会报错但也不会生效；
    页面背景由根视图的容器承载，窗口背景则由 ``window.bgcolor`` 承担。

    Args:
        page: Flet 页面。
        window: 窗口配置。
        content_bg: 内容区背景色（同时作为窗口底色，避免拖动时露白）。
    """
    page.title = window.title
    page.fonts = {FONT_FAMILY: FONT_ASSET_PATH}
    page.theme = ft.Theme(font_family=FONT_FAMILY)
    page.padding = ft.Padding.all(0)
    page.window.width = window.width
    page.window.height = window.height
    page.window.min_width = window.min_width
    page.window.min_height = window.min_height
    page.window.bgcolor = content_bg

    if window.frameless:
        page.window.frameless = True
        page.window.title_bar_hidden = True


def main() -> None:
    """启动应用。"""
    container: AppContainer = build_container()

    def setup_window(page: ft.Page) -> None:
        apply_window_settings(
            page,
            container.settings_service.window(),
            container.settings_service.colors().content_bg,
        )

    def build_app(page: ft.Page) -> None:
        # @ft.component 组件不能直接调用：page.render 会建立渲染上下文；
        # 且它接收的是组件函数本身，而非已实例化的控件。
        page.render(RootWithContainer, container)

    ft.run(build_app, before_main=setup_window)


if __name__ == "__main__":
    main()
