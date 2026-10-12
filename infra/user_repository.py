"""用户账号的 SQLModel 实现。

实现 :class:`~infra.protocols.UserRepository` 协议。这里只做数据存取，
「用户名唯一」「密码是否正确」等判定属于业务层。
"""

from __future__ import annotations

from sqlmodel import select

from infra.database import SqliteDatabase
from models import User


class SqlUserRepository:
    """基于 SQLModel 的用户仓库。

    Args:
        database: 数据库门面。
    """

    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def find_by_username(self, username: str) -> User | None:
        """按用户名查找用户。"""
        with self._database.session() as session:
            return session.exec(
                select(User).where(User.username == username)
            ).first()

    def get(self, user_id: int) -> User | None:
        """按主键查找用户。"""
        with self._database.session() as session:
            return session.get(User, user_id)

    def create(self, username: str, password_hash: str) -> User:
        """创建用户。"""
        with self._database.session() as session:
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update_password_hash(self, user_id: int, password_hash: str) -> None:
        """更新指定用户的密码哈希。"""
        with self._database.session() as session:
            user = session.get(User, user_id)
            if user is None:
                return
            user.password_hash = password_hash
            session.commit()
