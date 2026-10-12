"""领域枚举。

集中定义具有固定取值集合的领域概念，避免散落的字符串字面量。
所有枚举均继承 :class:`~enum.StrEnum`，因此可直接与数据库中的字符串
互操作，也可直接参与 ``==`` 比较与格式化。
"""

from __future__ import annotations

from enum import StrEnum


class ModuleId(StrEnum):
    """内置功能模块标识。

    取值与数据库 ``module.id`` 一致；模块列表本身仍由数据驱动，
    此处仅固定三个内置模块，供种子数据与默认路由使用。
    """

    CHAT = "chat"
    CONTACTS = "contacts"
    EMAIL = "email"


class MessageRole(StrEnum):
    """聊天消息的发送方角色。"""

    ME = "me"
    """己方发送，界面右对齐。"""

    THEM = "them"
    """对方发送，界面左对齐。"""
