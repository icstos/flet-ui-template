"""路由值对象。

把「形如 ``/chat/zhang`` 的路径字符串」解析为结构化、不可变的值对象，
使各层无需重复做字符串切分。
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MODULE_ID = "chat"
"""路径无法给出模块时的兜底模块。"""


@dataclass(frozen=True, slots=True)
class WorkspaceRoute:
    """工作区路由。

    Attributes:
        module_id: 模块 ID，如 ``chat``、``contacts``、``email``。
        item_id: 条目 ID；未指定时为空字符串。
    """

    module_id: str
    item_id: str

    @classmethod
    def parse(cls, location: str) -> WorkspaceRoute:
        """解析路由路径。

        与既有行为完全一致：去除首尾斜杠后按 ``/`` 切分，取前两段。

        Args:
            location: 路由路径，如 ``/chat/zhang``。

        Returns:
            解析后的路由；路径为空或无效时给出兜底值。
        """
        parts = location.strip("/").split("/")
        module_id = parts[0] if parts else DEFAULT_MODULE_ID
        item_id = parts[1] if len(parts) > 1 else ""
        return cls(module_id=module_id, item_id=item_id)

    @property
    def has_item(self) -> bool:
        """是否已定位到具体条目。"""
        return bool(self.item_id)

    @property
    def path(self) -> str:
        """该路由对应的规范路径。"""
        if not self.item_id:
            return f"/{self.module_id}"
        return f"/{self.module_id}/{self.item_id}"

    @classmethod
    def for_item(cls, module_id: str, item_id: str) -> str:
        """构造条目页路径字符串。

        Args:
            module_id: 模块 ID。
            item_id: 条目 ID。

        Returns:
            形如 ``/chat/zhang`` 的路径。
        """
        return f"/{module_id}/{item_id}"
