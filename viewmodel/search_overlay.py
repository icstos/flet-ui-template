"""全局搜索弹窗视图模型。"""

from __future__ import annotations

from models import Item
from service import WorkspaceService
from viewmodel.base import ViewModel


class SearchOverlayViewModel(ViewModel):
    """搜索弹窗状态：开关与关键词。

    Args:
        workspace: 工作区业务服务。
    """

    def __init__(self, workspace: WorkspaceService) -> None:
        super().__init__()
        self._workspace = workspace
        self._is_open: bool = False
        self._query: str = ""

    @property
    def is_open(self) -> bool:
        """弹窗是否显示。"""
        return self._is_open

    @property
    def query(self) -> str:
        """搜索关键词。"""
        return self._query

    @property
    def module_labels(self) -> dict[str, str]:
        """模块 ID 到显示名的映射。"""
        return {module.id: module.label for module in self._workspace.list_modules()}

    @property
    def results(self) -> tuple[Item, ...]:
        """搜索结果；弹窗关闭时不返回结果。"""
        if not self._is_open:
            return ()
        return tuple(self._workspace.search(self._query))

    def open(self) -> None:
        """打开弹窗。"""
        if not self._is_open:
            self._is_open = True
            self.notify()

    def close(self) -> None:
        """关闭弹窗并清空关键词。"""
        self._is_open = False
        self._query = ""
        self.notify()

    def set_query(self, query: str) -> None:
        """更新搜索关键词。"""
        self._query = query
        self.notify()
