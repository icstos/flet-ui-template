"""基础设施层对外暴露的抽象接口。

业务层（service）**只依赖本模块中的 Protocol**，不感知 TOML、SQLite、
JSON 或任何具体技术实现；具体实现位于同包的各个 ``*_store`` / ``*_repository``
模块中，由组合根负责装配。这样替换存储介质（例如改用 PostgreSQL 或云端
配置中心）时，业务代码无需改动。
"""

from __future__ import annotations

from typing import Protocol

from models import AppSettings, Item, Message, Module, User
from models.session import AuthSession


class SettingsStore(Protocol):
    """应用配置的持久化接口。"""

    def load(self) -> AppSettings:
        """读取配置；文件缺失或损坏时返回默认配置。"""
        ...

    def save(self, settings: AppSettings) -> None:
        """把配置写入持久化介质。"""
        ...

    def reload(self) -> AppSettings:
        """丢弃缓存，强制从持久化介质重新读取。"""
        ...


class PasswordHasher(Protocol):
    """密码哈希接口。"""

    def hash_password(self, password: str) -> str:
        """生成不可逆的密码哈希。"""
        ...

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """校验明文密码与已存哈希是否匹配。"""
        ...


class SessionStore(Protocol):
    """登录状态持久化接口。"""

    def load(self) -> AuthSession | None:
        """读取已保存的登录状态；不存在或损坏时返回 ``None``。"""
        ...

    def save(self, session: AuthSession) -> None:
        """保存登录状态。"""
        ...

    def clear(self) -> None:
        """清除登录状态。"""
        ...


class WorkspaceRepository(Protocol):
    """工作区数据（模块 / 条目 / 消息）访问接口。"""

    def list_modules(self) -> tuple[Module, ...]:
        """按排序返回全部功能模块。"""
        ...

    def list_items(self, module_id: str) -> list[Item]:
        """返回模块下未隐藏的条目，置顶优先。"""
        ...

    def get_item(self, item_id: str) -> Item | None:
        """按 ID 取单个条目。"""
        ...

    def list_messages(self, item_id: str) -> list[Message]:
        """按顺序返回条目的全部消息。"""
        ...

    def add_message(self, item_id: str, role: str, text: str) -> Message:
        """追加一条消息并返回它。"""
        ...

    def update_item(self, item_id: str, **changes: object) -> Item | None:
        """更新条目字段并返回更新后的条目。"""
        ...

    def search_items(self, query: str) -> list[Item]:
        """跨模块搜索条目；查询为空时返回全部。"""
        ...

    def delete_item(self, item_id: str) -> bool:
        """删除条目，返回是否删除成功。"""
        ...


class UserRepository(Protocol):
    """用户账号访问接口。"""

    def find_by_username(self, username: str) -> User | None:
        """按用户名查找用户。"""
        ...

    def get(self, user_id: int) -> User | None:
        """按主键查找用户。"""
        ...

    def create(self, username: str, password_hash: str) -> User:
        """创建用户并返回它。"""
        ...

    def update_password_hash(self, user_id: int, password_hash: str) -> None:
        """更新指定用户的密码哈希。"""
        ...
