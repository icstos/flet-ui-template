"""主题常量模块。

从配置中动态读取布局和颜色参数，供视图层统一引用。
每次访问属性时都会从当前配置中获取最新值，支持主题热切换。
"""

from config import get_config


# 属性名到配置路径的映射
# 格式: (属性名, 配置节, 配置字段)
_THEME_ATTRS = [
    # 布局尺寸
    ("NAV_WIDTH", "layout", "nav_width"),
    ("LIST_MIN", "layout", "list_min"),
    ("LIST_MAX", "layout", "list_max"),
    ("LIST_DEFAULT", "layout", "list_default"),
    ("TITLE_BAR_H", "layout", "title_bar_h"),
    # 颜色常量
    ("C_SIDEBAR", "colors", "sidebar"),
    ("C_SIDEBAR_ACTIVE", "colors", "sidebar_active"),
    ("C_ACCENT", "colors", "accent"),
    ("C_ACCENT_SOFT", "colors", "accent_soft"),
    ("C_LIST_BG", "colors", "list_bg"),
    ("C_CONTENT_BG", "colors", "content_bg"),
    ("C_BORDER", "colors", "border"),
    ("C_TEXT", "colors", "text"),
    ("C_TEXT_SEC", "colors", "text_sec"),
    ("C_TITLE_BAR", "colors", "title_bar"),
    ("C_SEARCH_BG", "colors", "search_bg"),
    ("C_ICON_INACTIVE", "colors", "icon_inactive"),
    ("C_WINDOW_BTN", "colors", "window_btn_icon"),
    ("C_TITLE_TEXT", "colors", "title_text"),
    ("C_TITLE_SUB", "colors", "title_subtitle"),
    ("C_INPUT_BG", "colors", "input_bg"),
    ("C_CHAT_SELF_BG", "colors", "chat_self_bg"),
    ("C_CHAT_SELF_BORDER", "colors", "chat_self_border"),
]

_ATTR_MAP = {attr_name: (section, field) for attr_name, section, field in _THEME_ATTRS}


def __getattr__(name: str):
    """模块级动态属性访问。

    当访问的属性在 _ATTR_MAP 中时，从当前配置中动态读取对应值。

    Args:
        name: 属性名。

    Returns:
        配置中对应的属性值。

    Raises:
        AttributeError: 属性名不存在时抛出。
    """
    if name in _ATTR_MAP:
        section, field = _ATTR_MAP[name]
        cfg = get_config()
        return getattr(getattr(cfg, section), field)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """返回模块属性列表，包含所有主题常量名。"""
    return list(_ATTR_MAP.keys()) + list(globals().keys())
