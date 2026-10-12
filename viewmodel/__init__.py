"""视图模型层。

连接视图与业务：持有界面状态、调用业务服务，并在状态变化时通知订阅者。
本层是**纯 Python 类**，不依赖 Flet 或任何 UI 组件，也不直接操作界面。
"""

from __future__ import annotations

from viewmodel.auth import (
    ChangePasswordViewModel,
    LoginViewModel,
    RegisterViewModel,
)
from viewmodel.base import RouteTarget, ViewModel
from viewmodel.chat_detail import ChatDetailViewModel
from viewmodel.generic_detail import GenericDetailViewModel
from viewmodel.list_panel import ListPanelViewModel
from viewmodel.nav_rail import NavRailViewModel
from viewmodel.search_overlay import SearchOverlayViewModel
from viewmodel.settings import SettingsViewModel
from viewmodel.shell import ShellViewModel, TabData
from viewmodel.theme import ThemeState
from viewmodel.title_bar import TitleBarViewModel

__all__ = [
    "ChangePasswordViewModel",
    "ChatDetailViewModel",
    "GenericDetailViewModel",
    "ListPanelViewModel",
    "LoginViewModel",
    "NavRailViewModel",
    "RegisterViewModel",
    "RouteTarget",
    "SearchOverlayViewModel",
    "SettingsViewModel",
    "ShellViewModel",
    "TabData",
    "ThemeState",
    "TitleBarViewModel",
    "ViewModel",
]
