"""领域实体。

基于 SQLModel 定义的持久化实体。类名决定表名（``Module`` -> ``module``），
字段名与列名一一对应，**不可随意改名**，否则会与既有数据库文件失配。

这些实体同时充当跨层数据载体：视图模型与视图层直接读取其字段渲染界面，
因此字段命名保持面向业务语义。
"""

# 注意：本模块**不能**使用 `from __future__ import annotations`。
# SQLModel 需要读取真实注解对象来构建 Relationship；
# 若注解被延迟成字符串，会报
# "seems to be using a generic class as the argument to relationship()"。
from sqlmodel import Field, Relationship, SQLModel

DEFAULT_AVATAR_COLOR = "#3b7cff"
"""条目/用户的默认头像底色。"""


class Module(SQLModel, table=True):
    """功能模块（左侧导航栏入口）。

    Attributes:
        id: 模块唯一标识。
        label: 模块显示名称。
        icon: 未选中态图标名。
        icon_filled: 选中态图标名。
        sort_order: 排序序号。
    """

    id: str = Field(primary_key=True)
    label: str
    icon: str
    icon_filled: str
    sort_order: int = 0

    items: list["Item"] = Relationship(back_populates="module")


class Item(SQLModel, table=True):
    """列表条目（会话 / 联系人分组 / 邮件）。

    Attributes:
        id: 条目唯一标识。
        module_id: 所属模块 ID。
        name: 名称。
        subtitle: 副标题（职位、邮箱地址等）。
        preview: 列表预览文本。
        time: 时间显示文本。
        color: 头像底色。
        detail_title: 详情页标题。
        detail_body: 详情页正文。
        is_unread: 是否未读。
        is_pinned: 是否置顶。
        is_hidden: 是否隐藏。
    """

    id: str = Field(primary_key=True)
    module_id: str = Field(foreign_key="module.id", index=True)
    name: str
    subtitle: str = ""
    preview: str = ""
    time: str = ""
    color: str = DEFAULT_AVATAR_COLOR
    detail_title: str = ""
    detail_body: str = ""
    is_unread: bool = Field(default=False)
    is_pinned: bool = Field(default=False)
    is_hidden: bool = Field(default=False)

    module: Module | None = Relationship(back_populates="items")
    messages: list["Message"] = Relationship(
        back_populates="item", cascade_delete=True
    )


class Message(SQLModel, table=True):
    """聊天消息。

    Attributes:
        id: 自增主键。
        item_id: 所属条目 ID。
        role: 发送方角色，取值见 :class:`~models.enums.MessageRole`。
        text: 消息正文。
        sort_order: 排序序号。
    """

    id: int | None = Field(default=None, primary_key=True)
    item_id: str = Field(foreign_key="item.id", index=True)
    role: str
    text: str
    sort_order: int = 0

    item: Item | None = Relationship(back_populates="messages")


class User(SQLModel, table=True):
    """系统用户。

    Attributes:
        id: 自增主键。
        username: 用户名（唯一）。
        password_hash: 密码哈希，格式 ``salt$hash``。
        avatar_color: 头像底色。
    """

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    avatar_color: str = DEFAULT_AVATAR_COLOR
