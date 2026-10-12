"""聊天详情视图模型。"""

from __future__ import annotations

from models import Item, Message
from service import WorkspaceService
from viewmodel.base import ViewModel


class ChatDetailViewModel(ViewModel):
    """聊天会话状态：当前条目、消息列表与输入草稿。

    Args:
        workspace: 工作区业务服务。
    """

    def __init__(self, workspace: WorkspaceService) -> None:
        super().__init__()
        self._workspace = workspace
        self._item_id: str = ""
        self._item: Item | None = None
        self._messages: list[Message] = []
        self._draft: str = ""

    @property
    def item(self) -> Item | None:
        """当前会话条目；不存在为 ``None``。"""
        return self._item

    @property
    def messages(self) -> tuple[Message, ...]:
        """消息列表。"""
        return tuple(self._messages)

    @property
    def draft(self) -> str:
        """输入框草稿。"""
        return self._draft

    @property
    def is_empty(self) -> bool:
        """是否没有可展示的会话。"""
        return self._item is None

    def load(self, item_id: str) -> None:
        """加载指定会话。

        条目 ID 未变化时不重复查库，避免每次重渲染都产生查询。

        Args:
            item_id: 会话条目 ID。
        """
        if item_id == self._item_id and self._item is not None:
            return

        self._item_id = item_id
        self._item = self._workspace.get_item(item_id)
        self._messages = (
            self._workspace.list_messages(item_id) if self._item else []
        )
        self._draft = ""
        self.notify()

    def set_draft(self, text: str) -> None:
        """更新输入框草稿。"""
        self._draft = text
        self.notify()

    def send(self) -> None:
        """发送草稿内容并清空输入框；空白内容不发送。"""
        text = str(self._draft).strip()
        if not text:
            return

        self._workspace.send_message(self._item_id, text)
        self._messages = self._workspace.list_messages(self._item_id)
        self._draft = ""
        self.notify()
