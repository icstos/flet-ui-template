"""数据模型模块。

定义 SQLModel 数据库表模型，包括模块、条目和消息三个核心实体。
"""

from sqlmodel import Field, Relationship, SQLModel


class Module(SQLModel, table=True):
    """功能模块模型。

    表示左侧导航栏中的一个功能模块（聊天、通讯录、邮箱等）。

    Attributes:
        id: 模块唯一标识。
        label: 模块显示名称。
        icon: 未选中状态图标名。
        icon_filled: 选中状态图标名。
        sort_order: 排序序号。
    """

    id: str = Field(primary_key=True)
    label: str
    icon: str
    icon_filled: str
    sort_order: int = 0

    items: list["Item"] = Relationship(back_populates="module")


class Item(SQLModel, table=True):
    """条目模型。

    表示某个模块下的列表条目（聊天会话、联系人、邮件等）。

    Attributes:
        id: 条目唯一标识。
        module_id: 所属模块 ID。
        name: 条目名称。
        subtitle: 副标题（如职位、邮箱地址等）。
        preview: 预览文本。
        time: 时间显示文本。
        color: 头像背景色。
        detail_title: 详情页标题。
        detail_body: 详情页正文内容。
    """

    id: str = Field(primary_key=True)
    module_id: str = Field(foreign_key="module.id", index=True)
    name: str
    subtitle: str = ""
    preview: str = ""
    time: str = ""
    color: str = "#3b7cff"
    detail_title: str = ""
    detail_body: str = ""

    module: Module | None = Relationship(back_populates="items")
    messages: list["Message"] = Relationship(back_populates="item")


class Message(SQLModel, table=True):
    """消息模型。

    表示聊天会话中的一条消息。

    Attributes:
        id: 消息自增 ID。
        item_id: 所属条目 ID。
        role: 消息角色（"me" 己方 / "them" 对方）。
        text: 消息内容。
        sort_order: 排序序号。
    """

    id: int | None = Field(default=None, primary_key=True)
    item_id: str = Field(foreign_key="item.id", index=True)
    role: str
    text: str
    sort_order: int = 0

    item: Item | None = Relationship(back_populates="messages")
