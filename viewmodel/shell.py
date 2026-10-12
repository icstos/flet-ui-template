"""应用外壳视图模型：标签页管理与登录态守卫。"""

from __future__ import annotations

from dataclasses import dataclass

from models import LOGIN_ROUTE, ROOT_ROUTE, SETTINGS_ROUTE, ModuleId, WorkspaceRoute
from service import AuthService, WorkspaceService
from viewmodel.base import RouteTarget, ViewModel


@dataclass(frozen=True, slots=True)
class TabData:
    """一个标签页。

    Attributes:
        route: 标签对应的路由路径，同时作为唯一标识。
        title: 显示标题。
        module_id: 所属模块 ID。
        item_id: 条目 ID。
    """

    route: str
    title: str
    module_id: str
    item_id: str


class ShellViewModel(ViewModel):
    """外壳状态：已打开的标签页集合与当前路由。

    Args:
        workspace: 工作区业务服务。
        auth: 认证业务服务。
    """

    def __init__(self, workspace: WorkspaceService, auth: AuthService) -> None:
        super().__init__()
        self._workspace = workspace
        self._auth = auth
        self._tabs: list[TabData] = []
        self._location: str = ROOT_ROUTE

    @property
    def tabs(self) -> tuple[TabData, ...]:
        """当前已打开的标签页。"""
        return tuple(self._tabs)

    @property
    def location(self) -> str:
        """当前路由位置。"""
        return self._location

    @property
    def is_authenticated(self) -> bool:
        """用户是否已登录。"""
        return self._auth.current_session() is not None

    def sync_location(self, location: str) -> RouteTarget:
        """路由变化时同步标签页。

        职责：
            1. 未登录时要求跳转登录页；
            2. 为可展示的路由创建标签（若尚不存在）。

        Args:
            location: 新的路由位置。

        Returns:
            需要跳转的目标路由；无需跳转返回 ``None``。
        """
        self._location = location

        if not self.is_authenticated:
            return LOGIN_ROUTE
        if not location or location == ROOT_ROUTE:
            return None

        resolved = self._resolve_tab(location)
        if resolved is None:
            return None

        route, title, module_id, item_id = resolved
        if any(tab.route == route for tab in self._tabs):
            return None

        self._tabs.append(
            TabData(route=route, title=title, module_id=module_id, item_id=item_id)
        )
        self.notify()
        return None

    def close_tab(self, route: str) -> RouteTarget:
        """关闭标签。

        若关闭的是当前激活标签，则返回相邻标签的路由作为跳转目标；
        全部关闭时回到默认会话。

        Args:
            route: 要关闭的标签路由。

        Returns:
            需要跳转的目标路由；无需跳转返回 ``None``。
        """
        index = next(
            (i for i, tab in enumerate(self._tabs) if tab.route == route), -1
        )
        if index < 0:
            return None

        self._tabs.pop(index)
        self.notify()

        if route != self._location:
            return None
        if not self._tabs:
            return self.default_route()
        return self._tabs[min(index, len(self._tabs) - 1)].route

    def default_route(self) -> str:
        """默认会话路由。"""
        return WorkspaceRoute.for_item(
            ModuleId.CHAT, self._workspace.default_item_id(ModuleId.CHAT)
        )

    def _resolve_tab(self, location: str) -> tuple[str, str, str, str] | None:
        """把路由解析为 ``(route, title, module_id, item_id)``。

        设置页单独处理；模块根路径与不存在的条目都不产生标签。
        """
        workspace_route = WorkspaceRoute.parse(location)

        if workspace_route.module_id == SETTINGS_ROUTE.strip("/"):
            return SETTINGS_ROUTE, "设置", workspace_route.module_id, ""

        if not workspace_route.has_item:
            return None

        item = self._workspace.get_item(workspace_route.item_id)
        if item is None:
            return None

        return (
            workspace_route.path,
            item.name,
            workspace_route.module_id,
            workspace_route.item_id,
        )
