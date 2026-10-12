"""应用设置业务服务。

负责配置的读取、局部更新与持久化。只依赖
:class:`~infra.protocols.SettingsStore` 抽象，不关心落地格式是 TOML 还是其它。
"""

from __future__ import annotations

from collections.abc import Mapping

from infra.protocols import SettingsStore
from models import AppSettings, ColorSettings, LayoutSettings, WindowSettings


class SettingsService:
    """配置读写用例。

    Args:
        store: 配置存储。
    """

    def __init__(self, store: SettingsStore) -> None:
        self._store = store

    def settings(self) -> AppSettings:
        """当前生效的完整配置。"""
        return self._store.load()

    def colors(self) -> ColorSettings:
        """当前配色。"""
        return self._store.load().colors

    def layout(self) -> LayoutSettings:
        """当前布局尺寸。"""
        return self._store.load().layout

    def window(self) -> WindowSettings:
        """当前窗口配置。"""
        return self._store.load().window

    def update_colors(self, changes: Mapping[str, str]) -> ColorSettings:
        """更新配色并立即持久化。

        仅接受 :class:`~models.ColorSettings` 上已存在的字段，未知键被忽略。

        Args:
            changes: 字段名到颜色值的映射。

        Returns:
            更新后的配色。
        """
        settings = self._store.load()
        colors = settings.colors
        for key, value in changes.items():
            if hasattr(colors, key):
                setattr(colors, key, value)
        self._store.save(settings)
        return colors

    def reload(self) -> AppSettings:
        """丢弃缓存，从持久化介质重新读取配置。

        Returns:
            重新读取后的配置。
        """
        return self._store.reload()
