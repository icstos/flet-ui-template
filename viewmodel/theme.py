"""全局主题状态。

替代旧实现里「保存配置 -> ``importlib.reload`` 主题模块 -> 连续两次导航」
的强制刷新手法：改色只需更新本状态并 :meth:`~models.reactive.Observable.notify`，
所有订阅了主题的视图即自动重新派生，无需重启或跳转。
"""

from __future__ import annotations

from collections.abc import Mapping

from models import AppSettings, ColorSettings, LayoutSettings, WindowSettings
from service import SettingsService
from viewmodel.base import ViewModel


class ThemeState(ViewModel):
    """当前生效的配色与布局尺寸。

    Args:
        settings: 设置业务服务。
    """

    def __init__(self, settings: SettingsService) -> None:
        super().__init__()
        self._settings = settings
        self._snapshot: AppSettings = settings.settings()

    @property
    def colors(self) -> ColorSettings:
        """当前配色。"""
        return self._snapshot.colors

    @property
    def layout(self) -> LayoutSettings:
        """当前布局尺寸。"""
        return self._snapshot.layout

    @property
    def window(self) -> WindowSettings:
        """当前窗口配置。"""
        return self._snapshot.window

    def apply_colors(self, changes: Mapping[str, str]) -> None:
        """更新部分配色、持久化，并通知全部订阅者。

        Args:
            changes: 字段名到颜色值的映射。
        """
        self._settings.update_colors(changes)
        self._snapshot = self._settings.settings()
        self.notify()

    def reload(self) -> None:
        """丢弃缓存并从磁盘重新读取配置，然后通知订阅者。"""
        self._snapshot = self._settings.reload()
        self.notify()
