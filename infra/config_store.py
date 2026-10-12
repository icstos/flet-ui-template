"""基于 TOML 文件的配置存储。

显式序列化而非依赖第三方 TOML 写库：一方面保持与既有 ``config.toml``
**逐字节兼容**（节名、键序、转义规则均不变），另一方面避免为写配置再引入
一个运行时依赖。

实现 :class:`~infra.protocols.SettingsStore` 协议。
"""

from __future__ import annotations

import tomllib
from dataclasses import fields
from pathlib import Path

from models import (
    AppSettings,
    ColorSettings,
    DatabaseSettings,
    LayoutSettings,
    WindowSettings,
)

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"
"""默认配置文件路径（项目根目录下的 ``config.toml``）。"""

# 节名 -> 类型；顺序即写盘顺序，保持与既有文件一致。
_SECTIONS: tuple[tuple[str, type], ...] = (
    ("layout", LayoutSettings),
    ("window", WindowSettings),
    ("colors", ColorSettings),
    ("database", DatabaseSettings),
)


def _escape(value: str) -> str:
    """转义 TOML 基本字符串中的特殊字符。"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _format_value(value: object) -> str:
    """把 Python 值格式化为 TOML 字面量。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return f'"{_escape(str(value))}"'


class TomlSettingsStore:
    """把 :class:`~models.AppSettings` 读写到 TOML 文件。

    Args:
        path: 配置文件路径；默认使用项目根目录下的 ``config.toml``。
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else DEFAULT_CONFIG_PATH
        self._cache: AppSettings | None = None

    @property
    def path(self) -> Path:
        """当前配置文件路径。"""
        return self._path

    def load(self) -> AppSettings:
        """读取配置。

        首次调用时从磁盘读取并缓存；此后直接返回缓存实例，
        以保证全局共享同一份可变配置对象。

        Returns:
            当前配置；文件不存在时返回默认配置。
        """
        if self._cache is None:
            self._cache = self._read()
        return self._cache

    def save(self, settings: AppSettings) -> None:
        """把配置写入 TOML 文件，并更新缓存。

        Args:
            settings: 待保存的配置。
        """
        lines: list[str] = []
        for section_name, section_type in _SECTIONS:
            section = getattr(settings, section_name)
            lines.append(f"[{section_name}]")
            for section_field in fields(section_type):
                value = getattr(section, section_field.name)
                lines.append(f"{section_field.name} = {_format_value(value)}")
            lines.append("")

        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("\n".join(lines), encoding="utf-8")
        self._cache = settings

    def reload(self) -> AppSettings:
        """丢弃缓存并从磁盘重新读取。

        Returns:
            重新读取后的配置。
        """
        self._cache = None
        return self.load()

    def _read(self) -> AppSettings:
        """从磁盘解析配置，未知键与缺失键均安全忽略。"""
        settings = AppSettings()
        if not self._path.exists():
            return settings

        with self._path.open("rb") as handle:
            raw = tomllib.load(handle)

        for section_name, _ in _SECTIONS:
            section_data = raw.get(section_name)
            if not isinstance(section_data, dict):
                continue
            section = getattr(settings, section_name)
            for key, value in section_data.items():
                if hasattr(section, key):
                    setattr(section, key, value)
        return settings
