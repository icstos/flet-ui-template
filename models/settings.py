"""应用配置数据结构。

纯数据定义，不含任何文件读写逻辑——落盘格式由基础设施层负责，
本层只描述「配置由哪些字段构成、默认值是什么」。

字段名即配置文件中的键名，**不可随意改名**，否则会丢失用户已保存的配置。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LayoutSettings:
    """布局尺寸配置。"""

    nav_width: int = 68
    """侧边导航栏宽度。"""

    list_min: int = 200
    """列表面板最小宽度。"""

    list_max: int = 480
    """列表面板最大宽度。"""

    list_default: int = 300
    """列表面板默认宽度。"""

    title_bar_h: int = 40
    """标题栏高度。"""


@dataclass(slots=True)
class WindowSettings:
    """主窗口配置。"""

    title: str = "CSTOS"
    subtitle: str = "企业协作"
    width: int = 1180
    height: int = 720
    min_width: int = 920
    min_height: int = 520
    frameless: bool = True
    """是否使用无边框窗口（由应用自绘标题栏）。"""


@dataclass(slots=True)
class ColorSettings:
    """主题配色配置。"""

    sidebar: str = "#141820"
    sidebar_hover: str = "#1e2433"
    sidebar_active: str = "#252d3d"
    accent: str = "#3b7cff"
    """主强调色，用于选中态、主按钮。"""

    accent_soft: str = "#e8f0ff"
    """柔和强调色，用于选中条目底色。"""

    list_bg: str = "#ffffff"
    content_bg: str = "#f4f6f9"
    border: str = "#e4e8ef"
    text: str = "#1a1d26"
    text_sec: str = "#8b92a5"
    title_bar: str = "#141820"
    search_bg: str = "#f0f2f6"
    icon_inactive: str = "#7d8496"
    window_btn_icon: str = "#b8bcc8"
    title_text: str = "#e8eaef"
    title_subtitle: str = "#6b7288"
    input_bg: str = "#f4f6f9"
    chat_self_bg: str = "#ffffff"
    chat_self_border: str = "#e4e8ef"


@dataclass(slots=True)
class DatabaseSettings:
    """数据库配置。"""

    url: str = "sqlite:///data/cstos.db"


@dataclass(slots=True)
class AppSettings:
    """应用总配置，聚合全部配置节。"""

    layout: LayoutSettings = field(default_factory=LayoutSettings)
    window: WindowSettings = field(default_factory=WindowSettings)
    colors: ColorSettings = field(default_factory=ColorSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
