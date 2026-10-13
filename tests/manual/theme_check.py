"""验证响应式主题：真实点击换肤，确认配色立即全局生效。

旧实现靠 ``importlib.reload(theme)`` + 连续两次导航强制刷新；
新实现应当仅通过 ``ThemeState.notify()`` 就让所有订阅视图重渲染。
本脚本临时把窗口调高（使设置页完整可见），结束后恢复 ``config.toml``。

坐标均为**逻辑客户区**坐标（无边框窗口的客户区比窗口矩形小约 10px，
故不能用窗口矩形换算）。设置页内部坐标以「内容区原点」为基准记录，
再分别加上导航栏宽度与标题栏高度——这样调整 ``nav_width`` 时只需改一处。
"""

from __future__ import annotations

import shutil
import sys
import time

from probe_support import (
    ROOT,
    ROOT_PADDING,
    WINDOW_TITLE,
    cleanup_processes,
    client_logical_size,
    drv,
    launch,
    report_errors,
    teardown,
)

CONFIG = ROOT / "config.toml"
CONFIG_BACKUP = ROOT / ".workbuddy" / "config.backup.toml"

TALL_WIDTH = 1300
TALL_HEIGHT = 1080

NAV_WIDTH = 48
TITLE_BAR_H = 40
RAIL_PADDING_V = 10
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


# 设置页内部元素相对「内容区原点」的偏移（实测记录，已剔除根视图内边距）
_CONTENT = {
    "green_preset": (426, 742),
    "save": (69, 869),
    "back": (61, 52),
}


def _content_point(key: str) -> tuple[int, int]:
    """把内容区相对偏移换算为客户区绝对坐标。"""
    dx, dy = _CONTENT[key]
    return int(ROOT_PADDING + NAV_WIDTH + dx), int(ROOT_PADDING + TITLE_BAR_H + dy)


GREEN_PRESET = _content_point("green_preset")
"""常用颜色中第 2 个圆点（绿色 #50c878）。"""

SAVE_BUTTON = _content_point("save")
BACK_ARROW = _content_point("back")


def make_tall_config() -> None:
    """把窗口改高，使设置页全部内容可点击。"""
    CONFIG_BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CONFIG, CONFIG_BACKUP)
    text = CONFIG.read_text(encoding="utf-8")
    text = text.replace("width = 1180", f"width = {TALL_WIDTH}")
    text = text.replace("height = 720", f"height = {TALL_HEIGHT}")
    CONFIG.write_text(text, encoding="utf-8")


def restore_config() -> None:
    """还原用户配置。"""
    if CONFIG_BACKUP.exists():
        shutil.copy2(CONFIG_BACKUP, CONFIG)
        CONFIG_BACKUP.unlink()


def main() -> int:
    make_tall_config()
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
            path = drv.ROOT / f"_themecheck_{name}.png"
            drv.print_window(hwnd, path)
            print(f"  截图 -> {path.name}")

        def click(point: tuple[int, int], label: str) -> None:
            ok = drv.click_at(hwnd, *point)
            print(f"  点击 {label} @ {point} -> {'OK' if ok else 'SKIP'}")
            time.sleep(1.3)

        shot("01_before")
        click(gear_position(height), "设置齿轮")
        shot("02_settings")
        click(GREEN_PRESET, "绿色预设")
        shot("03_preset_clicked")
        click(SAVE_BUTTON, "保存")
        shot("04_saved")
        click(BACK_ARROW, "返回")
        shot("05_back_to_chat")
    finally:
        output = teardown(proc)
        exit_code = report_errors(output)
        restore_config()
        print("已恢复 config.toml")

    if exit_code:
        return exit_code

    print(
        "\n[人工核对] 03 应显示主颜色输入框变为 #50c878；\n"
        "          04 应为设置页按钮变绿；\n"
        "          05 应为列表选中态、消息气泡、发送按钮、标签指示条全部变绿。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
