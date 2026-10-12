"""自定义标题栏视图模型。"""

from __future__ import annotations

from viewmodel.base import ViewModel


class TitleBarViewModel(ViewModel):
    """标题栏状态：最大化标记与悬停按钮。

    窗口本身的最小化 / 最大化 / 关闭属于操作系统交互，由视图层执行；
    本模型只保存「界面需要据此渲染」的状态。
    """

    def __init__(self) -> None:
        super().__init__()
        self._maximized: bool = False
        self._hovered: str = ""

    @property
    def maximized(self) -> bool:
        """窗口是否处于最大化状态。"""
        return self._maximized

    @property
    def hovered_button(self) -> str:
        """当前被悬停的窗口按钮标识；无则空串。"""
        return self._hovered

    def sync_maximized(self, maximized: bool) -> None:
        """与真实窗口状态对齐。

        Args:
            maximized: 窗口是否最大化。
        """
        if maximized != self._maximized:
            self._maximized = maximized
            self.notify()

    def is_hovered(self, button_id: str) -> bool:
        """指定按钮是否处于悬停态。"""
        return self._hovered == button_id

    def set_hover(self, button_id: str, hovered: bool) -> None:
        """更新悬停按钮。

        Args:
            button_id: 按钮标识。
            hovered: 是否进入悬停。
        """
        target = button_id if hovered else ""
        if target != self._hovered:
            self._hovered = target
            self.notify()
