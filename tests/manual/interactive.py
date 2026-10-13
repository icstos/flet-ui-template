"""真实交互测试：注入鼠标点击，验证关键交互路径。

用法：
    python tests/manual/interactive.py theme

场景：
    theme —— 进入设置页，为后续手工观察或截图留出窗口
    login —— 观察未登录时的重定向结果

坐标均为**逻辑客户区**坐标。注意：Flet 渲染的内容整体相对客户区左上角有约
10.3px 的根视图内边距（见 :data:`probe_support.ROOT_PADDING`），按布局公式
推算坐标时必须加上它，否则点击会稳定偏出约 10px。
窗口内的布局是确定的：
    * 侧栏宽 ``nav_width``（默认 54），齿轮中心横坐标
      ``ROOT_PADDING + nav_width/2``；
    * 齿轮中心纵坐标 ``客户区高 - ROOT_PADDING - (垂直内边距 + 底部内边距
      + 半个按钮高)``；
    * 标题栏高 ``title_bar_h``（默认 40）。
"""

from __future__ import annotations

import sys
import time

from probe_support import (
    ROOT_PADDING,
    WINDOW_TITLE,
    cleanup_processes,
    client_logical_size,
    drv,
    launch,
    report_errors,
    teardown,
)

NAV_WIDTH = 48
RAIL_PADDING_V = 8
BOTTOM_PADDING = 6
SETTINGS_BUTTON_SIZE = 32


def gear_position(client_height: int) -> tuple[int, int]:
    """按布局公式推算设置齿轮的可点击坐标（客户区逻辑坐标）。"""
    x = ROOT_PADDING + NAV_WIDTH / 2
    y = (
        client_height
        - ROOT_PADDING
        - (RAIL_PADDING_V + BOTTOM_PADDING + SETTINGS_BUTTON_SIZE / 2)
    )
    return int(x), int(y)


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
        width, height = client_logical_size(hwnd)
        print(f"窗口 hwnd={hwnd} 客户区逻辑尺寸 {width}x{height}")

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
            click(*gear_position(height), "设置齿轮")
            shot("01_settings")
        else:
            shot("01_state")
    finally:
        output = teardown(proc)
        exit_code = report_errors(output)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
