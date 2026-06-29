"""应用外壳布局模块。

提供应用的最外层布局结构：标题栏 + 侧边导航栏 + 内容区域。
"""

import flet as ft

from components.title_bar import TitleBar
from views.nav_rail import NavRail


@ft.component
def ShellLayout():
    """应用外壳布局组件。

    垂直布局：
    - 顶部：标题栏（TitleBar）
    - 下方：水平排列的侧边导航栏 + 路由内容区

    Returns:
        外壳布局容器。
    """
    outlet = ft.use_route_outlet()
    return ft.Column(
        [
            TitleBar(),
            ft.Row(
                [NavRail(), ft.Container(content=outlet, expand=True)],
                expand=True,
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ],
        expand=True,
        spacing=0,
    )
