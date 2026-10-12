"""SQLite 数据库连接、建表与结构迁移。

只负责「连接与结构」，不含任何业务查询——数据访问由
:mod:`infra.workspace_repository` 与 :mod:`infra.user_repository` 承担。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from models import Module

logger = logging.getLogger(__name__)

_SQLITE_PREFIX = "sqlite:///"

# 为既有 Item 表补齐后加的列。SQLite 不支持 ADD COLUMN IF NOT EXISTS，
# 重复执行会报错，因此逐条捕获忽略以实现幂等。
_ITEM_MIGRATIONS: tuple[str, ...] = (
    "ALTER TABLE item ADD COLUMN is_unread BOOLEAN DEFAULT FALSE",
    "ALTER TABLE item ADD COLUMN is_pinned BOOLEAN DEFAULT FALSE",
    "ALTER TABLE item ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE",
)


class SqliteDatabase:
    """数据库门面：持有引擎单例并提供会话。

    Args:
        url: SQLAlchemy 连接串，例如 ``sqlite:///data/cstos.db``。
    """

    def __init__(self, url: str) -> None:
        self._url = url
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        """惰性创建并返回引擎单例。

        对 SQLite 会先确保数据库文件所在目录存在。
        """
        if self._engine is None:
            if self._url.startswith(_SQLITE_PREFIX):
                db_path = Path(self._url.removeprefix(_SQLITE_PREFIX))
                db_path.parent.mkdir(parents=True, exist_ok=True)
            self._engine = create_engine(
                self._url, connect_args={"check_same_thread": False}
            )
        return self._engine

    def session(self) -> Session:
        """创建一个新的数据库会话。

        Returns:
            调用方负责关闭的 :class:`~sqlmodel.Session`（可直接用作上下文管理器）。
        """
        return Session(self.engine)

    def initialize(self, seeder: Callable[[Session], None]) -> None:
        """建表、迁移结构，并在库为空时执行种子填充。

        Args:
            seeder: 数据库为空时调用的种子填充回调。
        """
        SQLModel.metadata.create_all(self.engine)
        self._migrate_item_columns()
        with self.session() as session:
            if session.exec(select(Module)).first():
                return
            seeder(session)
            session.commit()

    def _migrate_item_columns(self) -> None:
        """为既有 Item 表补齐后加的布尔列（幂等）。

        SQLite 没有 ``ADD COLUMN IF NOT EXISTS``，列已存在时必然抛错，
        这是**预期内**的结果，因此静默忽略；用调试日志留下痕迹便于排查。
        """
        with self.engine.connect() as connection:
            for statement in _ITEM_MIGRATIONS:
                try:
                    connection.execute(text(statement))
                except Exception as error:  # noqa: BLE001
                    logger.debug("跳过已存在的列: %s (%s)", statement, error)
            connection.commit()
