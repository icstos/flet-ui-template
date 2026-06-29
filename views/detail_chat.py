"""聊天详情页组件模块。

显示聊天会话的消息列表和输入框，支持发送消息。
"""

import flet as ft

from components.detail_panel import detail_panel
from services.repository import add_message, get_item, get_messages
import theme


def _build_message_bubbles(messages) -> ft.Column:
    """构建消息气泡列表。

    根据消息的角色（自己/对方）显示不同的样式和对齐方式。

    Args:
        messages: 消息列表。

    Returns:
        包含所有消息气泡的可滚动列。
    """
    bubbles = []
    for msg in messages:
        is_me = msg.role == "me"

        # 构建气泡内容
        bubble = ft.Container(
            bgcolor=theme.C_ACCENT if is_me else "#ffffff",
            border_radius=ft.BorderRadius.only(
                top_left=12,
                top_right=12,
                bottom_left=4 if is_me else 12,
                bottom_right=12 if is_me else 4,
            ),
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border=None if is_me else ft.Border.all(1, theme.C_BORDER),
            content=ft.Text(
                msg.text,
                size=14,
                color="#ffffff" if is_me else theme.C_TEXT,
                selectable=True,
            ),
        )

        # 根据角色决定对齐方式
        row_children = [bubble]
        if is_me:
            # 己方消息右对齐
            row_children.insert(0, ft.Container(expand=True))
        else:
            # 对方消息左对齐
            row_children.append(ft.Container(expand=True))

        bubbles.append(ft.Row(row_children, spacing=0))

    return ft.Column(bubbles, spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)


@ft.component
def ChatDetail():
    """聊天详情页组件。

    布局结构：
    - 上部：消息列表（可滚动）
    - 下部：输入工具栏（附件、表情、输入框、发送按钮）

    Returns:
        聊天详情面板。
    """
    params = ft.use_route_params()
    item = get_item(params.get("item_id", ""))

    # 条目不存在时返回空容器
    if not item:
        return ft.Container(expand=True)

    messages, set_messages = ft.use_state(get_messages(item.id))
    draft, set_draft = ft.use_state("")

    def _send(e=None):
        """发送消息。

        清空草稿框，将消息保存到数据库并刷新消息列表。

        Args:
            e: 事件对象（可选）。
        """
        text = draft.strip() if isinstance(draft, str) else str(draft).strip()
        if not text:
            return
        add_message(item.id, "me", text)
        set_messages(get_messages(item.id))
        set_draft("")

    # 消息列表 + 输入框
    detail_body = ft.Column(
        [
            # 消息展示区
            ft.Container(
                expand=True, padding=20, content=_build_message_bubbles(messages)
            ),
            # 输入工具栏
            ft.Container(
                bgcolor="#ffffff",
                border=ft.Border.only(top=ft.BorderSide(1, theme.C_BORDER)),
                padding=16,
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ATTACH_FILE,
                            icon_size=20,
                            icon_color=theme.C_TEXT_SEC,
                        ),
                        ft.IconButton(
                            ft.Icons.EMOJI_EMOTIONS_OUTLINED,
                            icon_size=20,
                            icon_color=theme.C_TEXT_SEC,
                        ),
                        ft.TextField(
                            expand=True,
                            height=40,
                            border_radius=8,
                            bgcolor=theme.C_INPUT_BG,
                            content_padding=ft.Padding.symmetric(
                                horizontal=14, vertical=8
                            ),
                            hint_text="输入消息…",
                            value=draft,
                            on_change=lambda e: set_draft(e.control.value),
                            on_submit=lambda e: _send(e),
                        ),
                        ft.Container(
                            width=40,
                            height=40,
                            border_radius=8,
                            bgcolor=theme.C_ACCENT,
                            alignment=ft.Alignment.CENTER,
                            on_click=_send,
                            content=ft.Icon(ft.Icons.SEND, size=18, color="#ffffff"),
                        ),
                    ],
                    spacing=4,
                ),
            ),
        ],
        expand=True,
        spacing=0,
    )
    return detail_panel(item, item.subtitle, detail_body)
