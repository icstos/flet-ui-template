"""真实启动应用，捕获运行期异常并在数秒后自动退出。

用于验证 Flet 1.0.4 下真实的启动路径（窗口创建、字体加载、组件渲染）。
Python 侧不报错并不等于 Flutter 侧渲染成功——灰块问题请用 render_check.py。
"""

from __future__ import annotations

import sys
import time

from probe_support import (
    WINDOW_TITLE,
    cleanup_processes,
    launch,
    report_errors,
    teardown,
)

STARTUP_WAIT_SECONDS = 12


def main() -> int:
    cleanup_processes()
    time.sleep(0.5)

    proc = launch()
    still_running = False
    try:
        deadline = time.time() + STARTUP_WAIT_SECONDS
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            time.sleep(0.5)
        still_running = proc.poll() is None
    finally:
        print("\n" + "=" * 64)
        print(
            "进程状态: "
            + ("仍在运行(启动成功)" if still_running else f"已退出 code={proc.returncode}")
        )
        print("=" * 64)
        output = teardown(proc)

    print("\n----- 应用输出 -----")
    print(output.strip() or "(无输出)")

    code = report_errors(output)
    if code:
        print("\n[结论] 启动过程中出现异常")
        return code

    print(f"\n[结论] {WINDOW_TITLE} 成功启动并持续运行，无异常输出 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
