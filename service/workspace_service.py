"""工作区业务服务。

编排模块、条目、消息相关的用例，向视图模型暴露面向业务语义的方法
（「置顶 / 隐藏 / 标记未读 / 发送消息」），而不是裸的字段更新。

只依赖 :class:`~infra.protocols.WorkspaceRepository` 抽象。
"""

from __future__ import annotations

from infra.protocols import WorkspaceRepository
from models import Item, Message, MessageRole, Module


class WorkspaceService:
    """模块 / 条目 / 消息用例。

    Args:
        repository: 工作区数据仓库。
    """

    def __init__(self, repository: WorkspaceRepository) -> None:
        self._repository = repository

    # ── 读取 ────────────────────────────────────────────────

    def list_modules(self) -> tuple[Module, ...]:
        """全部功能模块（按排序）。"""
        return self._repository.list_modules()

    def list_items(self, module_id: str) -> list[Item]:
        """模块下未隐藏的条目，置顶优先。"""
        return self._repository.list_items(module_id)

    def get_item(self, item_id: str) -> Item | None:
        """按 ID 取条目。"""
        return self._repository.get_item(item_id)

    def list_messages(self, item_id: str) -> list[Message]:
        """条目的全部消息（按顺序）。"""
        return self._repository.list_messages(item_id)

    def default_item_id(self, module_id: str) -> str:
        """模块下第一个条目的 ID；无条目时返回空串。"""
        items = self._repository.list_items(module_id)
        return items[0].id if items else ""

    def search(self, query: str) -> list[Item]:
        """跨模块搜索条目；查询为空时返回全部。"""
        return self._repository.search_items(query)

    def module_label(self, module_id: str) -> str:
        """模块显示名；未知模块返回空串。"""
        for module in self._repository.list_modules():
            if module.id == module_id:
                return module.label
        return ""

    # ── 写入 ────────────────────────────────────────────────

    def send_message(self, item_id: str, text: str) -> Message | None:
        """以「己方」身份发送一条消息。

        Args:
            item_id: 目标会话。
            text: 消息正文；空白内容不发送。

        Returns:
            新消息；内容为空时返回 ``None``。
        """
        content = text.strip()
        if not content:
            return None
        return self._repository.add_message(
            item_id, MessageRole.ME, content
        )

    def mark_unread(self, item_id: str) -> None:
        """标记条目为未读。"""
        self._repository.update_item(item_id, is_unread=True)

    def toggle_pin(self, item_id: str) -> None:
        """切换条目的置顶状态。"""
        item = self._repository.get_item(item_id)
        if item is None:
            return
        self._repository.update_item(item_id, is_pinned=not item.is_pinned)

    def hide_item(self, item_id: str) -> None:
        """隐藏条目（不再出现在列表中）。"""
        self._repository.update_item(item_id, is_hidden=True)

    def delete_item(self, item_id: str) -> bool:
        """删除条目。"""
        return self._repository.delete_item(item_id)

    def remove(self, action: str, item_id: str) -> None:
        """按右键菜单动作标识执行相应操作。

        集中在此处以避免视图层出现业务分支。

        Args:
            action: 动作标识，取值 ``mark_unread`` / ``toggle_pin`` / ``hide`` / ``delete``。
            item_id: 目标条目 ID。
        """
        match action:
            case "mark_unread":
                self.mark_unread(item_id)
            case "toggle_pin":
                self.toggle_pin(item_id)
            case "hide":
                self.hide_item(item_id)
            case "delete":
                self.delete_item(item_id)
