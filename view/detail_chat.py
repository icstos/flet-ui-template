"""聊天详情页：消息气泡列表 + 输入工具栏。"""

from __future__ import annotations

import flet as ft

from models import ColorSettings, Message, MessageRole
from view.contexts import use_container
from view.hooks import use_view_model
from view.widgets.detail_panel import detail_panel, empty_detail_panel


def _build_message_bubbles(
    messages: tuple[Message, ...], colors: ColorSettings
) -> ft.Column:
    """构建消息气泡列表。

    己方消息右对齐、对方消息左对齐，气泡圆角方向随对齐方式变化。

    Args:
        messages: 消息集合。
        colors: 当前配色。

    Returns:
        可滚动的气泡列。
    """
    bubbles = []
    for message in messages:
        is_me = message.role == MessageRole.ME

        bubble = ft.Container(
            bgcolor=colors.accent if is_me else "#ffffff",
            border_radius=ft.BorderRadius.only(
                top_left=12,
                top_right=12,
                bottom_left=4 if is_me else 12,
                bottom_right=12 if is_me else 4,
            ),
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border=None if is_me else ft.Border.all(1, colors.border),
            content=ft.Text(
                message.text,
                size=14,
                color="#ffffff" if is_me else colors.text,
                selectable=True,
            ),
        )

        # 己方靠右（前置弹性空白），对方靠左（后置弹性空白）
        spacer = ft.Container(expand=True)
        children = [spacer, bubble] if is_me else [bubble, spacer]
        bubbles.append(ft.Row(children, spacing=0))

    return ft.Column(bubbles, spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)


@ft.component
def ChatDetail():
    """聊天会话详情。

    Returns:
        聊天详情面板。
    """
    container = use_container()
    theme = use_view_model(container.theme)
    view_model = use_view_model(container.chat_detail)

    params = ft.use_route_params()
    item_id = params.get("item_id", "")

    ft.use_effect(lambda: view_model.load(item_id), dependencies=[item_id])

    colors = theme.colors
    item = view_model.item
    if item is None:
        return empty_detail_panel(colors)

    body = ft.Column(
        [
            ft.Container(
                expand=True,
                padding=20,
                content=_build_message_bubbles(view_model.messages, colors),
            ),
            ft.Container(
                bgcolor="#ffffff",
                border=ft.Border.only(top=ft.BorderSide(1, colors.border)),
                padding=16,
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ATTACH_FILE,
                            icon_size=20,
                            icon_color=colors.text_sec,
                        ),
                        ft.IconButton(
                            ft.Icons.EMOJI_EMOTIONS_OUTLINED,
                            icon_size=20,
                            icon_color=colors.text_sec,
                        ),
                        ft.TextField(
                            expand=True,
                            height=40,
                            border_radius=8,
                            bgcolor=colors.input_bg,
                            content_padding=ft.Padding.symmetric(
                                horizontal=14, vertical=8
                            ),
                            hint_text="输入消息…",
                            value=view_model.draft,
                            on_change=lambda event: view_model.set_draft(
                                event.control.value
                            ),
                            on_submit=lambda _: view_model.send(),
                        ),
                        ft.Container(
                            width=40,
                            height=40,
                            border_radius=8,
                            bgcolor=colors.accent,
                            alignment=ft.Alignment.CENTER,
                            on_click=lambda _: view_model.send(),
                            content=ft.Icon(
                                ft.Icons.SEND, size=18, color="#ffffff"
                            ),
                        ),
                    ],
                    spacing=4,
                ),
            ),
        ],
        expand=True,
        spacing=0,
    )
    return detail_panel(item, item.subtitle, body, colors)
