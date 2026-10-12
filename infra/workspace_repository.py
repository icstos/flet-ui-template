"""工作区数据（模块 / 条目 / 消息）的 SQLModel 实现。

实现 :class:`~infra.protocols.WorkspaceRepository` 协议。查询语义与既有实现
逐条对齐（排序、过滤、级联行为均不变），仅做职责归位。
"""

from __future__ import annotations

from sqlmodel import select

from infra.database import SqliteDatabase
from models import Item, Message, Module


class SqlWorkspaceRepository:
    """基于 SQLModel 的工作区仓库。

    Args:
        database: 数据库门面。
    """

    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database
        self._modules: tuple[Module, ...] | None = None

    def list_modules(self) -> tuple[Module, ...]:
        """按 ``sort_order`` 返回全部模块。

        结果在实例内缓存：模块是几乎不变的字典数据，避免每次渲染都查库。
        """
        if self._modules is None:
            with self._database.session() as session:
                self._modules = tuple(
                    session.exec(select(Module).order_by(Module.sort_order)).all()
                )
        return self._modules

    def list_items(self, module_id: str) -> list[Item]:
        """返回模块下未隐藏的条目，置顶优先、其次按 ID。"""
        with self._database.session() as session:
            return list(
                session.exec(
                    select(Item)
                    .where(Item.module_id == module_id)
                    .where(Item.is_hidden == False)
                    .order_by(Item.is_pinned.desc(), Item.id)
                ).all()
            )

    def get_item(self, item_id: str) -> Item | None:
        """按 ID 取条目。"""
        with self._database.session() as session:
            return session.get(Item, item_id)

    def list_messages(self, item_id: str) -> list[Message]:
        """按 ``sort_order`` 返回条目消息。"""
        with self._database.session() as session:
            return list(
                session.exec(
                    select(Message)
                    .where(Message.item_id == item_id)
                    .order_by(Message.sort_order)
                ).all()
            )

    def add_message(self, item_id: str, role: str, text: str) -> Message:
        """追加消息，序号接在现有最后一条之后。"""
        with self._database.session() as session:
            last = session.exec(
                select(Message)
                .where(Message.item_id == item_id)
                .order_by(Message.sort_order.desc())
            ).first()
            message = Message(
                item_id=item_id,
                role=role,
                text=text,
                sort_order=(last.sort_order + 1) if last else 0,
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    def update_item(self, item_id: str, **changes: object) -> Item | None:
        """更新条目字段；未知字段被忽略。"""
        with self._database.session() as session:
            item = session.get(Item, item_id)
            if item is None:
                return None
            for key, value in changes.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            session.commit()
            session.refresh(item)
            return item

    def search_items(self, query: str) -> list[Item]:
        """跨模块搜索；查询为空时返回全部未隐藏条目。"""
        with self._database.session() as session:
            statement = select(Item).where(Item.is_hidden == False)
            keyword = query.strip()
            if keyword:
                statement = statement.where(
                    Item.name.contains(keyword) | Item.preview.contains(keyword)
                )
            statement = statement.order_by(Item.is_pinned.desc(), Item.name)
            return list(session.exec(statement).all())

    def delete_item(self, item_id: str) -> bool:
        """删除条目，返回是否删除成功。"""
        with self._database.session() as session:
            item = session.get(Item, item_id)
            if item is None:
                return False
            session.delete(item)
            session.commit()
            return True
