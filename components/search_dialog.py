"""全局搜索弹窗组件模块。

提供命令面板风格的全局搜索功能：
- 按 Ctrl+Shift+F 唤起
- 实时搜索条目和消息
- 点击结果跳转到对应页面
- 支持 ESC 关闭、方向键导航
"""

import flet as ft

from components.avatar import avatar_circle
from services.repository import search_all
import theme


def _highlight_text(text: str, query: str) -> ft.Text:
    """高亮显示匹配的关键词。

    Args:
        text: 原始文本。
        query: 搜索关键词。

    Returns:
        包含高亮样式的 Text 组件。
    """
    if not query:
        return ft.Text(text, size=13, color=theme.C_TEXT)

    query_lower = query.lower()
    text_lower = text.lower()
    parts = []
    last_idx = 0

    while True:
        idx = text_lower.find(query_lower, last_idx)
        if idx == -1:
            if last_idx < len(text):
                parts.append(
                    ft.TextSpan(text[last_idx:], style=ft.TextStyle(font_size=13))
                )
            break
        if idx > last_idx:
            parts.append(
                ft.TextSpan(text[last_idx:idx], style=ft.TextStyle(font_size=13))
            )
        parts.append(
            ft.TextSpan(
                text[idx : idx + len(query)],
                style=ft.TextStyle(font_size=13, background="#e8f0ff"),
            )
        )
        last_idx = idx + len(query)

    return ft.Text(spans=parts)


@ft.component
def SearchDialog(visible: bool, on_close, on_keyboard):
    """全局搜索弹窗组件。

    命令面板风格的居中弹窗，包含搜索输入框和结果列表。

    Args:
        visible: 是否显示弹窗。
        on_close: 关闭弹窗的回调函数。
        on_keyboard: 键盘事件处理回调。

    Returns:
        搜索弹窗组件。
    """
    query, set_query = ft.use_state("")
    results, set_results = ft.use_state([])
    focused_index, set_focused_index = ft.use_state(0)

    def _reset_state():
        """重置搜索状态。"""
        set_query("")
        set_results([])
        set_focused_index(0)

    ft.use_effect(
        lambda: _reset_state() if visible else None,
        dependencies=[visible],
    )

    def _perform_search(q: str):
        """执行搜索并更新结果列表。

        Args:
            q: 搜索关键词。
        """
        if q.strip():
            set_results(search_all(q))
            set_focused_index(0)
        else:
            set_results([])

    ft.use_effect(
        lambda: _perform_search(query),
        dependencies=[query],
    )

    def _on_select_result(item):
        """选择搜索结果并导航到对应页面。

        Args:
            item: 选中的条目对象。
        """
        on_close()
        ft.context.page.navigate(f"/{item.module_id}/{item.id}")

    def _build_result_item(item, module_label, context, is_focused):
        """构建单个搜索结果项。

        Args:
            item: 条目对象。
            module_label: 模块显示名称。
            context: 匹配上下文。
            is_focused: 是否为当前焦点项。

        Returns:
            结果项容器。
        """
        return ft.Container(
            bgcolor=theme.C_ACCENT_SOFT if is_focused else None,
            border_radius=6,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            ink=True,
            on_click=lambda _: _on_select_result(item),
            content=ft.Row(
                [
                    avatar_circle(item.name, item.color, 36),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        item.name,
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=theme.C_TEXT,
                                    ),
                                    ft.Container(
                                        padding=ft.Padding.symmetric(
                                            horizontal=6, vertical=1
                                        ),
                                        bgcolor=theme.C_SEARCH_BG,
                                        border_radius=4,
                                        content=ft.Text(
                                            module_label,
                                            size=11,
                                            color=theme.C_TEXT_SEC,
                                        ),
                                    ),
                                ],
                                spacing=8,
                            ),
                            _highlight_text(context, query),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18, color=theme.C_TEXT_SEC),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _handle_keyboard(e: ft.KeyboardEvent):
        """处理弹窗内键盘事件。

        Args:
            e: 键盘事件对象。
        """
        if e.key == "ArrowDown":
            if results:
                set_focused_index((focused_index + 1) % len(results))
        elif e.key == "ArrowUp":
            if results:
                set_focused_index((focused_index - 1) % len(results))
        elif e.key == "Enter" and results:
            _on_select_result(results[focused_index][0])
        else:
            on_keyboard(e)

    results_list = [
        _build_result_item(item, module_label, context, idx == focused_index)
        for idx, (item, module_label, context) in enumerate(results)
    ]

    if not results_list:
        if query.strip():
            results_list.append(
                ft.Container(
                    padding=32,
                    content=ft.Text(
                        "未找到匹配结果",
                        size=14,
                        color=theme.C_TEXT_SEC,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )
        else:
            results_list.append(
                ft.Container(
                    padding=32,
                    content=ft.Text(
                        "输入关键词进行搜索",
                        size=14,
                        color=theme.C_TEXT_SEC,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )

    dialog_content = ft.Container(
        width=600,
        bgcolor="#ffffff",
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color="rgba(0, 0, 0, 0.15)",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            [
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    border=ft.Border(bottom=ft.BorderSide(1, theme.C_BORDER)),
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SEARCH, size=18, color=theme.C_TEXT_SEC),
                            ft.TextField(
                                expand=True,
                                height=40,
                                border=None,
                                content_padding=0,
                                hint_text="搜索消息、联系人、邮件...",
                                value=query,
                                on_change=lambda e: set_query(e.control.value),
                                on_submit=lambda e: (
                                    _on_select_result(results[0][0])
                                    if results
                                    else None
                                ),
                                autofocus=True,
                            ),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                bgcolor=theme.C_SEARCH_BG,
                                border_radius=4,
                                content=ft.Text("ESC", size=11, color=theme.C_TEXT_SEC),
                            ),
                        ],
                        spacing=8,
                    ),
                ),
                ft.Container(
                    expand=True,
                    height=300,
                    content=ft.ListView(
                        results_list,
                        spacing=2,
                        padding=4,
                    ),
                ),
            ],
            spacing=0,
            height=380,
        ),
    )

    return ft.Stack(
        [
            ft.Container(
                expand=True,
                bgcolor="rgba(0, 0, 0, 0.3)",
                on_click=lambda _: on_close(),
            ),
            ft.Container(
                visible=visible,
                alignment=ft.Alignment.TOP_CENTER,
                padding=ft.Padding(top=120),
                content=dialog_content,
            ),
        ],
        expand=True,
    )
