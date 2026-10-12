"""服务（业务）层。

编排核心业务流程：认证、工作区、设置。本层**只依赖抽象接口**
（:mod:`infra.protocols` 与 :mod:`models`），不感知 TOML / SQLite / JSON
等具体技术实现，因此更换存储介质时业务代码无需改动。
"""

from __future__ import annotations

from service.auth_service import AuthService
from service.settings_service import SettingsService
from service.workspace_service import WorkspaceService

__all__ = ["AuthService", "SettingsService", "WorkspaceService"]
