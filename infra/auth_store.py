"""登录状态的 JSON 文件持久化。

实现 :class:`~infra.protocols.SessionStore` 协议。

路径与 JSON 结构**与既有实现保持一致**（``data/auth.json``，键为
``user_id`` / ``username`` / ``avatar_color``），以便已登录用户升级后
仍保持登录态。
"""

from __future__ import annotations

import json
from pathlib import Path

from models.session import AuthSession

DEFAULT_SESSION_PATH = Path("data/auth.json")
"""默认登录状态文件路径（相对工作目录）。"""


class JsonSessionStore:
    """把登录状态存成 JSON 文件。

    Args:
        path: 存储路径；默认 ``data/auth.json``。
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else DEFAULT_SESSION_PATH

    @property
    def path(self) -> Path:
        """当前存储路径。"""
        return self._path

    def load(self) -> AuthSession | None:
        """读取登录状态。

        Returns:
            已保存的会话；文件不存在、损坏或字段缺失时返回 ``None``（视为未登录）。
        """
        if not self._path.exists():
            return None
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return AuthSession(
                user_id=int(payload["user_id"]),
                username=str(payload["username"]),
                avatar_color=str(payload["avatar_color"]),
            )
        except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError):
            return None

    def save(self, session: AuthSession) -> None:
        """保存登录状态。"""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(
                {
                    "user_id": session.user_id,
                    "username": session.username,
                    "avatar_color": session.avatar_color,
                }
            ),
            encoding="utf-8",
        )

    def clear(self) -> None:
        """清除登录状态（文件不存在时静默返回）。"""
        self._path.unlink(missing_ok=True)
