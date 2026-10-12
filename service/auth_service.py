"""认证业务服务。

编排「校验凭据 -> 建立会话 -> 持久化会话」流程。
只依赖 :mod:`infra.protocols` 中的抽象接口，不感知具体存储实现。
"""

from __future__ import annotations

from infra.protocols import PasswordHasher, SessionStore, UserRepository
from models import User
from models.session import AuthSession


def _to_session(user: User, *, user_id: int) -> AuthSession:
    """把用户实体转换为会话值对象。"""
    return AuthSession(
        user_id=user_id,
        username=user.username,
        avatar_color=user.avatar_color,
    )


class AuthService:
    """登录、注册、改密与登出。

    Args:
        users: 用户仓库。
        hasher: 密码哈希器。
        sessions: 登录状态存储。
    """

    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        sessions: SessionStore,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._sessions = sessions

    def current_session(self) -> AuthSession | None:
        """返回当前登录会话；未登录时为 ``None``。"""
        return self._sessions.load()

    def login(self, username: str, password: str) -> AuthSession | None:
        """校验凭据并建立会话。

        Args:
            username: 用户名。
            password: 明文密码。

        Returns:
            登录成功时返回会话；用户名不存在或密码错误返回 ``None``。
        """
        user = self._users.find_by_username(username)
        if user is None or user.id is None:
            return None
        if not self._hasher.verify_password(password, user.password_hash):
            return None
        session = _to_session(user, user_id=user.id)
        self._sessions.save(session)
        return session

    def register(self, username: str, password: str) -> AuthSession | None:
        """注册新用户并直接登录。

        Args:
            username: 用户名。
            password: 明文密码。

        Returns:
            注册成功时返回会话；用户名已被占用返回 ``None``。
        """
        if self._users.find_by_username(username) is not None:
            return None
        user = self._users.create(username, self._hasher.hash_password(password))
        if user.id is None:
            return None
        session = _to_session(user, user_id=user.id)
        self._sessions.save(session)
        return session

    def change_password(self, old_password: str, new_password: str) -> bool:
        """修改当前登录用户的密码。

        Args:
            old_password: 旧密码。
            new_password: 新密码。

        Returns:
            修改成功返回 ``True``；未登录或旧密码错误返回 ``False``。
        """
        session = self._sessions.load()
        if session is None:
            return False
        user = self._users.get(session.user_id)
        if user is None:
            return False
        if not self._hasher.verify_password(old_password, user.password_hash):
            return False
        self._users.update_password_hash(
            session.user_id, self._hasher.hash_password(new_password)
        )
        return True

    def logout(self) -> None:
        """登出并清除持久化的会话。"""
        self._sessions.clear()
