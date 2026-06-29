"""数据库模块。

管理 SQLite 数据库引擎、会话创建，以及数据库初始化和种子数据填充。
"""

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from config import get_config
from models import Item, Message, Module

# 数据库引擎单例
_engine = None


def get_engine():
    """获取数据库引擎实例。

    首次调用时创建引擎，并确保数据库文件所在目录存在。
    使用单例模式，全局只创建一个引擎实例。

    Returns:
        SQLAlchemy 引擎对象。
    """
    global _engine
    if _engine is None:
        url = get_config().database.url
        # 对于 SQLite，确保数据库目录存在
        if url.startswith("sqlite:///"):
            db_path = Path(url.removeprefix("sqlite:///"))
            db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(url, connect_args={"check_same_thread": False})
    return _engine


def get_session() -> Session:
    """创建新的数据库会话。

    Returns:
        新的 Session 实例。
    """
    return Session(get_engine())


def init_db() -> None:
    """初始化数据库。

    创建所有数据表，如果数据库为空则填充种子数据。
    """
    SQLModel.metadata.create_all(get_engine())
    with get_session() as session:
        # 检查是否已有模块数据，有则说明已初始化
        if session.exec(select(Module)).first():
            return
        _seed_database(session)
        session.commit()


def _seed_database(session: Session) -> None:
    """填充初始种子数据。

    包括功能模块、示例条目和聊天消息。

    Args:
        session: 数据库会话。
    """
    # ── 功能模块 ──────────────────────────────────────────
    modules = [
        Module(
            id="chat",
            label="聊天",
            icon="CHAT_BUBBLE_OUTLINE",
            icon_filled="CHAT_BUBBLE",
            sort_order=0,
        ),
        Module(
            id="contacts",
            label="通讯录",
            icon="CONTACTS_OUTLINED",
            icon_filled="CONTACTS",
            sort_order=1,
        ),
        Module(
            id="email",
            label="邮箱",
            icon="MAIL_OUTLINE",
            icon_filled="MAIL",
            sort_order=2,
        ),
    ]
    session.add_all(modules)

    # ── 示例条目 ──────────────────────────────────────────
    items = [
        # 聊天模块
        Item(
            id="zhang",
            module_id="chat",
            name="张三",
            subtitle="产品部 · 经理",
            preview="好的，明天下午三点会议室见",
            time="14:32",
            color="#4a90d9",
        ),
        Item(
            id="li",
            module_id="chat",
            name="李四",
            subtitle="研发部 · 工程师",
            preview="代码已合并到 develop 分支",
            time="11:05",
            color="#50c878",
        ),
        Item(
            id="wang",
            module_id="chat",
            name="王五",
            subtitle="设计部 · UI",
            preview="[图片] 新版首页稿已上传",
            time="昨天",
            color="#e6a23c",
        ),
        Item(
            id="group",
            module_id="chat",
            name="项目 Alpha 组",
            subtitle="8 人",
            preview="赵六: 本周迭代已排期",
            time="昨天",
            color="#9b59b6",
        ),
        # 通讯录模块
        Item(
            id="dept_rd",
            module_id="contacts",
            name="研发部",
            subtitle="24 人",
            preview="李四、王五、周八…",
            color="#3b7cff",
            detail_title="研发部",
            detail_body=(
                "部门成员 24 人\n\n"
                "· 李四 — 高级工程师\n"
                "· 王五 — 前端工程师\n"
                "· 周八 — 测试工程师\n"
                "· …"
            ),
        ),
        Item(
            id="dept_pd",
            module_id="contacts",
            name="产品部",
            subtitle="12 人",
            preview="张三、钱九…",
            color="#50c878",
            detail_title="产品部",
            detail_body=("部门成员 12 人\n\n· 张三 — 产品经理\n· 钱九 — 产品助理"),
        ),
        Item(
            id="dept_ds",
            module_id="contacts",
            name="设计部",
            subtitle="8 人",
            preview="王五、吴十…",
            color="#e6a23c",
            detail_title="设计部",
            detail_body=("部门成员 8 人\n\n· 王五 — UI 设计师\n· 吴十 — 视觉设计师"),
        ),
        # 邮箱模块
        Item(
            id="mail1",
            module_id="email",
            name="系统通知",
            subtitle="noreply@company.com",
            preview="【重要】账号安全提醒",
            time="09:12",
            color="#e74c3c",
            detail_title="【重要】账号安全提醒",
            detail_body=(
                "尊敬的用户：\n\n"
                "检测到您的账号在新设备登录。"
                "如非本人操作，请立即修改密码并联系 IT 支持。\n\n"
                "此致\n安全中心"
            ),
        ),
        Item(
            id="mail2",
            module_id="email",
            name="人力资源部",
            subtitle="hr@company.com",
            preview="2026 年度体检安排",
            time="昨天",
            color="#3b7cff",
            detail_title="2026 年度体检安排",
            detail_body=(
                "各位同事：\n\n"
                "公司年度体检定于 6 月 1 日—6 月 15 日进行，"
                "请登录 OA 预约时段。\n\n人力资源部"
            ),
        ),
        Item(
            id="mail3",
            module_id="email",
            name="行政部",
            subtitle="admin@company.com",
            preview="办公区空调检修通知",
            time="周一",
            color="#50c878",
            detail_title="办公区空调检修通知",
            detail_body=(
                "本周六 9:00—17:00 将进行中央空调检修，"
                "请提前关窗并收好个人物品。\n\n行政部"
            ),
        ),
    ]
    session.add_all(items)

    # ── 聊天消息 ──────────────────────────────────────────
    messages_data = [
        ("zhang", "them", "你好，明天的评审会还照常吗？", 0),
        ("zhang", "me", "是的，三点会议室，我稍后发议程。", 1),
        ("zhang", "them", "好的，明天下午三点会议室见", 2),
        ("li", "them", "PR #128 你看一下？", 0),
        ("li", "me", "正在看，接口部分有个小问题。", 1),
        ("li", "them", "代码已合并到 develop 分支", 2),
        ("wang", "them", "新版首页稿已上传 Figma", 0),
        ("wang", "me", "收到，下午和设计组一起过一遍。", 1),
        ("group", "them", "赵六: 本周迭代已排期", 0),
        ("group", "them", "孙七: 测试环境今晚升级", 1),
        ("group", "me", "收到，我会同步给相关同学。", 2),
    ]
    session.add_all(
        Message(item_id=iid, role=role, text=text, sort_order=order)
        for iid, role, text, order in messages_data
    )
