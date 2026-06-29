"""工作区布局模块。

提供列表-详情式的双栏布局，用于聊天、通讯录、邮箱等模块。
"""

import flet as ft

from views.list_panel import ListPanel


@ft.component
def WorkspaceLayout():
    """工作区布局组件。

    水平布局：
    - 左侧：列表面板（ListPanel），可拖动调整宽度
    - 右侧：详情内容区（路由出口）

    Returns:
        工作区布局容器。
    """
    outlet = ft.use_route_outlet()
    return ft.Row(
        [ListPanel(), ft.Container(content=outlet, expand=True)],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
