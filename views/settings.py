"""设置页面组件模块。

提供主题颜色自定义功能，包括：
- 主颜色、侧栏色、内容背景、文字色的自定义
- 常用颜色预设快速选择
- 保存配置和恢复默认值
"""

import importlib

import flet as ft

from config import get_config, save_config
import theme

# 预设主题色列表
_COLOR_PRESETS = [
    "#3b7cff",  # 蓝色
    "#50c878",  # 绿色
    "#e6a23c",  # 橙色
    "#9b59b6",  # 紫色
    "#e74c3c",  # 红色
    "#4a90d9",  # 天蓝
]


def _color_preview_box(color: str) -> ft.Container:
    """构建颜色预览小方块。

    Args:
        color: 颜色值。

    Returns:
        颜色预览容器。
    """
    return ft.Container(
        width=28,
        height=28,
        border_radius=4,
        bgcolor=color,
        border=ft.Border.all(1, "#ddd"),
    )


def _color_input_row(
    label: str,
    value: str,
    on_change,
) -> ft.Row:
    """构建颜色输入行。

    Args:
        label: 标签文本。
        value: 当前颜色值。
        on_change: 值变化回调。

    Returns:
        颜色输入行组件。
    """
    return ft.Row(
        [
            ft.Text(label, width=80, color=theme.C_TEXT),
            ft.TextField(value=value, width=160, on_change=on_change),
            _color_preview_box(value),
        ],
        spacing=8,
    )


@ft.component
def SettingsView():
    """设置页面组件。

    提供主题颜色的自定义配置，支持保存到配置文件和恢复默认值。

    Returns:
        设置页面容器。
    """

    def go_back(_):
        """返回聊天页面。"""
        ft.context.page.navigate("/chat/zhang")

    cfg = get_config()
    colors = cfg.colors

    # 各颜色的状态
    accent, set_accent = ft.use_state(colors.accent)
    sidebar, set_sidebar = ft.use_state(colors.sidebar)
    content_bg, set_content_bg = ft.use_state(colors.content_bg)
    text_color, set_text_color = ft.use_state(colors.text)

    def _apply_and_save(_):
        """应用并保存配置。

        将当前颜色设置写入配置对象，保存到文件，
        重新加载主题模块，并触发页面刷新。
        """
        colors.accent = accent
        colors.sidebar = sidebar
        colors.content_bg = content_bg
        colors.text = text_color
        save_config()
        importlib.reload(theme)
        # 通过导航切换强制组件重新渲染以应用新主题
        cur = ft.context.page.route
        ft.context.page.navigate("/")
        ft.context.page.navigate(cur)

    def _restore_defaults(_):
        """恢复为默认配置。

        从磁盘重新加载配置，重置所有颜色状态。
        """
        from config import reload_config

        new_cfg = reload_config()
        importlib.reload(theme)
        set_accent(new_cfg.colors.accent)
        set_sidebar(new_cfg.colors.sidebar)
        set_content_bg(new_cfg.colors.content_bg)
        set_text_color(new_cfg.colors.text)
        ft.context.page.update()

    return ft.Container(
        expand=True,
        bgcolor=theme.C_CONTENT_BG,
        padding=32,
        content=ft.Column(
            [
                # 标题栏
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK, icon_size=20, on_click=go_back
                        ),
                        ft.Text(
                            "设置",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=theme.C_TEXT,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Text("应用偏好与账号管理", size=14, color=theme.C_TEXT_SEC),
                ft.Divider(),
                # 主题色设置区
                ft.Text("主题色", weight=ft.FontWeight.W_600, color=theme.C_TEXT),
                ft.Row(
                    [
                        # 左侧：颜色输入框
                        ft.Column(
                            [
                                _color_input_row(
                                    "主颜色",
                                    accent,
                                    lambda e: set_accent(e.control.value),
                                ),
                                _color_input_row(
                                    "侧栏色",
                                    sidebar,
                                    lambda e: set_sidebar(e.control.value),
                                ),
                                _color_input_row(
                                    "内容背景",
                                    content_bg,
                                    lambda e: set_content_bg(e.control.value),
                                ),
                                _color_input_row(
                                    "文字色",
                                    text_color,
                                    lambda e: set_text_color(e.control.value),
                                ),
                            ]
                        ),
                        ft.Container(width=24),
                        # 右侧：常用颜色预设
                        ft.Column(
                            [
                                ft.Text("常用颜色", color=theme.C_TEXT),
                                ft.Row(
                                    [
                                        ft.Container(
                                            width=28,
                                            height=28,
                                            border_radius=14,
                                            bgcolor=p,
                                            on_click=lambda e, p=p: set_accent(p),
                                        )
                                        for p in _COLOR_PRESETS
                                    ],
                                    spacing=6,
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=24,
                ),
                # 操作按钮
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "保存",
                            on_click=_apply_and_save,
                            bgcolor=theme.C_ACCENT,
                            color="#ffffff",
                        ),
                        ft.TextButton("恢复为默认", on_click=_restore_defaults),
                    ],
                    spacing=12,
                ),
            ],
            spacing=16,
        ),
    )
