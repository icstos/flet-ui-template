"""通用详情视图模型（通讯录 / 邮箱）。"""

from __future__ import annotations

from models import Item
from service import WorkspaceService
from viewmodel.base import ViewModel


class GenericDetailViewModel(ViewModel):
    """通用详情状态：仅持有一条待展示的条目。

    Args:
        workspace: 工作区业务服务。
    """

    def __init__(self, workspace: WorkspaceService) -> None:
        super().__init__()
        self._workspace = workspace
        self._item_id: str = ""
        self._item: Item | None = None

    @property
    def item(self) -> Item | None:
        """当前条目；不存在为 ``None``。"""
        return self._item

    @property
    def body(self) -> str:
        """详情正文；缺失时降级为列表预览文本。"""
        if self._item is None:
            return ""
        return self._item.detail_body or self._item.preview

    def load(self, item_id: str) -> None:
        """加载指定条目（ID 未变化时不重复查库）。

        Args:
            item_id: 条目 ID。
        """
        if item_id == self._item_id and self._item is not None:
            return
        self._item_id = item_id
        self._item = self._workspace.get_item(item_id)
        self.notify()
