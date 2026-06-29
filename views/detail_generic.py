"""通用详情页组件模块。

用于显示通讯录、邮箱等模块的详情内容，支持可滚动的文本展示。
"""

import flet as ft

from components.detail_panel import detail_panel
from services.repository import get_item
import theme


@ft.component
def GenericDetail():
    """通用详情页组件。

    从路由参数获取条目 ID，显示条目的详细内容。
    优先使用 detail_body 字段，无内容时降级为 preview 字段。

    Returns:
        通用详情面板。
    """
    params = ft.use_route_params()
    item = get_item(params.get("item_id", ""))

    # 条目不存在时返回空容器
    if not item:
        return ft.Container(expand=True)

    # 详情内容区
    detail_body = ft.Container(
        expand=True,
        padding=24,
        content=ft.Column(
            [
                ft.Text(
                    item.detail_body or item.preview,
                    size=14,
                    color=theme.C_TEXT,
                    selectable=True,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    return detail_panel(item, item.subtitle, detail_body)
