"""基础设施层。

封装底层技术实现（TOML 配置、SQLite、JSON 文件、密码哈希），并通过
:mod:`infra.protocols` 暴露抽象接口，把技术变化隔离在本层内部。
本层**不含业务逻辑**，只做「存 / 取 / 算」。
"""

from __future__ import annotations

from infra.auth_store import DEFAULT_SESSION_PATH, JsonSessionStore
from infra.config_store import DEFAULT_CONFIG_PATH, TomlSettingsStore
from infra.database import SqliteDatabase
from infra.password_hasher import Pbkdf2PasswordHasher
from infra.protocols import (
    PasswordHasher,
    SessionStore,
    SettingsStore,
    UserRepository,
    WorkspaceRepository,
)
from infra.seed import (
    DEFAULT_PASSWORD,
    DEFAULT_USERNAME,
    ensure_default_user,
    initialize_database,
    seed_catalog,
)
from infra.user_repository import SqlUserRepository
from infra.workspace_repository import SqlWorkspaceRepository

__all__ = [
    "DEFAULT_CONFIG_PATH",
    "DEFAULT_PASSWORD",
    "DEFAULT_SESSION_PATH",
    "DEFAULT_USERNAME",
    "JsonSessionStore",
    "PasswordHasher",
    "Pbkdf2PasswordHasher",
    "SessionStore",
    "SettingsStore",
    "SqlUserRepository",
    "SqlWorkspaceRepository",
    "SqliteDatabase",
    "TomlSettingsStore",
    "UserRepository",
    "WorkspaceRepository",
    "ensure_default_user",
    "initialize_database",
    "seed_catalog",
]
