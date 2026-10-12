"""列表面板视图模型。

持有列表宽度、搜索关键词与当前条目集合；所有条目变更（置顶 / 隐藏 / 删除）
都经由业务服务完成，视图模型只负责编排与状态通知。
"""

from __future__ import annotations

from models import ROOT_ROUTE, Item, WorkspaceRoute
from service import SettingsService, WorkspaceService
from viewmodel.base import RouteTarget, ViewModel

# 关闭当前条目后需要跳转的菜单动作
_NAVIGATING_ACTIONS: frozenset[str] = frozenset({"hide", "delete"})


class ListPanelViewModel(ViewModel):
    """列表面板状态。

    Args:
        workspace: 工作区业务服务。
        settings: 设置业务服务（读取列表宽度上下限）。
    """

    def __init__(
        self, workspace: WorkspaceService, settings: SettingsService
    ) -> None:
        super().__init__()
        self._workspace = workspace
        self._settings = settings
        self._width: int = settings.layout().list_default
        self._query: str = ""
        self._module_id: str = ""
        self._item_id: str = ""
        self._items: list[Item] = []

    # ── 只读状态 ────────────────────────────────────────────

    @property
    def width(self) -> int:
        """列表面板当前宽度。"""
        return self._width

    @property
    def query(self) -> str:
        """搜索关键词。"""
        return self._query

    @property
    def module_label(self) -> str:
        """当前模块显示名。"""
        return self._workspace.module_label(self._module_id)

    @property
    def selected_item_id(self) -> str:
        """当前选中条目 ID。"""
        return self._item_id

    @property
    def items(self) -> tuple[Item, ...]:
        """按搜索条件过滤后的条目。"""
        keyword = self._query.strip().lower()
        if not keyword:
            return tuple(self._items)
        return tuple(
            item
            for item in self._items
            if keyword in item.name.lower() or keyword in item.preview.lower()
        )

    def is_selected(self, item_id: str) -> bool:
        """条目是否为当前选中项。"""
        return item_id == self._item_id

    def item_route(self, item_id: str) -> str:
        """条目对应的路由路径。

        Args:
            item_id: 条目 ID。

        Returns:
            形如 ``/chat/zhang`` 的路径。
        """
        return WorkspaceRoute.for_item(self._module_id, item_id)

    # ── 状态变更 ────────────────────────────────────────────

    def sync_route(self, location: str) -> RouteTarget:
        """路由变化时重载列表。

        搜索关键词会被重置（切换会话后不应残留上一轮的过滤条件）。

        Args:
            location: 新的路由位置。

        Returns:
            未选中任何条目但列表非空时，返回首个条目的路由。
        """
        route = WorkspaceRoute.parse(location)
        self._module_id = route.module_id
        self._item_id = route.item_id
        self._query = ""
        self._reload_items()
        self.notify()

        if not route.has_item and self.items:
            return WorkspaceRoute.for_item(route.module_id, self.items[0].id)
        return None

    def set_query(self, query: str) -> None:
        """更新搜索关键词。"""
        self._query = query
        self.notify()

    def resize_by(self, delta: float) -> None:
        """按拖动位移调整列表宽度，并限制在配置区间内。

        Args:
            delta: 水平位移（像素）。
        """
        layout = self._settings.layout()
        self._width = int(
            max(layout.list_min, min(layout.list_max, self._width + delta))
        )
        self.notify()

    def activate(self, action: str, item_id: str) -> RouteTarget:
        """执行右键菜单动作。

        Args:
            action: ``mark_unread`` / ``toggle_pin`` / ``hide`` / ``delete``。
            item_id: 目标条目 ID。

        Returns:
            若隐藏或删除了当前选中条目，返回应跳转的路由。
        """
        self._workspace.remove(action, item_id)
        self._reload_items()

        should_navigate = action in _NAVIGATING_ACTIONS and item_id == self._item_id
        if not should_navigate:
            self.notify()
            return None

        remaining = self._items
        if remaining:
            return WorkspaceRoute.for_item(self._module_id, remaining[0].id)
        return ROOT_ROUTE

    def _reload_items(self) -> None:
        """从服务重新拉取当前模块的条目。"""
        self._items = self._workspace.list_items(self._module_id)
