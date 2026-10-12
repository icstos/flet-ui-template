"""基于 PBKDF2-HMAC-SHA256 的密码哈希实现。

算法与存储格式**必须与既有数据保持兼容**（``salt$hash``，salt 为 16 字节
随机值的十六进制，迭代 100000 次），否则已有账号将无法登录。
"""

from __future__ import annotations

import hashlib
import secrets

_ALGORITHM = "sha256"
_ITERATIONS = 100_000
_SALT_BYTES = 16
_SEPARATOR = "$"


class Pbkdf2PasswordHasher:
    """PBKDF2 密码哈希器。

    实现 :class:`~infra.protocols.PasswordHasher` 协议。
    """

    def hash_password(self, password: str) -> str:
        """生成 ``salt$hash`` 格式的密码哈希。

        Args:
            password: 明文密码。

        Returns:
            随机加盐后的哈希字符串。
        """
        salt = secrets.token_hex(_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            _ALGORITHM, password.encode(), salt.encode(), _ITERATIONS
        )
        return f"{salt}{_SEPARATOR}{digest.hex()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """校验密码是否与存储的哈希匹配。

        Args:
            password: 待校验的明文密码。
            stored_hash: 已存储的 ``salt$hash`` 字符串。

        Returns:
            匹配返回 ``True``；格式非法或密码错误返回 ``False``。
        """
        salt, separator, digest = stored_hash.partition(_SEPARATOR)
        if not separator:
            return False
        candidate = hashlib.pbkdf2_hmac(
            _ALGORITHM, password.encode(), salt.encode(), _ITERATIONS
        )
        return secrets.compare_digest(candidate.hex(), digest)
