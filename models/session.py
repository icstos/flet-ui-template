"""登录会话值对象。

描述「当前已登录用户」这一跨层概念，供持久化层与业务层共同使用。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthSession:
    """已登录用户的会话信息。

    Attributes:
        user_id: 用户主键。
        username: 用户名。
        avatar_color: 头像底色，用于界面渲染。
    """

    user_id: int
    username: str
    avatar_color: str
