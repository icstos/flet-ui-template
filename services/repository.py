"""数据访问层模块。

封装所有数据库查询操作，提供模块、条目、消息的 CRUD 接口。
使用 SQLModel 进行数据库操作。
"""

from functools import lru_cache

from sqlmodel import select

from database import get_session
from models import Item, Message, Module


@lru_cache(maxsize=1)
def get_modules() -> tuple[Module, ...]:
    """获取所有功能模块列表。

    结果会被缓存，首次查询后后续调用直接返回缓存结果。

    Returns:
        按排序顺序排列的模块元组。
    """
    with get_session() as session:
        return tuple(session.exec(select(Module).order_by(Module.sort_order)).all())


def get_items(module_id: str) -> list[Item]:
    """获取指定模块下的所有未隐藏条目。

    Args:
        module_id: 模块 ID。

    Returns:
        条目列表，置顶条目优先，其余按 ID 排序。
    """
    with get_session() as session:
        return list(
            session.exec(
                select(Item)
                .where(Item.module_id == module_id)
                .where(Item.is_hidden == False)
                .order_by(Item.is_pinned.desc(), Item.id)
            ).all()
        )


def get_item(item_id: str) -> Item | None:
    """根据 ID 获取单个条目。

    Args:
        item_id: 条目 ID。

    Returns:
        条目对象，不存在时返回 None。
    """
    with get_session() as session:
        return session.get(Item, item_id)


def get_messages(item_id: str) -> list[Message]:
    """获取指定条目的所有消息。

    Args:
        item_id: 条目 ID。

    Returns:
        消息列表，按排序顺序排列。
    """
    with get_session() as session:
        return list(
            session.exec(
                select(Message)
                .where(Message.item_id == item_id)
                .order_by(Message.sort_order)
            ).all()
        )


def add_message(item_id: str, role: str, text: str) -> Message:
    """添加一条新消息。

    自动计算新消息的排序序号（在现有最后一条之后。

    Args:
        item_id: 所属条目 ID。
        role: 消息角色（"me" 或 "them"）。
        text: 消息内容。

    Returns:
        新创建的消息对象。
    """
    with get_session() as session:
        # 查询最后一条消息的序号
        last_msg = session.exec(
            select(Message)
            .where(Message.item_id == item_id)
            .order_by(Message.sort_order.desc())
        ).first()
        next_order = (last_msg.sort_order + 1) if last_msg else 0

        msg = Message(item_id=item_id, role=role, text=text, sort_order=next_order)
        session.add(msg)
        session.commit()
        session.refresh(msg)
        return msg


def get_default_item_id(module_id: str) -> str:
    """获取指定模块的默认条目 ID。

    Args:
        module_id: 模块 ID。

    Returns:
        第一个条目的 ID，模块下无条目时返回空字符串。
    """
    items = get_items(module_id)
    return items[0].id if items else ""


def update_item(item_id: str, **kwargs) -> Item | None:
    """更新条目的指定字段。

    Args:
        item_id: 条目 ID。
        **kwargs: 要更新的字段名和值。

    Returns:
        更新后的条目对象，不存在时返回 None。
    """
    with get_session() as session:
        item = session.get(Item, item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        session.commit()
        session.refresh(item)
        return item


def delete_item(item_id: str) -> bool:
    """删除指定条目。

    Args:
        item_id: 条目 ID。

    Returns:
        删除成功返回 True，失败返回 False。
    """
    with get_session() as session:
        item = session.get(Item, item_id)
        if not item:
            return False
        session.delete(item)
        session.commit()
        return True
