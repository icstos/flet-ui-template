"""工作区布局：列表面板 + 详情出口。"""

from __future__ import annotations

import flet as ft

from view.list_panel import ListPanel


@ft.component
def WorkspaceLayout():
    """左列表 / 右详情的双栏布局。

    Returns:
        工作区容器。
    """
    outlet = ft.use_route_outlet()
    return ft.Row(
        [
            ListPanel(),
            ft.Container(content=outlet, expand=True),
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
