"""设置页视图模型。

主题改色不再依赖「保存 -> 重载模块 -> 连续导航」的强制刷新，
而是把变更写入 :class:`~viewmodel.theme.ThemeState`，由订阅者自动重渲染。
"""

from __future__ import annotations

from models import COLOR_PRESETS, LOGIN_ROUTE
from service import AuthService, SettingsService
from viewmodel.base import RouteTarget, ViewModel
from viewmodel.theme import ThemeState

BACK_ROUTE = "/chat/zhang"
"""设置页返回按钮的目标路由（沿用既有行为）。"""


class SettingsViewModel(ViewModel):
    """设置页状态：可编辑的四个主题色。

    Args:
        settings: 设置业务服务。
        theme: 全局主题状态。
        auth: 认证业务服务。
    """

    def __init__(
        self,
        settings: SettingsService,
        theme: ThemeState,
        auth: AuthService,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._theme = theme
        self._auth = auth

        colors = theme.colors
        self._accent: str = colors.accent
        self._sidebar: str = colors.sidebar
        self._content_bg: str = colors.content_bg
        self._text: str = colors.text

    @property
    def presets(self) -> tuple[str, ...]:
        """常用颜色预设。"""
        return COLOR_PRESETS

    @property
    def back_route(self) -> str:
        """返回按钮的目标路由。"""
        return BACK_ROUTE

    @property
    def accent(self) -> str:
        """主颜色输入值。"""
        return self._accent

    @property
    def sidebar(self) -> str:
        """侧栏色输入值。"""
        return self._sidebar

    @property
    def content_bg(self) -> str:
        """内容背景色输入值。"""
        return self._content_bg

    @property
    def text_color(self) -> str:
        """文字色输入值。"""
        return self._text

    def set_accent(self, value: str) -> None:
        """更新主颜色。"""
        self._accent = value
        self.notify()

    def set_sidebar(self, value: str) -> None:
        """更新侧栏色。"""
        self._sidebar = value
        self.notify()

    def set_content_bg(self, value: str) -> None:
        """更新内容背景色。"""
        self._content_bg = value
        self.notify()

    def set_text_color(self, value: str) -> None:
        """更新文字色。"""
        self._text = value
        self.notify()

    def apply_and_save(self) -> None:
        """把当前四个颜色写入配置并立即生效。"""
        self._theme.apply_colors(
            {
                "accent": self._accent,
                "sidebar": self._sidebar,
                "content_bg": self._content_bg,
                "text": self._text,
            }
        )

    def restore_defaults(self) -> None:
        """从磁盘重新读取配置，并把输入框同步为读取结果。"""
        self._theme.reload()
        colors = self._theme.colors
        self._accent = colors.accent
        self._sidebar = colors.sidebar
        self._content_bg = colors.content_bg
        self._text = colors.text
        self.notify()

    def logout(self) -> RouteTarget:
        """退出登录。

        Returns:
            登录页路由。
        """
        self._auth.logout()
        return LOGIN_ROUTE
