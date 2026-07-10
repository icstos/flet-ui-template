"""登录状态本地持久化存储模块。

使用 JSON 文件存储用户登录信息，应用重启后仍保持登录状态。
"""

import json
from pathlib import Path

_AUTH_FILE = Path("data/auth.json")


def save_auth(user_id: int, username: str, avatar_color: str) -> None:
    """保存登录信息到本地文件。

    Args:
        user_id: 用户 ID。
        username: 用户名。
        avatar_color: 头像背景色。
    """
    _AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    _AUTH_FILE.write_text(
        json.dumps(
            {
                "user_id": user_id,
                "username": username,
                "avatar_color": avatar_color,
            }
        ),
        encoding="utf-8",
    )


def load_auth() -> dict | None:
    """从本地文件加载登录信息。

    Returns:
        包含 user_id、username、avatar_color 的字典，无文件时返回 None。
    """
    if not _AUTH_FILE.exists():
        return None
    try:
        return json.loads(_AUTH_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def clear_auth() -> None:
    """清除登录信息。"""
    if _AUTH_FILE.exists():
        _AUTH_FILE.unlink()
