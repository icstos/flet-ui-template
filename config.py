"""应用配置模块。

提供类型化的配置管理，支持从 TOML 文件加载、保存到文件、热重载等功能。
配置分为布局、窗口、颜色、数据库四个配置节。
"""

from dataclasses import dataclass, field, fields
from pathlib import Path
import tomllib

# 默认配置文件路径
_CONFIG_PATH = Path(__file__).parent / "config.toml"


@dataclass(slots=True)
class LayoutConfig:
    """布局相关配置。"""

    nav_width: int = 68  # 侧边导航栏宽度
    list_min: int = 200  # 列表面板最小宽度
    list_max: int = 480  # 列表面板最大宽度
    list_default: int = 300  # 列表面板默认宽度
    title_bar_h: int = 40  # 标题栏高度


@dataclass(slots=True)
class WindowConfig:
    """窗口相关配置。"""

    title: str = "CSTOS"  # 窗口标题
    subtitle: str = "企业协作"  # 窗口副标题
    width: int = 1180  # 窗口默认宽度
    height: int = 720  # 窗口默认高度
    min_width: int = 920  # 窗口最小宽度
    min_height: int = 520  # 窗口最小高度
    frameless: bool = True  # 是否使用无边框窗口


@dataclass(slots=True)
class ColorConfig:
    """颜色主题配置。"""

    sidebar: str = "#141820"  # 侧边栏背景色
    sidebar_hover: str = "#1e2433"  # 侧边栏悬停色
    sidebar_active: str = "#252d3d"  # 侧边栏选中色
    accent: str = "#3b7cff"  # 主题强调色
    accent_soft: str = "#e8f0ff"  # 柔和强调色
    list_bg: str = "#ffffff"  # 列表背景色
    content_bg: str = "#f4f6f9"  # 内容区背景色
    border: str = "#e4e8ef"  # 边框颜色
    text: str = "#1a1d26"  # 主文字颜色
    text_sec: str = "#8b92a5"  # 次要文字颜色
    title_bar: str = "#141820"  # 标题栏背景色
    search_bg: str = "#f0f2f6"  # 搜索框背景色
    icon_inactive: str = "#7d8496"  # 未激活图标颜色
    window_btn_icon: str = "#b8bcc8"  # 窗口按钮图标颜色
    title_text: str = "#e8eaef"  # 标题栏文字颜色
    title_subtitle: str = "#6b7288"  # 标题栏副标题颜色
    input_bg: str = "#f4f6f9"  # 输入框背景色
    chat_self_bg: str = "#ffffff"  # 己方聊天气泡背景色
    chat_self_border: str = "#e4e8ef"  # 己方聊天气泡边框色


@dataclass(slots=True)
class DatabaseConfig:
    """数据库配置。"""

    url: str = "sqlite:///data/cstos.db"  # 数据库连接 URL


@dataclass(slots=True)
class AppConfig:
    """应用总配置，聚合所有配置节。"""

    layout: LayoutConfig = field(default_factory=LayoutConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    colors: ColorConfig = field(default_factory=ColorConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)


# 全局配置单例
_config: AppConfig | None = None


def _apply_section[T](obj: T, data: dict) -> None:
    """将字典数据应用到 dataclass 实例上。

    只设置对象已存在的字段，忽略未知字段。

    Args:
        obj: 目标 dataclass 实例。
        data: 包含配置键值对的字典。
    """
    for key, value in data.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


def _toml_escape(value: str) -> str:
    """转义 TOML 字符串中的特殊字符。

    Args:
        value: 原始字符串。

    Returns:
        转义后的字符串。
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _format_toml_value(value) -> str:
    """将 Python 值格式化为 TOML 值字符串。

    Args:
        value: 要格式化的值。

    Returns:
        TOML 格式的字符串表示。
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return f'"{_toml_escape(str(value))}"'


def _write_section(lines: list[str], section_name: str, section_obj) -> None:
    """将一个配置节写入 TOML 行列表。

    Args:
        lines: 行列表，结果会追加到其中。
        section_name: TOML 节名称。
        section_obj: dataclass 配置节实例。
    """
    lines.append(f"[{section_name}]")
    for f in fields(section_obj):
        value = getattr(section_obj, f.name)
        lines.append(f"{f.name} = {_format_toml_value(value)}")
    lines.append("")


def load_config(path: Path | str | None = None) -> AppConfig:
    """加载配置文件。

    如果已加载过配置，则直接返回缓存的实例。
    配置文件不存在时返回默认配置。

    Args:
        path: 配置文件路径，为 None 时使用默认路径。

    Returns:
        加载后的 AppConfig 实例。
    """
    global _config
    if _config is not None:
        return _config

    cfg = AppConfig()
    config_path = Path(path) if path else _CONFIG_PATH

    if config_path.exists():
        with open(config_path, "rb") as f:
            raw = tomllib.load(f)

        # 按配置节依次应用
        section_map = (
            ("layout", cfg.layout),
            ("window", cfg.window),
            ("colors", cfg.colors),
            ("database", cfg.database),
        )
        for section_name, section_obj in section_map:
            if section_name in raw:
                _apply_section(section_obj, raw[section_name])

    _config = cfg
    return cfg


def get_config() -> AppConfig:
    """获取当前配置实例。

    如果尚未加载，则自动加载默认配置。

    Returns:
        当前 AppConfig 实例。
    """
    return _config if _config is not None else load_config()


def save_config(path: Path | str | None = None) -> None:
    """将当前配置保存到 TOML 文件。

    Args:
        path: 保存路径，为 None 时使用默认路径。
    """
    config_path = Path(path) if path else _CONFIG_PATH
    cfg = get_config()

    lines: list[str] = []
    _write_section(lines, "layout", cfg.layout)
    _write_section(lines, "window", cfg.window)
    _write_section(lines, "colors", cfg.colors)
    _write_section(lines, "database", cfg.database)

    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def reload_config(path: Path | str | None = None) -> AppConfig:
    """强制从磁盘重新加载配置。

    清除缓存的配置实例，重新从文件加载。

    Args:
        path: 配置文件路径，为 None 时使用默认路径。

    Returns:
        重新加载后的 AppConfig 实例。
    """
    global _config
    _config = None
    return load_config(path)
