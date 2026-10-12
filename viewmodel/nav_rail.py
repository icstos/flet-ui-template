"""侧边导航栏视图模型。"""

from __future__ import annotations

from models import Module
from models.session import AuthSession
from service import AuthService, WorkspaceService
from viewmodel.base import ViewModel

FALLBACK_USERNAME = "用户"
"""未登录时展示的占位用户名。"""


class NavRailViewModel(ViewModel):
    """导航栏状态：模块列表与当前登录用户。

    Args:
        workspace: 工作区业务服务。
        auth: 认证业务服务。
    """

    def __init__(self, workspace: WorkspaceService, auth: AuthService) -> None:
        super().__init__()
        self._workspace = workspace
        self._auth = auth
        self._session: AuthSession | None = auth.current_session()

    @property
    def modules(self) -> tuple[Module, ...]:
        """全部功能模块。"""
        return self._workspace.list_modules()

    @property
    def session(self) -> AuthSession | None:
        """当前登录会话；未登录为 ``None``。"""
        return self._session

    @property
    def display_name(self) -> str:
        """用于展示的用户名。"""
        return self._session.username if self._session else FALLBACK_USERNAME

    def refresh(self) -> None:
        """重新读取登录态（登录 / 登出后调用）。"""
        session = self._auth.current_session()
        if session != self._session:
            self._session = session
            self.notify()

    @staticmethod
    def is_module_active(module_id: str, location: str) -> bool:
        """判断模块是否为当前激活项。

        Args:
            module_id: 模块 ID。
            location: 当前路由位置。

        Returns:
            路由以该模块为前缀时返回 ``True``。
        """
        return location.startswith(f"/{module_id}")
