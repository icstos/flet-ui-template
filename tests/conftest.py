"""pytest 公共装置：把项目根加入导入路径，并提供隔离的容器。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """构建一个指向临时目录的容器，避免污染用户数据。

    通过写入最小配置文件把数据库指向临时 SQLite 文件；
    其余配置节留空即使用默认值。
    """
    monkeypatch.chdir(tmp_path)
    db_path = tmp_path / "test.db"
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        f'[database]\nurl = "sqlite:///{db_path.as_posix()}"\n', encoding="utf-8"
    )

    from container import build_container

    return build_container(
        config_path=config_path,
        session_path=tmp_path / "auth.json",
    )
