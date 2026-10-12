"""真实交互测试：注入鼠标点击，验证关键交互路径。

用法：
    python tests/manual/interactive.py theme

场景：
    theme —— 进入设置页，为后续手工观察或截图留出窗口
    login —— 观察未登录时的重定向结果

坐标均为**逻辑**客户区坐标（物理像素 / DPI）。窗口内的布局是确定的：
    * 侧栏宽 ``nav_width``（默认 68），齿轮位于距底边 40px 处；
    * 标题栏高 ``title_bar_h``（默认 40）。
"""

from __future__ import annotations

import sys
import time

from probe_support import (
    WINDOW_TITLE,
    cleanup_processes,
    drv,
    launch,
    logical_size,
    report_errors,
    teardown,
)

NAV_WIDTH = 68
GEAR_BOTTOM_OFFSET = 40


def main() -> int:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "theme"
    cleanup_processes()
    time.sleep(0.5)

    exit_code = 0
    proc = launch()
    try:
        hwnd = drv.find_window_pid(WINDOW_TITLE, proc.pid, timeout=45)
        if not hwnd:
            print(f"! 未找到 {WINDOW_TITLE} 窗口")
            return 1

        time.sleep(4.5)
        width, height, dpi = logical_size(hwnd)
        print(f"窗口 hwnd={hwnd} 逻辑尺寸 {width}x{height} dpi={dpi}")

        drv.ensure_foreground(hwnd)
        time.sleep(0.6)

        def shot(name: str) -> None:
            path = drv.ROOT / f"_{scenario}_{name}.png"
            drv.print_window(hwnd, path)
            print(f"  截图 -> {path.name}")

        def click(x: int, y: int, label: str) -> None:
            ok = drv.click_at(hwnd, x, y)
            print(f"  点击 {label} @ ({x},{y}) -> {'OK' if ok else 'SKIP'}")
            time.sleep(1.4)

        shot("00_start")

        if scenario == "theme":
            click(NAV_WIDTH // 2, height - GEAR_BOTTOM_OFFSET, "设置齿轮")
            shot("01_settings")
        else:
            shot("01_state")
    finally:
        output = teardown(proc)
        exit_code = report_errors(output)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
